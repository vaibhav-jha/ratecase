import asyncio
from functools import partial
import langsmith_config

from langchain.prompts import PromptTemplate
from langchain.document_loaders import PyPDFLoader
from langchain.schema import format_document, StrOutputParser
from langchain.schema import Document

from utils import get_or_create_eventloop
from watsonx_model import get_summary_llm, llm_ibm
from prompts import summary_prompt, reduce_prompt, collapse_prompt, comparison_prompt_template, ans_prompt_template, \
    final_ans_prompt_template, basic_qa_prompt

from langchain.chains.combine_documents import collapse_docs, split_list_of_docs
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough

from vector_store import get_retriever

from operator import itemgetter
from langchain.schema.runnable import RunnableMap

# from GPT_Model import llm

langsmith_config.set_env()


# --------------------------SUMMARY GENERATION-------------------------------------

def _build_documents_legacy(filename, llm, token_threshold=2000):
    loader = PyPDFLoader(f"./temp/user_uploaded/{filename}")
    pages = loader.load()

    document = ""
    documents = []

    prev_pno = 0
    pno = len(pages)

    if len(pages) > 50:
        pages = pages[:50]

    for page in pages[:20]:
        pno = page.metadata['page']
        content = page.page_content
        document += f"""Page {pno + 1}:
{content}


        """
        if llm_ibm.get_num_tokens(document) > token_threshold:
            documents.append(Document(page_content=document, metadata={"pages": f"{prev_pno + 1}-{pno + 1}"}))
            document = ""
            prev_pno = pno + 1

    documents.append(Document(page_content=document, metadata={"pages": f"{prev_pno + 1}-{pno + 1}"}))

    return documents


def _build_documents(filename, llm, token_threshold=2000, legacy=True):
    if legacy:
        return _build_documents_legacy(filename, llm, token_threshold)

    return _build_documents_legacy(filename, llm, token_threshold)
    # loader = PyPDFLoader(f"./temp/user_uploaded/{filename}")
    # pages = loader.load()


def _get_summary_llm(model: str, creative: float):
    if model.startswith("llama"):
        return get_summary_llm(creative)
    else:
        from llms import CustomLLM
        llm_obj = CustomLLM()
        return llm_obj.get_llm(option=model, temperature=creative)


def summarize(filename, detail=500, creative=0.35, model='gpt4'):
    summary_llm = _get_summary_llm("claude3", creative)

    documents = _build_documents(filename, summary_llm, token_threshold=150000)
    print(f"Document length {len(documents)}")
    document_prompt = PromptTemplate.from_template("{page_content}")
    partial_format_document = partial(format_document, prompt=document_prompt)
    partial_format_wc = partial(format_document, prompt=PromptTemplate.from_template(f"{detail}"))

    # The chain we'll apply to each individual document.
    # Returns a summary of the document.
    map_chain = (
            {"document_content": partial_format_document, "word_count": partial_format_wc}
            | PromptTemplate.from_template(summary_prompt)
            | summary_llm
            | StrOutputParser()
    )

    # A wrapper chain to keep the original Document metadata
    map_as_doc_chain = (
            RunnableParallel({"doc": RunnablePassthrough(), "content": map_chain})
            | (lambda x: Document(page_content=x["content"], metadata=x["doc"].metadata))
    ).with_config(run_name="Summarize (return doc)")

    # The chain we'll repeatedly apply to collapse subsets of the documents
    # into a consolidate document until the total token size of our
    # documents is below some max size.
    def format_docs(docs):
        doc_prompt = PromptTemplate.from_template("Summary for pages {pages}:\n{page_content}")
        partial_format_doc = partial(format_document, prompt=doc_prompt)
        return "\n\n".join(partial_format_doc(doc) for doc in docs)

    collapse_chain = (
            {"context": format_docs}
            | PromptTemplate.from_template(collapse_prompt, partial_variables={"word_count": str(detail)})
            | summary_llm
            | StrOutputParser()
    )

    def get_num_tokens(docs):
        return summary_llm.get_num_tokens(format_docs(docs))

    def collapse(
            docs,
            config,
            token_max=3500,
    ):
        print("I came here")
        collapse_ct = 1
        while get_num_tokens(docs) > token_max:
            config["run_name"] = f"Collapse {collapse_ct}"
            invoke = partial(collapse_chain.invoke, config=config)
            split_docs = split_list_of_docs(docs, get_num_tokens, token_max)
            docs = [collapse_docs(_docs, invoke) for _docs in split_docs]
            collapse_ct += 1
        return docs

    reduce_chain = (
            {"context": format_docs}
            | PromptTemplate.from_template(reduce_prompt, partial_variables={"word_count": str(detail)})
            | summary_llm
            | StrOutputParser()
    ).with_config(run_name="Reduce")

    # print(map_as_doc_chain.map())
    # The final full chain
    map_reduce = (map_as_doc_chain.map() | collapse | reduce_chain).with_config(
        run_name="Map reduce"
    )

    return map_reduce.invoke(documents, config={"max_concurrency": 10})

    # return chain.invoke({'word_count': detail, 'document_content': document_content})


# --------------------------COMPARE SUMMARIES--------------------------------------------
def compare_summaries(summaries):
    summary_doc = ""
    for key in summaries:
        filename = key
        file_summary = summaries[key]
        summary_doc += f"Summary for {filename}:\n{file_summary.strip()}\n\n"

    comp_prompt = PromptTemplate.from_template(comparison_prompt_template, partial_variables={"summaries": summary_doc})
    chain = comp_prompt | llm

    return chain.invoke({})


# --------------------------QUESTION TO VECTOR STORE-------------------------------------


def answer_legacy(question, llm, files):
    def format_retrieved_docs(docs):
        doc_prompt = PromptTemplate.from_template("Source: (filename: {citation}, pages: {page})\nText:{page_content}")
        partial_format_doc = partial(format_document, prompt=doc_prompt)
        return "\n\n".join(partial_format_doc(doc) for doc in docs)

    async def prompt_llm(chain, question):
        return await chain.ainvoke(question)

    loop = get_or_create_eventloop()  # For async

    answers = []
    for file in files:
        filename = file.name
        retriever = get_retriever(filename)

        # ans_chain = (
        #         {"context": retriever | format_retrieved_docs, "question": RunnablePassthrough()}
        #         | PromptTemplate.from_template(ans_prompt_template)
        #         | llm
        #         | StrOutputParser()
        # )

        rag_chain_from_docs = (
                {
                    "context": lambda x: format_retrieved_docs(x["documents"]),
                    "question": itemgetter("question"),
                }
                | PromptTemplate.from_template(ans_prompt_template)
                | llm
                | StrOutputParser()
        )
        rag_chain_with_source = RunnableMap(
            {"documents": retriever, "question": RunnablePassthrough()}
        ) | {
                                    "documents": lambda x: [
                                        {k: v for k, v in doc.metadata.items() if k in ['citation', 'page']} for doc in
                                        x["documents"]],
                                    "answer": rag_chain_from_docs,
                                }

        answers.append(prompt_llm(rag_chain_with_source, question))

    answers = loop.run_until_complete(asyncio.gather(*answers))
    loop.close()

    metadatas = [x['documents'] for x in answers]
    answers_text = [x['answer'] for x in answers]

    ans_docs = []
    for i, ans in enumerate(answers):
        print(f'{ans=}')
        ans_docs.append(Document(page_content=ans['answer'],
                                 metadata={"citation": ', '.join([y["citation"] for y in ans["documents"]]),
                                           "pages": ', '.join([y["page"] for y in ans["documents"]]),
                                           "doc_num": i}))

    def format_answer_docs(docs):
        template = "Document {doc_num} (filename: {citation}, pages: {pages}):\n{page_content}"
        doc_prompt = PromptTemplate.from_template(template)
        partial_format_doc = partial(format_document, prompt=doc_prompt)
        return "\n\n\n".join(partial_format_doc(doc) for doc in docs)

    final_ans_prompt = PromptTemplate.from_template(final_ans_prompt_template)
    formatted_answer_docs = format_answer_docs(ans_docs)

    final_ans_chain = (
            {"answers": lambda x: formatted_answer_docs, "question": RunnablePassthrough()}
            | PromptTemplate.from_template(final_ans_prompt_template)
            | llm_ibm
            | StrOutputParser()
    )

    final_answer = final_ans_chain.invoke(question)

    return final_answer, metadatas


def _choose_model(model='claude3'):
    if model.startswith("llama"):
        return llm_ibm
    else:
        from llms import CustomLLM
        llm_obj = CustomLLM()
        return llm_obj.get_llm(option=model)


def answer(question, files, legacy=False, model='claude3'):
    llm = _choose_model(model)

    if legacy:
        return answer_legacy(question, llm, files)

    # load all content into context
    def format_retrieved_docs(docs):
        doc_prompt = PromptTemplate.from_template("Source: (filename: {citation}, pages: {page})\nText:{page_content}")
        partial_format_doc = partial(format_document, prompt=doc_prompt)
        return "\n\n".join(partial_format_doc(doc) for doc in docs)

    context = ""

    for file in files:
        filename = file.name
        filepath = f"./temp/user_uploaded/{filename}"

        print(f"{filepath=}")

        from langchain.document_loaders import PDFPlumberLoader

        loader = PDFPlumberLoader(filepath)

        context += f"Document Name: {filename}\n"
        for page in loader.load():
            context += f"Page: {page.metadata['page']}\n"
            context += f"Content: \n{page.page_content}\n\n"

    prompt = PromptTemplate.from_template(basic_qa_prompt)
    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"context": context, "question": question}), None


def answer_all(question, files):
    pass
