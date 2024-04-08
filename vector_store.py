import os
from typing import List

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document


def _read_file(filename, doc_type='pdf'):
    from langchain.document_loaders import PDFPlumberLoader
    loader = PDFPlumberLoader(f'./temp/user_uploaded/{filename}')
    return loader.load()


def _get_token_count(page_content):
    from llms import CustomLLM

    llm = CustomLLM().get_llm(option='gpt3')
    return llm.get_num_tokens((page_content))


def _split_doc(doc: List[Document], chunk_chars=1500, overlap=100):
    import unidecode

    pdf_contents = [(i.page_content, i.metadata) for i in doc]

    citation = os.path.basename(pdf_contents[0][1]['file_path'])
    key = os.path.dirname(pdf_contents[0][1]['file_path']).split(os.sep)[-1]

    splits = []
    split = ""
    pages = []
    metadatas = []
    documents = []
    metadata = {}

    for i, content in enumerate(pdf_contents):

        page = content[0]
        metadata = content[1]

        split += unidecode.unidecode(page)
        pages.append(str(i + 1))
        # split could be so long it needs to be split
        # into multiple chunks. Or it could be so short
        # that it needs to be combined with the next chunk.
        while len(split) > chunk_chars:
            splits.append(split[:chunk_chars])
            # pretty formatting of pages (e.g. 1-3, 4, 5-7)
            pg = "-".join([pages[0], pages[-1]])

            num_tokens = _get_token_count(split[:chunk_chars])

            metadata.update(dict(
                citation=citation,
                dockey=key,
                page=f"{citation} pages {pg}",
                num_tokens=num_tokens,
            ))
            metadatas.append(metadata)

            documents.append(Document(page_content=split[:chunk_chars], metadata=metadata))

            split = split[chunk_chars - overlap:]
            pages = [str(i + 1)]
    if len(split) > overlap:
        splits.append(split[:chunk_chars])
        pg = "-".join([pages[0], pages[-1]])
        metadata.update(dict(
            citation=citation,
            dockey=key,
            page=f"{citation} pages {pg}",
        ))
        metadatas.append(metadata)
        documents.append(Document(page_content=split[:chunk_chars], metadata=metadata))

    return documents


def store_document(filename):
    collection_name = filename
    try:
        vs = FAISS.load_local(f"./temp/faiss_index/{collection_name}", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        print("Loaded from local")
    except RuntimeError:
        print("Loading from docs")
        doc = _read_file(filename)
        doc_split = _split_doc(doc)
        vs = FAISS.from_documents(doc_split, OpenAIEmbeddings())
        vs.save_local(f"./temp/faiss_index/{collection_name}")
    return vs


def get_retriever(filename):
    vs = store_document(filename)
    return vs.as_retriever(lambda_mult=0.6, k=10)



