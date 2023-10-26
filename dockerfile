FROM python:3.10.13-slim-bookworm
ENV BOT_TOKEN = 0
RUN pip install poetry
COPY . /app/
WORKDIR /app/
RUN poetry config virtualenvs.create false
RUN poetry install