import os
from dotenv import load_dotenv

from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams
from genai.credentials import Credentials

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint=api_url)

params = GenerateParams(
    decoding_method="greedy",
    min_new_tokens=1,
    max_new_tokens=1200,
    repetition_penalty=1.2
)

llm = LangChainInterface(model="meta-llama/llama-2-70b-chat", params=params, credentials=creds)


def get_summary_llm(creative=0.35):
    summary_params = GenerateParams(
        decoding_method="sample",
        min_new_tokens=1,
        max_new_tokens=1200,
        repetition_penalty=1.2,
        temperature=creative,
    )
    summary_llm = LangChainInterface(model="meta-llama/llama-2-70b-chat", params=summary_params, credentials=creds)

    return summary_llm
