"""
Assessment models for the AI Clinical Assessment Engine
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FindingType(str, Enum):
    SYMPTOM = "symptom"
    SIGN = "sign"
    LAB = "lab"
    IMAGING = "imaging"
    VITAL = "vital"

class ClinicalFinding(BaseModel):
    """Individual clinical finding with detailed metadata"""
    finding_type: FindingType = Field(..., description="Type of clinical finding")
    description: str = Field(..., description="Detailed description of the finding")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    source: str = Field(..., description="Source of the finding")
    icd10_codes: List[str] = Field(default=[], description="Related ICD-10 codes")
    snomed_codes: List[str] = Field(default=[], description="Related SNOMED-CT codes")
    severity: Optional[str] = Field(None, description="Severity of the finding")
    onset_date: Optional[datetime] = Field(None, description="When the finding was first observed")
    duration: Optional[str] = Field(None, description="Duration of the finding")

class DiagnosticEvidence(BaseModel):
    """Evidence supporting a diagnosis"""
    evidence_type: str = Field(..., description="Type of evidence")
    description: str = Field(..., description="Description of the evidence")
    strength: float = Field(..., ge=0.0, le=1.0, description="Strength of evidence (0-1)")
    source: str = Field(..., description="Source of the evidence")

class Diagnosis(BaseModel):
    """Diagnosis with supporting evidence"""
    code: str = Field(..., description="Diagnosis code (ICD-10)")
    name: str = Field(..., description="Diagnosis name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in diagnosis (0-1)")
    evidence: List[DiagnosticEvidence] = Field(default=[], description="Supporting evidence")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability of this diagnosis")
    differential_rank: int = Field(..., description="Rank in differential diagnosis list")

class AssessmentResult(BaseModel):
    """Comprehensive clinical assessment result"""
    primary_diagnosis: Optional[Diagnosis] = Field(None, description="Primary diagnosis")
    differential_diagnoses: List[Diagnosis] = Field(default=[], description="Differential diagnoses")
    clinical_findings: List[ClinicalFinding] = Field(default=[], description="All clinical findings")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    urgency_level: UrgencyLevel = Field(..., description="Urgency level")
    risk_factors: List[str] = Field(default=[], description="Identified risk factors")
    follow_up_required: bool = Field(..., description="Whether follow-up is required")
    follow_up_timeline: Optional[str] = Field(None, description="Recommended follow-up timeline")
    treatment_recommendations: List[str] = Field(default=[], description="Treatment recommendations")
    monitoring_requirements: List[str] = Field(default=[], description="Monitoring requirements")
    contraindications: List[str] = Field(default=[], description="Contraindications")
    red_flags: List[str] = Field(default=[], description="Red flags requiring immediate attention")

class ExplainableAI(BaseModel):
    """Explainable AI insights and reasoning"""
    decision_path: List[str] = Field(..., description="Step-by-step decision path")
    key_factors: List[str] = Field(..., description="Key factors influencing the assessment")
    confidence_breakdown: Dict[str, float] = Field(..., description="Confidence breakdown by factor")
    alternative_scenarios: List[str] = Field(default=[], description="Alternative diagnostic scenarios")
    limitations: List[str] = Field(default=[], description="Known limitations of the assessment")
    data_quality: Dict[str, Any] = Field(default={}, description="Data quality assessment")

class ClinicalAssessment(BaseModel):
    """Complete clinical assessment with metadata"""
    assessment_id: str = Field(..., description="Unique assessment ID")
    patient_id: int = Field(..., description="Patient ID")
    timestamp: datetime = Field(..., description="Assessment timestamp")
    assessment_result: AssessmentResult = Field(..., description="Assessment results")
    explainable_ai: ExplainableAI = Field(..., description="Explainable AI insights")
    ai_model_version: str = Field(..., description="AI model version used")
    processing_time: float = Field(..., description="Processing time in seconds")
    data_sources: List[str] = Field(..., description="Data sources used in assessment")
    quality_indicators: Dict[str, Any] = Field(default={}, description="Data quality indicators")
