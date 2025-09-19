FROM python:3.12-slim-bullseye AS builder

WORKDIR /app

# Install only required deps
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir transformers optimum[onnxruntime]

# Export ONNX model at build time
COPY init_model.py .
RUN python init_model.py

FROM python:3.12-slim-bullseye

WORKDIR /app

# Install only runtime deps
RUN pip install --no-cache-dir onnxruntime transformers

# Copy handler and model
COPY --from=builder /app/onnx_model ./onnx_model

RUN pip install --no-cache-dir fastapi uvicorn

COPY handler.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "handler.py"]
