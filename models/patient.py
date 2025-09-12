"""
Patient data models for the AI Clinical Assessment Engine
Compatible with FHIR R4 and Beden Healthcare API format
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"

class FindingType(str, Enum):
    SYMPTOM = "symptom"
    SIGN = "sign"
    LAB = "lab"
    IMAGING = "imaging"
    VITAL = "vital"

class Patient(BaseModel):
    """Patient information model"""
    id: int = Field(..., description="Patient ID")
    identity_number: str = Field(..., alias="identityNumber", description="National ID number")
    name: str = Field(..., description="Patient first name")
    surname: str = Field(..., description="Patient last name")
    gender: Gender = Field(..., description="Patient gender")
    birth_date: datetime = Field(..., alias="birthDate", description="Patient birth date")
    
    class Config:
        allow_population_by_field_name = True

class FileData(BaseModel):
    """File data model for radiology images"""
    file_name: str = Field(..., alias="fileName", description="Name of the file")
    file_data: str = Field(..., alias="fileData", description="Base64 encoded file data")
    
    class Config:
        allow_population_by_field_name = True

class RadiologyImage(BaseModel):
    """Radiology image model"""
    process_name: str = Field(..., alias="processName", description="Type of radiology process")
    files: List[FileData] = Field(..., description="List of image files")
    
    class Config:
        allow_population_by_field_name = True

class Diagnosis(BaseModel):
    """Diagnosis model"""
    code: str = Field(..., description="Diagnosis code (ICD-10)")
    name: str = Field(..., description="Diagnosis name")

class PatientData(BaseModel):
    """Complete patient data model from API"""
    patient: Patient = Field(..., description="Patient information")
    anamnesis: str = Field(..., description="Patient medical history")
    diagnoses: List[Diagnosis] = Field(..., description="List of current diagnoses")
    radiology_images: List[RadiologyImage] = Field(..., alias="radiologyImages", description="Radiology images")
    
    class Config:
        allow_population_by_field_name = True

class RadiologyAnalysis(BaseModel):
    """AI analysis results for radiology images"""
    process_name: str = Field(..., description="Type of radiology process")
    findings: List[str] = Field(..., description="AI-detected findings")
    confidence_scores: Dict[str, float] = Field(..., description="Confidence scores for each finding")
    recommendations: List[str] = Field(..., description="AI recommendations based on images")
    severity: str = Field(..., description="Overall severity assessment")

class ClinicalFinding(BaseModel):
    """Individual clinical finding"""
    finding_type: FindingType = Field(..., description="Type of finding (symptom, sign, lab, imaging)")
    description: str = Field(..., description="Description of the finding")
    confidence: float = Field(..., description="Confidence score (0-1)")
    source: str = Field(..., description="Source of the finding (anamnesis, radiology, etc.)")
    icd10_codes: List[str] = Field(default=[], description="Related ICD-10 codes")
    snomed_codes: List[str] = Field(default=[], description="Related SNOMED-CT codes")

class AssessmentResult(BaseModel):
    """Clinical assessment result"""
    primary_diagnosis: Optional[str] = Field(None, description="Primary diagnosis")
    differential_diagnoses: List[str] = Field(default=[], description="Differential diagnoses")
    clinical_findings: List[ClinicalFinding] = Field(default=[], description="Clinical findings")
    confidence_score: float = Field(..., description="Overall confidence score (0-1)")
    urgency_level: str = Field(..., description="Urgency level (low, medium, high, critical)")
    radiology_analysis: Optional[RadiologyAnalysis] = Field(None, description="Radiology analysis results")
    risk_factors: List[str] = Field(default=[], description="Identified risk factors")
    follow_up_required: bool = Field(..., description="Whether follow-up is required")
    follow_up_timeline: Optional[str] = Field(None, description="Recommended follow-up timeline")

class ClinicalAssessment(BaseModel):
    """Complete clinical assessment"""
    assessment_id: str = Field(..., description="Unique assessment ID")
    patient_id: int = Field(..., description="Patient ID")
    timestamp: datetime = Field(..., description="Assessment timestamp")
    assessment_result: AssessmentResult = Field(..., description="Assessment results")
    ai_model_version: str = Field(..., description="AI model version used")
    processing_time: float = Field(..., description="Processing time in seconds")
