import os
from google import genai

def generate_text():
    # Retrieve the API key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    # Initialize the client (modern SDK)
    client = genai.Client(api_key=api_key)

    try:
        # call the gemini-2.5-flash model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain how a neural network works in one sentence."
        )
        
        # Print the text result
        print(response.text)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_text()