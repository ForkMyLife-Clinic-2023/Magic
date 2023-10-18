FROM python:3.10.13-slim-bookworm
RUN pip install poetry
COPY . /app/
WORKDIR /app/
RUN poetry config virtualenvs.create false
RUN poetry install
CMD ["python", "magic/main.py"]