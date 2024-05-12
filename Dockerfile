FROM python:3.11-alpine
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY . .
ENV LANGCHAIN_TRACING_V2=true
ENV LANGCHAIN_PROJECT=ratecase_2024_mash
EXPOSE 5000
CMD ["python3", "streamlit run ui.py"]
