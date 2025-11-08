import requests
from core.utils import get_env

def generate_conversation(prompt: str) -> list[str]:
    """Generate a conversation between two characters using Groq, without prepending speaker labels."""
    api_key = get_env("GROQ_API_KEY")
    model = get_env("GROQ_MODEL")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Generate a realistic back-and-forth conversation between two people "
                    "with natural expressions. Do NOT include speaker labels like A: or B:. "
                    "Return only the lines of dialogue separated by line breaks."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if res.status_code != 200:
        print("\n[Groq API Error]")
        print("Status Code:", res.status_code)
        print("Response:", res.text)
        raise requests.HTTPError(f"Groq API returned {res.status_code}")

    text = res.json()["choices"][0]["message"]["content"]

    # Split into lines and strip any leading/trailing whitespace
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Extra safety: remove any accidental "A:" or "B:" prefixes
    cleaned_lines = []
    for line in lines:
        if line[:2].upper() in ["A:", "B:"]:
            cleaned_lines.append(line[2:].strip())
        else:
            cleaned_lines.append(line)

    return cleaned_lines