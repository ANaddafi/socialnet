import onnxruntime as ort
from transformers import AutoTokenizer
import numpy as np

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


MODEL_DIR = "onnx_model"

# Topic labels from cardiffnlp/tweet-topic-21-multi
TOPIC_LABELS = [
    "arts_&_culture", "business_&_entrepreneurs", "celebrity_&_pop_culture",
    "diaries_&_daily_life", "family", "fashion_&_style", "film_tv_&_video",
    "fitness_&_health", "food_&_dining", "gaming", "learning_&_educational",
    "music", "news_&_social_concern", "other_hobbies", "relationships",
    "science_&_technology", "sports", "travel_&_adventure", "youth_&_student_life"
]

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
session = ort.InferenceSession(f"{MODEL_DIR}/model.onnx")

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(-1, keepdims=True)

def handler(event, context=None):
    text = event.get("text")
    if not text:
        return {"error": "No text provided"}

    # Tokenize → numpy tensors
    inputs = tokenizer(text, return_tensors="np")
    ort_inputs = {k: v for k, v in inputs.items()}

    # Run inference
    outputs = session.run(None, ort_inputs)
    logits = outputs[0]
    probs = softmax(logits)[0]

    # Map scores to labels
    results = [
        {"label": label, "score": float(score)}
        for label, score in zip(TOPIC_LABELS, probs)
    ]

    # Filter top ones
    topics = [r for r in results if r["score"] > 0.3]

    return {"topics": topics}

# MODEL_DIR = "onnx_model"

# # Load ONNX model + tokenizer once at cold start
# tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
# model = ORTModelForSequenceClassification.from_pretrained(MODEL_DIR)
# classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)

app = FastAPI()

# def handler(event, context=None):
#     # event: {"text": "..."}
#     text = event.get("text")
#     if not text:
#         return {"error": "No text provided"}

#     preds = classifier(text)
#     topics = [p for p in preds[0] if p["score"] > 0.3]

#     return {"topics": topics}

@app.post("/categorize")
async def categorize_post(request: Request):
    data = await request.json()
    result = handler(data)
    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9999)
