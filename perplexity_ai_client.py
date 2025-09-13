import requests
import json
import base64
import os
from typing import Dict, Any, Union
from PIL import Image
import io

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass

def send_to_perplexity_ai(input_dict: Dict[str, Any], image_path: str, custom_prompt: str = None) -> str:
    """
    Send a dictionary and image to Perplexity AI API and return the response.
    
    Args:
        input_dict (Dict[str, Any]): Dictionary containing input data to send to AI
        image_path (str): Path to the image file to send
        custom_prompt (str, optional): Custom instructions for how to process the data and image
        
    Returns:
        str: Cleaned AI response as a plain string
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If API key is not provided
        requests.RequestException: If API request fails
    """
    
    # Get API key from environment variable
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set")
    
    # Check if image file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Encode image to base64
    try:
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Error reading image file: {e}")
    
    # Prepare the prompt
    if custom_prompt:
        prompt_text = f"{custom_prompt}\n\nInput data: {json.dumps(input_dict, indent=2)}"
    else:
        prompt_text = f"Analyze this medical data and image. Provide a concise analysis in 4-5 sentences. You can use bullet points (-) and line breaks (\\n) for better readability, but avoid bold formatting (**). Input data: {json.dumps(input_dict, indent=2)}"
    
    # Prepare the request payload
    payload = {
        "model": "sonar",  # Perplexity's latest model
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 400,
        "temperature": 0.1
    }
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Make the API request
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        # Parse the response
        ai_response = response.json()
        
        # Extract the AI's text response
        ai_text = ai_response['choices'][0]['message']['content']
        
        # Clean up the response to remove only bold formatting while keeping bullet points and line breaks
        import re
        # Remove only bold formatting, keep bullet points and line breaks
        ai_text = re.sub(r'\*\*(.*?)\*\*', r'\1', ai_text)  # Remove bold formatting
        # Only replace multiple spaces that are not followed by newlines
        ai_text = re.sub(r'[ \t]+', ' ', ai_text)  # Replace multiple spaces/tabs with single space
        ai_text = ai_text.strip()
        
        # Return just the cleaned string response
        return ai_text
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"API request failed: {e}")
    except KeyError as e:
        raise ValueError(f"Unexpected API response format: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")


def send_to_perplexity_ai_with_pil_image(input_dict: Dict[str, Any], pil_image: Image.Image, custom_prompt: str = None) -> str:
    """
    Send a dictionary and PIL Image object to Perplexity AI API and return the response.
    
    Args:
        input_dict (Dict[str, Any]): Dictionary containing input data to send to AI
        pil_image (PIL.Image.Image): PIL Image object to send
        custom_prompt (str, optional): Custom instructions for how to process the data and image
        
    Returns:
        str: Cleaned AI response as a plain string
    """
    
    # Get API key from environment variable
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable not set")
    
    # Convert PIL image to base64
    try:
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Error converting PIL image to base64: {e}")
    
    # Prepare the prompt
    if custom_prompt:
        prompt_text = f"{custom_prompt}\n\nInput data: {json.dumps(input_dict, indent=2)}"
    else:
        prompt_text = f"Analyze this medical data and image. Provide a concise analysis in 4-5 sentences. You can use bullet points (-) and line breaks (\\n) for better readability, but avoid bold formatting (**). Input data: {json.dumps(input_dict, indent=2)}"
    
    # Prepare the request payload
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 400,
        "temperature": 0.1
    }
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Make the API request
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        # Parse the response
        ai_response = response.json()
        
        # Extract the AI's text response
        ai_text = ai_response['choices'][0]['message']['content']
        
        # Clean up the response to remove only bold formatting while keeping bullet points and line breaks
        import re
        # Remove only bold formatting, keep bullet points and line breaks
        ai_text = re.sub(r'\*\*(.*?)\*\*', r'\1', ai_text)  # Remove bold formatting
        # Only replace multiple spaces that are not followed by newlines
        ai_text = re.sub(r'[ \t]+', ' ', ai_text)  # Replace multiple spaces/tabs with single space
        ai_text = ai_text.strip()
        
        # Return just the cleaned string response
        return ai_text
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"API request failed: {e}")
    except KeyError as e:
        raise ValueError(f"Unexpected API response format: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")


# Example usage function
def example_usage():
    """
    Example of how to use the Perplexity AI client functions
    """
    # Example input dictionary
    sample_data = {
        "patient_id": 12345,
        "patient_name": "John Doe",
        "age": 45,
        "info": """Pacient: X 
                Data: 05.08.2025
                Data nasterii: 15.07.1967 Vîrsta: 58 a.

                Radiografie digital a mainii bilateral(1 incidenta)

                Descriere Radiografie
                GE Healthcare Proteus XR/F DAP: 0.39 mGycm2
                Osteoporoza epifizara, juxtaarticulara bilateral, simetric, cu desen trabecular pastrat.
                Spatiile articulare in articulatiile radio- carpiene pe dreapta , metacarpo-falangiene si interfalangiene
                proximale si distale – reduse, cu scleroza subcondrala la nivelul suprafetelor articulare.
                Formatiuni productive pronuntate si osteofitoza pe contururile laterale si mediale a articulatiilor
                interfalangiene distale.
                Multiple formatiuni chistice in oasele carpiene, epifizele metacarpieneleor si falangiene bilateral.
                Formatiuni productive incipiente pe contururile laterale si mediale a articulatiilor metacarpofalangiene
                , interfalangiene proximale si distale.
                Concluzie Rx : Semne radiologice indirecte de artropatie seronegativa nediferentiata posibil
                reactiva (de exclus focar cronic de infectie) – necesita evaluare in context clinic si de
                laborator / DD artrita seronegative psoriazica. Osteoartrita deformanta
                degenerativa articulațiilor interfalangiene distale, proximale si metacarpo-falangiene.""",
    }
    
    # Example image path (replace with actual image path)
    image_path = "received_data/1.png"
    
    try:
        # Example with custom prompt
        custom_instruction = "Focus on the bone structure and joint spaces. Identify any abnormalities or conditions visible in the X-ray."
        result = send_to_perplexity_ai(sample_data, image_path, custom_instruction)
        
        print("AI Analysis Result:")
        print(result)  # Now prints just the string
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    # Run example if script is executed directly
    example_usage()
    # print("test\ntest\ntest")
