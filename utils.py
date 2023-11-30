import asyncio

from parser import parse_pdf


# def hash(files):
#     import hashlib
#
#     key = f'{doc.metadata["dockey"]}/{doc.metadata["citation"]}'
#     val = doc.page_content
#
#     hashed_key = hashlib.sha256(key.encode('UTF-8')).hexdigest()
#     hashed_val = hashlib.sha256(val.encode('UTF-8')).hexdigest()
#
#     ids = f'{hashed_key}_{hashed_val}'
#
#     return ids


def process_files(files):
    splits, metadatas = parse_pdf(files[0], citation=files[0].name, key=files[0].name)


def store_temp(files):
    for file in files:
        with open(f'./temp/user_uploaded/{file.name}', 'wb') as f:
            data = file.getbuffer()
            f.write(data)


def get_or_create_eventloop():
    try:
        loop = asyncio.get_event_loop()
        loop.close()
        return loop
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()
