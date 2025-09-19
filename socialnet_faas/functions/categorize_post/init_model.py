from transformers import AutoTokenizer, AutoModelForSequenceClassification
from optimum.onnxruntime import ORTModelForSequenceClassification

model_name = "cardiffnlp/tweet-topic-21-multi"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Export to ONNX format
onnx_model = ORTModelForSequenceClassification.from_pretrained(
    model_name,
    export=True
)

onnx_model.save_pretrained("./onnx_model")
tokenizer.save_pretrained("./onnx_model")
