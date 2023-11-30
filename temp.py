

# from langchain.chat_models import ChatOpenAI

#
# llm = ChatOpenAI()
# llm.invoke("Hello, world!")



import os
from dotenv import load_dotenv

from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams
from genai.credentials import Credentials

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint=api_url)

print("\n------------- Example (LangChain)-------------\n")

params = GenerateParams(decoding_method="greedy", max_new_tokens= 500, repetition_penalty=1.12)

print("Using GenAI Model expressed as LangChain Model via LangChainInterface:")

llm = LangChainInterface(model="meta-llama/llama-2-70b-chat", params=params, credentials=creds)
print(llm("What is ChatGPT?"))