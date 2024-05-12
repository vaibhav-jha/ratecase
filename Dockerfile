FROM python:3.10.14-slim
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY . .
ENV LANGCHAIN_TRACING_V2=true
ENV LANGCHAIN_PROJECT=ratecase_2024_mash
EXPOSE 8501
CMD ["python3", "streamlit run ui.py"]
