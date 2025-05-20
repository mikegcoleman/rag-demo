import requests
import os

def query_llm(base_url: str, model_name: str, prompt: str) -> str:
    # Normalize base URL and append OpenAI endpoint
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    url = f"{base_url}/chat/completions"

    # Build request
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()

    return result["choices"][0]["message"]["content"]
