import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

# Initialize the client (it automatically picks up GROQ_API_KEY from your system environment)
# If you don't have .env loading set up yet, you can temporarily do: Client(api_key="your_actual_key_here")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    completion = client.chat.completions.create(
        model="Llama-3.3-70B-Versatile",
        messages=[
            {
                "role": "user",
                "content": "Say 'Groq connection successful!' if you can read this."
            }
        ],
    )
    print("\n--- RESPONSE FROM GROQ ---")
    print(completion.choices[0].message.content)
    print("---------------------------\n")
except Exception as e:
    print(f"An error occurred: {e}")