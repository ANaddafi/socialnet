FROM python:3.12-slim-bullseye as builder

WORKDIR /app

RUN pip install --no-cache-dir requests

COPY combine_words.py .
RUN python combine_words.py

FROM python:3.12-slim-bullseye

WORKDIR /app
COPY --from=builder /app/merged_badwords.txt .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py .

ENV PYTHONUNBUFFERED=1
ENV DEBUG=0

CMD ["python", "handler.py"]
