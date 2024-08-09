FROM python:3.9-slim-bookworm

WORKDIR /file_uploader
COPY src .
COPY pyproject.toml .
COPY poetry.lock .

RUN pip install --upgrade poetry
RUN poetry config virtualenvs.create false && poetry install -v --all-extras

ENTRYPOINT [ "python", "-m", "file_uploader" ]
CMD [ ]
