FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader punkt_tab && python -m nltk.downloader stopwords

COPY handler.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "handler.py"]
