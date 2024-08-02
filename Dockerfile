FROM python:3.9-slim-bookworm

WORKDIR /file_uploader
COPY src .
COPY main.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]