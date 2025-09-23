import requests
import csv
from pathlib import Path

# List of repositories containing offensive word lists
REPOS = [
    "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master",
    "https://raw.githubusercontent.com/amirshnll/Persian-Swear-Words/master",
    "https://raw.githubusercontent.com/saadeghi/curse/master",
]

OUTFILE = Path("merged_badwords.csv")

def fetch_csv(url: str):
    print("Downloading:", url)
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    for row in csv.reader(r.text.splitlines()):
        if row:
            # take only first column (the word)
           yield row[0].strip()

def fetch_json(url: str):
    print("Downloading:", url)
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                yield item.strip()
            elif isinstance(item, dict) and 'word' in item:
                yield item['word'].strip()
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                yield value.strip()
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        yield item.strip()

def get_from_LDNBOOW():
    url = "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master"
    langs = [
        "ar",  # Arabic
        "zh",  # Chinese
        "cs",  # Czech
        "da",  # Danish
        "nl",  # Dutch
        "en",  # English
        "eo",  # Esperanto
        "fil", # Filipino
        "fi",  # Finnish
        "fr",  # French
        "fr-CA-u-sd-caqc",  # French (Canada) variant
        "de",  # German
        "hi",  # Hindi
        "hu",  # Hungarian
        "it",  # Italian
        "ja",  # Japanese
        "kab", # Kabyle
        "tlh", # Klingon
        "ko",  # Korean
        "no",  # Norwegian
        "fa",  # Persian
        "pl",  # Polish
        "pt",  # Portuguese
        "ru",  # Russian
        "es",  # Spanish
        "sv",  # Swedish
        "th",  # Thai
        "tr"   # Turkish
    ]
    for lang in langs:
        lang_url = f"{url}/{lang}"
        try:
            for w in fetch_csv(lang_url):
                if w:
                    yield w
        except Exception as e:
            print("Skip:", lang_url, "->", e)

def get_from_Persian_Swear_Words():
    url = "https://raw.githubusercontent.com/amirshnll/Persian-Swear-Words/master"
    try:
        for w in fetch_json(f"{url}/data.json"):
            if w:
                yield w
    except Exception as e:
        print("Skip:", url, "->", e)

def get_from_curse():
    url = "https://raw.githubusercontent.com/saadeghi/curse/master"
    langs = [
        "arabic",
        "chinese",
        "czech",
        "danish",
        "dutch",
        "english",
        "esperanto",
        "farsi",
        "finglish",
        "finnish",
        "french",
        "german",
        "hindi",
        "hungarian",
        "italian",
        "japanese",
        "korean",
        "norwegian",
        "polish",
        "portuguese",
        "russian",
        "spanish",
        "swedish",
        "thai",
        "turkish",
        "arabic",
        "chinese",
        "czech",
        "danish",
        "dutch",
        "english",
        "esperanto",
        "farsi",
        "finglish",
        "finnish",
        "french",
        "german",
        "hindi",
        "hungarian",
        "italian",
        "japanese",
        "korean",
        "norwegian",
        "polish",
        "portuguese",
        "russian",
        "spanish",
        "swedish",
        "thai",
        "turkish",
    ]
    for lang in langs:
        lang_url = f"{url}/{lang}.csv"
        try:
            for w in fetch_csv(lang_url):
                if w:
                    yield w
        except Exception as e:
            print("Skip:", lang_url, "->", e)

def main():
    words = set()
    words |= set(get_from_LDNBOOW())
    words |= set(get_from_Persian_Swear_Words())
    words |= set(get_from_curse())
    print(f"Total unique words collected: {len(words)}")
    # lower all words
    words = {w.lower() for w in words if w}
    print(f"Total unique words after lowercasing: {len(words)}")

    # save merged list
    OUTFILE.write_text(",\n".join(sorted(words)), encoding="utf8")
    print(f"Saved {len(words)} words to {OUTFILE}")

if __name__ == "__main__":
    main()
