FROM python:3.10.13-slim-bookworm
RUN pip install poetry
COPY . /app/
WORKDIR /app/
RUN poetry config virtualenvs.create false
RUN poetry install
ENV BOT_TOKEN=6659670636:AAFPGljPDglDRV2pI2wCI3Zg1YxLMxyMmEM
CMD ["python", "magic/main.py"]