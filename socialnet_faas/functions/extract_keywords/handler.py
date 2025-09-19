import json

from rake_nltk import Rake


def handler(event, context=None):
    try:
        data = event if isinstance(event, dict) else json.loads(event)
        text = event.get('text', '')
        if not text:
            return {"status": "error", "body": "No text provided"}
        max_count = int(data.get('max_count', 10))
        r = Rake()
        r.extract_keywords_from_text(text)
        keywords = r.get_ranked_phrases()
        return {
            "status": "success",
            "body": {
                "keywords": keywords[:max_count]
            }
        }
    except Exception as e:
        return {"status": "error", "body": str(e)}

