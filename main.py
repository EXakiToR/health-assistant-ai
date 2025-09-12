"""
AI Clinical Assessment Engine for Diagnostic Support
HealthTech Challenge - Beden Grup Healthcare Systems & InVitro Diagnostics

This application provides AI-powered clinical assessment and diagnostic support
by processing structured patient data through API integration and delivering
transparent decision support insights for clinical assessment and diagnosis.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import httpx
import base64
import json
import logging
from datetime import datetime
import uvicorn

from models.patient import Patient, RadiologyImage, Diagnosis
from models.assessment import ClinicalAssessment, AssessmentResult
from services.api_client import BedenHealthcareAPIClient
from services.ai_engine import ClinicalAIEngine
from services.fhir_processor import FHIRProcessor
from services.diagnostic_engine import DiagnosticEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Clinical Assessment Engine",
    description="AI-powered diagnostic support system for clinical assessment",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
api_client = BedenHealthcareAPIClient()
ai_engine = ClinicalAIEngine()
fhir_processor = FHIRProcessor()
diagnostic_engine = DiagnosticEngine()

# Mount static files for web interface
app.mount("/static", StaticFiles(directory="static"), name="static")

class AssessmentRequest(BaseModel):
    """Request model for clinical assessment"""
    patient_id: int = Field(..., description="Patient ID for data retrieval")
    include_radiology: bool = Field(True, description="Include radiology images in assessment")
    assessment_type: str = Field("comprehensive", description="Type of assessment to perform")

class AssessmentResponse(BaseModel):
    """Response model for clinical assessment"""
    assessment_id: str
    patient_id: int
    timestamp: datetime
    assessment_result: AssessmentResult
    confidence_score: float
    recommendations: List[str]
    explainable_ai: Dict[str, Any]

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>AI Clinical Assessment Engine</title></head>
            <body>
                <h1>AI Clinical Assessment Engine</h1>
                <p>API is running. Visit <a href="/api/docs">/api/docs</a> for API documentation.</p>
            </body>
        </html>
        """)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/v1/assessment", response_model=AssessmentResponse)
async def perform_clinical_assessment(request: AssessmentRequest):
    """
    Perform AI-powered clinical assessment on patient data
    
    This endpoint:
    1. Retrieves patient data from Beden Healthcare API
    2. Processes radiology images and clinical data
    3. Generates AI-powered diagnostic insights
    4. Returns structured clinical assessment report
    """
    try:
        logger.info(f"Starting clinical assessment for patient {request.patient_id}")
        
        # Step 1: Retrieve patient data from API
        patient_data = await api_client.get_patient_data(request.patient_id)
        
        if not patient_data:
            raise HTTPException(status_code=404, detail="Patient data not found")
        
        # Step 2: Process FHIR data
        fhir_patient = fhir_processor.convert_to_fhir(patient_data)
        
        # Step 3: Process radiology images if requested
        radiology_analysis = None
        if request.include_radiology and patient_data.get("radiologyImages"):
            radiology_analysis = await ai_engine.analyze_radiology_images(
                patient_data["radiologyImages"]
            )
        
        # Step 4: Generate clinical assessment
        assessment_result = await diagnostic_engine.generate_assessment(
            patient_data=fhir_patient,
            radiology_analysis=radiology_analysis,
            assessment_type=request.assessment_type
        )
        
        # Step 5: Create explainable AI insights
        explainable_ai = ai_engine.generate_explainable_insights(
            assessment_result, patient_data
        )
        
        # Step 6: Generate recommendations
        recommendations = diagnostic_engine.generate_recommendations(assessment_result)
        
        # Create response
        response = AssessmentResponse(
            assessment_id=f"ASSESS_{request.patient_id}_{int(datetime.now().timestamp())}",
            patient_id=request.patient_id,
            timestamp=datetime.now(),
            assessment_result=assessment_result,
            confidence_score=assessment_result.confidence_score,
            recommendations=recommendations,
            explainable_ai=explainable_ai
        )
        
        logger.info(f"Assessment completed for patient {request.patient_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in clinical assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@app.get("/api/v1/patient/{patient_id}")
async def get_patient_data(patient_id: int):
    """Retrieve patient data from Beden Healthcare API"""
    try:
        patient_data = await api_client.get_patient_data(patient_id)
        if not patient_data:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient_data
    except Exception as e:
        logger.error(f"Error retrieving patient data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve patient data: {str(e)}")

@app.get("/api/v1/icd10/search")
async def search_icd10_codes(query: str):
    """Search ICD-10 codes for diagnostic support"""
    try:
        codes = diagnostic_engine.search_icd10_codes(query)
        return {"query": query, "codes": codes}
    except Exception as e:
        logger.error(f"Error searching ICD-10 codes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ICD-10 search failed: {str(e)}")

@app.get("/api/v1/snomed/search")
async def search_snomed_codes(query: str):
    """Search SNOMED-CT codes for clinical terminology"""
    try:
        codes = diagnostic_engine.search_snomed_codes(query)
        return {"query": query, "codes": codes}
    except Exception as e:
        logger.error(f"Error searching SNOMED codes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SNOMED search failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
