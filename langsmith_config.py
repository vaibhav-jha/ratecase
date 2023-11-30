import os


def set_env():
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
    os.environ['LANGCHAIN_API_KEY'] = "ls__6f792b52f87043e8ab903f2793d4f2df"
    os.environ['LANGCHAIN_PROJECT'] = "centerpoint"
