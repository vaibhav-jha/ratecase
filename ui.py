import asyncio

import streamlit as st

from brain import summarize, answer, compare_summaries
from parser import parse_pdf
from utils import process_files, store_temp
from vector_store import store_document
import time
from ui_helper import inject_bootstrap, display_summary

# -----------------------------------------------------------
# APP Config
st.set_page_config(layout="wide")

# -----------------------------------------------------------
# Custom CSS
# inject_bootstrap()
# with open('./style/custom.css') as f:
#     css = f.read()
# st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# -----------------------------------------------------------
# Title
st.title("Talk to Documents", anchor="title")
st.divider()
# -----------------------------------------------------------
# SIDEBAR
with st.sidebar:
    model_to_use = st.radio(horizontal=True, label='Select Model',
                            options={'llama-2-70b-chat': 'llama', 'gpt-3.5': 'gpt'})
    st.divider()
    summary_detail = st.slider(label='Summary level of detail', value=800, min_value=100, max_value=1600, step=100)
    st.divider()
    summary_creativity = st.slider(label='Summary Creativity', value=5, min_value=0, max_value=100, step=5)
    summary_creativity = summary_creativity * 1.0 / 50 if summary_creativity > 0 else 0.05


# -----------------------------------------------------------

def write_summary(filename, file_summary):
    with st.expander(f"Summary for {filename}"):
        st.write(file_summary)


# -----------------------------------------------------------
# BODY
files = st.file_uploader(label='Upload Files', accept_multiple_files=True)

if "summaries" not in st.session_state:
    st.session_state["summaries"] = {}

st.session_state["summary_written"] = False

if "file_analyses" not in st.session_state:
    st.session_state.file_analyses = []

if files:
    st.info(f'Files uploaded: {len(files)}')

    # Remove Summaries for files that do not exist anymore
    filenames = [file.name for file in files]
    summary_keys = st.session_state.summaries.keys()
    to_remove = set(summary_keys).difference(set(filenames))
    st.session_state["summaries"] = {key: value for key, value in st.session_state["summaries"].items() if
                                     key not in to_remove}

    # Check if files have changed
    if "files" not in st.session_state or st.session_state.files != files:
        st.session_state.files = files

        with st.spinner("Storing Files on Disk.."):
            store_temp(files)

        # loop = get_or_create_eventloop() # For async
        # -----------------------
        # for file in files:
        #     with st.spinner(f'Analyzing {file.name}...'):
        #         store_document(file.name)
        #         summary = summarize(file.name, detail=summary_detail, creative=summary_creativity)
        #         summary = summary.replace("$", "\\$")
        #         st.session_state["summaries"][file.name] = summary
        #     write_summary(file.name, summary)
        #
        # st.session_state["summary_written"] = True
        # ------------------------
        # with st.spinner(f"Analyzing {len(files)} documents.."):
        #     loop.run_until_complete(asyncio.gather(*st.session_state["summaries"]))
        #     loop.close()

        # if len(files) > 1:
        #     with st.spinner('Comparing Documents...'):
        #         comparison = compare_summaries(st.session_state["summaries"])
        #         # comparison = comparison.replace('-', '\\-')
        #     with st.expander(f"Comparison"):
        #         st.write(comparison)

    # if not st.session_state.summary_written:
    #     for file in files:
    #         label = file.name
    #         write_summary(label, st.session_state.summaries[file.name])

    for text in st.session_state.file_analyses:
        st.markdown(text)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"].replace("$", "\\$"))

    # React to user input
    if prompt := st.chat_input("Ask anything.."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        agent_response, sources = answer(prompt, files)
        agent_response = agent_response.replace("$", "\\$")

        st.write(agent_response)

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "ai", "content": agent_response})
