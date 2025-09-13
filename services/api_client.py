"""
API client for Beden Healthcare Systems integration
Handles communication with the provided API endpoints
"""

import httpx
import logging
from typing import Optional, Dict, Any
from models.patient import PatientData

logger = logging.getLogger(__name__)

class BedenHealthcareAPIClient:
    """Client for Beden Healthcare API integration"""
    
    def __init__(self, base_url: str = "http://88.248.132.97:3333/lisapi"):
        self.base_url = base_url
        self.timeout = 30.0
        
    async def get_patient_data(self, patient_id: int) -> Optional[PatientData]:
        """
        Retrieve patient data from Beden Healthcare API
        
        Args:
            patient_id: Patient ID to retrieve data for
            
        Returns:
            PatientData object or None if not found
        """
        try:
            url = f"{self.base_url}/api/v1/Radiology/getPatientPacsImages"
            params = {"patientId": patient_id}
            
            logger.info(f"Fetching patient data for ID: {patient_id}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Successfully retrieved patient data for ID: {patient_id}")
                
                # Convert API response to PatientData model
                return PatientData(**data)
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Patient {patient_id} not found")
                return None
            else:
                logger.error(f"HTTP error retrieving patient {patient_id}: {e}")
                raise
        except httpx.TimeoutException:
            logger.error(f"Timeout retrieving patient {patient_id}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving patient {patient_id}: {str(e)}")
            raise
    
    async def test_connection(self) -> bool:
        """
        Test connection to Beden Healthcare API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Test with a known patient ID or health check endpoint
            url = f"{self.base_url}/api/v1/Radiology/getPatientPacsImages"
            params = {"patientId": 1}  # Test with patient ID 1
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                # Even if patient not found, connection is working
                return response.status_code in [200, 404]
                
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def decode_base64_image(self, file_data: str) -> bytes:
        """
        Decode base64 encoded image data
        
        Args:
            file_data: Base64 encoded string
            
        Returns:
            Decoded bytes
        """
        try:
            return base64.b64decode(file_data)
        except Exception as e:
            logger.error(f"Error decoding base64 data: {str(e)}")
            raise
    
    def get_image_metadata(self, file_name: str) -> Dict[str, Any]:
        """
        Extract metadata from image filename
        
        Args:
            file_name: Name of the image file
            
        Returns:
            Dictionary with image metadata
        """
        metadata = {
            "file_name": file_name,
            "file_extension": file_name.split('.')[-1].lower() if '.' in file_name else None,
            "is_dicom": file_name.lower().endswith(('.dcm', '.dicom')),
            "is_standard_image": file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif'))
        }
        
        # Try to extract study information from filename
        if '_' in file_name:
            parts = file_name.split('_')
            metadata["possible_study_id"] = parts[0] if parts[0].isdigit() else None
            metadata["possible_series"] = parts[1] if len(parts) > 1 else None
        
        return metadata
