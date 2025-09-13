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

def send_to_perplexity_ai(input_dict: Dict[str, Any], image_path: str) -> Dict[str, Any]:
    """
    Send a dictionary and image to Perplexity AI API and return the response.
    
    Args:
        input_dict (Dict[str, Any]): Dictionary containing input data to send to AI
        image_path (str): Path to the image file to send
        
    Returns:
        Dict[str, Any]: Dictionary containing the AI response merged with original input
        
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
    
    # Prepare the request payload
    payload = {
        "model": "sonar",  # Perplexity's latest model
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Please analyze this medical data and image. Input data: {json.dumps(input_dict, indent=2)}"
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
        "max_tokens": 1000,
        "temperature": 0.2
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
        
        # Create the output dictionary by merging input with AI response
        output_dict = input_dict.copy()
        output_dict['ai_analysis'] = ai_text
        output_dict['ai_response_metadata'] = {
            'model': ai_response.get('model'),
            'usage': ai_response.get('usage'),
            'created': ai_response.get('created')
        }
        
        return output_dict
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"API request failed: {e}")
    except KeyError as e:
        raise ValueError(f"Unexpected API response format: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")


def send_to_perplexity_ai_with_pil_image(input_dict: Dict[str, Any], pil_image: Image.Image) -> Dict[str, Any]:
    """
    Send a dictionary and PIL Image object to Perplexity AI API and return the response.
    
    Args:
        input_dict (Dict[str, Any]): Dictionary containing input data to send to AI
        pil_image (PIL.Image.Image): PIL Image object to send
        
    Returns:
        Dict[str, Any]: Dictionary containing the AI response merged with original input
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
    
    # Prepare the request payload
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Please analyze this medical data and image. Input data: {json.dumps(input_dict, indent=2)}"
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
        "max_tokens": 1000,
        "temperature": 0.2
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
        
        # Create the output dictionary by merging input with AI response
        output_dict = input_dict.copy()
        output_dict['ai_analysis'] = ai_text
        output_dict['ai_response_metadata'] = {
            'model': ai_response.get('model'),
            'usage': ai_response.get('usage'),
            'created': ai_response.get('created')
        }
        
        return output_dict
        
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
        # Send to Perplexity AI
        result = send_to_perplexity_ai(sample_data, image_path)
        
        print("AI Analysis Result:")
        print(json.dumps(result, indent=2))
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    # Run example if script is executed directly
    example_usage()
