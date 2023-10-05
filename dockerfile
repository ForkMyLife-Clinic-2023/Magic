FROM python:3.10.13-slim-bookworm
RUN pip install poetry
COPY pyproject.toml /app/
COPY README.md /app/
COPY magic /app/magic/
COPY tests /app/tests/
WORKDIR /app/
RUN poetry config virtualenvs.create false
RUN poetry install
CMD ["uvicorn", "magic.main:app", "--host", "0.0.0.0", "--port", "80"]