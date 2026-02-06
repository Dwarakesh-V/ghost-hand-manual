import os
from google import genai

def generate_text(prompt):
    # Retrieve the API key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    # Initialize client
    client = genai.Client(api_key=api_key)

    try:
        # call the gemini-2.5-flash model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_text()