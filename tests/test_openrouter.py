import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

# We initialize the standard OpenAI client but override the base URL to point to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY") ,
)

try:
    # We will test with a free model automatically routed by OpenRouter
    completion = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": "Say 'OpenRouter connection successful!' if you can read this."
            }
        ]
    )
    
    print("\n--- RESPONSE FROM OPENROUTER ---")
    print(completion.choices[0].message.content)
    print("--------------------------------\n")
except Exception as e:
    print(f"An error occurred: {e}")