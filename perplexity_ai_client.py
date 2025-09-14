import requests
import json
import base64
import os
from typing import Dict, Any
import request_create_json as r
from dotenv import load_dotenv
load_dotenv()

def read_patient_history(patient_id: int) -> str:
    """
    Read patient history from the history file.
    
    Args:
        patient_id (int): The patient ID
        
    Returns:
        str: Patient history content or empty string if file not found
    """
    history_file_path = f"received_data/patient_id_{patient_id}/patient_id_{patient_id}_history.txt"
    
    try:
        if os.path.exists(history_file_path):
            with open(history_file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        else:
            print(f"History file not found: {history_file_path}")
            return ""
    except Exception as e:
        print(f"Error reading history file: {e}")
        return ""

def send_to_perplexity_ai(input_dict: Dict[str, Any], image_path: str) -> str:
    """
    Send a dictionary and image to Perplexity AI API and return the response.

    Args:
        input_dict (Dict[str, Any]): Dictionary containing input data to send to AI
        image_path (str): Path to the image file to send

    Returns:
        str: Cleaned AI response as a plain string

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If API key is not provided
        requests.RequestException: If API request fails
    """

    # Get API key from environment variable
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set")

    # Check if image file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Encode image to base64
    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Error reading image file: {e}")

    # Read patient history
    patient_history = read_patient_history(r.ida)
    
    # Prepare the complete prompt including patient history
    complete_prompt = {
        **input_dict,
        "patient_history": patient_history
    }

    # Prepare the request payload with the complete prompt including history
    payload = {
        "model": "sonar",  # Perplexity's lowest cost model
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(complete_prompt, indent=2)  # Send the complete prompt with history
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.1,
    }

    # Set up headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Make the API request
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        # Parse the response
        ai_response = response.json()

        # Extract the AI's text response
        ai_text = ai_response["choices"][0]["message"]["content"]

        # Clean up the response
        import re

        ai_text = re.sub(r"\*\*(.*?)\*\*", r"\1", ai_text)  # Remove bold formatting
        ai_text = re.sub(r"\[\d+\]", "", ai_text)  # Remove reference numbers
        ai_text = re.sub(r"[ \t]+", " ", ai_text)  # Replace multiple spaces/tabs
        ai_text = ai_text.strip()

        return ai_text

    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"API request failed: {e}")
    except KeyError as e:
        raise ValueError(f"Unexpected API response format: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")


# Example usage for testing (run this file directly)
if __name__ == "__main__":
    test_prompt = {
        "requirements": "test, do not refer to the image, answer the questions in the input here.",
        "patient_data": "none",
        "opinion": "This is a test opinion",
        "question": "What is the weather in Berlin?",
    }

    test_image_path = "test.png"  # replace with a real path

    try:
        result = send_to_perplexity_ai(test_prompt, test_image_path)
        print("AI Response:")
        print(result)
    except Exception as e:
        print("Error:", e)