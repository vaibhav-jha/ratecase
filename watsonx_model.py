import os
from dotenv import load_dotenv

from genai.extensions.langchain import LangChainInterface
from genai.schema import TextGenerationParameters

from genai import Client, Credentials

load_dotenv()
# api_key = os.getenv("GENAI_KEY", None)
# api_url = os.getenv("GENAI_API", None)
# creds = Credentials(api_key, api_endpoint=api_url)

client = Client(credentials=Credentials.from_env())

params = TextGenerationParameters(
    decoding_method="greedy",
    min_new_tokens=1,
    max_new_tokens=1200,
    repetition_penalty=1.2
)

llm_ibm = LangChainInterface(model_id="meta-llama/llama-2-70b-chat", parameters=params, client=client)


def get_summary_llm(creative=0.35):
    summary_params = TextGenerationParameters(
        decoding_method="sample",
        min_new_tokens=1,
        max_new_tokens=1200,
        repetition_penalty=1.2,
        temperature=creative,
    )
    summary_llm = LangChainInterface(model_id="meta-llama/llama-2-70b-chat", parameters=params, client=client)

    return summary_llm
