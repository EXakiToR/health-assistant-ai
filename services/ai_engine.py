"""
AI Clinical Assessment Engine
Provides explainable AI-powered clinical assessment and diagnostic support
"""

import logging
import json
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from models.patient import RadiologyImage, RadiologyAnalysis, ClinicalFinding, FindingType
from models.assessment import ExplainableAI, Diagnosis, DiagnosticEvidence, UrgencyLevel

logger = logging.getLogger(__name__)

class ClinicalAIEngine:
    """AI engine for clinical assessment and diagnostic support"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.confidence_threshold = 0.7
        
    async def analyze_radiology_images(self, radiology_images: List[RadiologyImage]) -> List[RadiologyAnalysis]:
        """
        Analyze radiology images using AI
        
        Args:
            radiology_images: List of radiology images to analyze
            
        Returns:
            List of radiology analysis results
        """
        analyses = []
        
        for image_set in radiology_images:
            try:
                analysis = await self._analyze_image_set(image_set)
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing image set {image_set.process_name}: {str(e)}")
                # Create a basic analysis even if AI fails
                analyses.append(self._create_fallback_analysis(image_set))
        
        return analyses
    
    async def _analyze_image_set(self, image_set: RadiologyImage) -> RadiologyAnalysis:
        """Analyze a single set of radiology images"""
        
        # Simulate AI analysis (in real implementation, this would use actual AI models)
        findings = []
        confidence_scores = {}
        recommendations = []
        
        # Analyze based on process type
        if "chest" in image_set.process_name.lower():
            findings, confidence_scores, recommendations = await self._analyze_chest_xray(image_set)
        elif "ct" in image_set.process_name.lower():
            findings, confidence_scores, recommendations = await self._analyze_ct_scan(image_set)
        elif "mri" in image_set.process_name.lower():
            findings, confidence_scores, recommendations = await self._analyze_mri_scan(image_set)
        else:
            findings, confidence_scores, recommendations = await self._analyze_general_imaging(image_set)
        
        # Determine overall severity
        severity = self._determine_severity(confidence_scores, findings)
        
        return RadiologyAnalysis(
            process_name=image_set.process_name,
            findings=findings,
            confidence_scores=confidence_scores,
            recommendations=recommendations,
            severity=severity
        )
    
    async def _analyze_chest_xray(self, image_set: RadiologyImage) -> tuple:
        """Analyze chest X-ray images"""
        findings = []
        confidence_scores = {}
        recommendations = []
        
        # Simulate AI analysis for chest X-ray
        findings.extend([
            "Bilateral lung fields appear clear",
            "Cardiac silhouette within normal limits",
            "No acute pulmonary abnormalities detected"
        ])
        
        confidence_scores = {
            "lung_fields_clear": 0.85,
            "cardiac_normal": 0.90,
            "no_acute_abnormalities": 0.88
        }
        
        recommendations = [
            "Continue current treatment plan",
            "Follow up in 2-4 weeks if symptoms persist",
            "Consider additional imaging if clinical suspicion remains high"
        ]
        
        return findings, confidence_scores, recommendations
    
    async def _analyze_ct_scan(self, image_set: RadiologyImage) -> tuple:
        """Analyze CT scan images"""
        findings = []
        confidence_scores = {}
        recommendations = []
        
        # Simulate AI analysis for CT scan
        findings.extend([
            "No evidence of acute intracranial pathology",
            "Ventricular system appears normal",
            "No mass lesions identified"
        ])
        
        confidence_scores = {
            "no_acute_pathology": 0.92,
            "ventricular_normal": 0.88,
            "no_mass_lesions": 0.90
        }
        
        recommendations = [
            "No immediate intervention required",
            "Consider clinical correlation with symptoms",
            "Follow up imaging if indicated by clinical course"
        ]
        
        return findings, confidence_scores, recommendations
    
    async def _analyze_mri_scan(self, image_set: RadiologyImage) -> tuple:
        """Analyze MRI scan images"""
        findings = []
        confidence_scores = {}
        recommendations = []
        
        # Simulate AI analysis for MRI
        findings.extend([
            "Normal brain parenchyma signal intensity",
            "No evidence of acute stroke",
            "White matter changes consistent with age"
        ])
        
        confidence_scores = {
            "normal_parenchyma": 0.89,
            "no_acute_stroke": 0.94,
            "age_appropriate_changes": 0.82
        }
        
        recommendations = [
            "No acute neurological intervention required",
            "Consider neuropsychological evaluation if cognitive concerns",
            "Routine follow-up as clinically indicated"
        ]
        
        return findings, confidence_scores, recommendations
    
    async def _analyze_general_imaging(self, image_set: RadiologyImage) -> tuple:
        """Analyze general imaging studies"""
        findings = []
        confidence_scores = {}
        recommendations = []
        
        findings.extend([
            "Images technically adequate for interpretation",
            "No obvious abnormalities detected",
            "Clinical correlation recommended"
        ])
        
        confidence_scores = {
            "technical_adequacy": 0.85,
            "no_obvious_abnormalities": 0.75,
            "clinical_correlation_needed": 0.90
        }
        
        recommendations = [
            "Correlate with clinical presentation",
            "Consider additional imaging if clinical suspicion high",
            "Follow up as clinically indicated"
        ]
        
        return findings, confidence_scores, recommendations
    
    def _create_fallback_analysis(self, image_set: RadiologyImage) -> RadiologyAnalysis:
        """Create fallback analysis when AI processing fails"""
        return RadiologyAnalysis(
            process_name=image_set.process_name,
            findings=["Technical analysis unavailable - manual review recommended"],
            confidence_scores={"manual_review_needed": 1.0},
            recommendations=["Manual radiological interpretation required"],
            severity="unknown"
        )
    
    def _determine_severity(self, confidence_scores: Dict[str, float], findings: List[str]) -> str:
        """Determine overall severity based on findings and confidence"""
        if not confidence_scores:
            return "unknown"
        
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
        
        # Check for concerning keywords in findings
        concerning_keywords = ["acute", "abnormal", "pathology", "lesion", "mass", "bleeding"]
        concerning_findings = any(
            any(keyword in finding.lower() for keyword in concerning_keywords)
            for finding in findings
        )
        
        if concerning_findings and avg_confidence > 0.8:
            return "high"
        elif concerning_findings or avg_confidence < 0.6:
            return "medium"
        else:
            return "low"
    
    def generate_explainable_insights(self, assessment_result, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explainable AI insights for the assessment
        
        Args:
            assessment_result: The assessment result
            patient_data: Original patient data
            
        Returns:
            Dictionary containing explainable AI insights
        """
        insights = {
            "decision_path": self._generate_decision_path(assessment_result, patient_data),
            "key_factors": self._identify_key_factors(assessment_result, patient_data),
            "confidence_breakdown": self._breakdown_confidence(assessment_result),
            "alternative_scenarios": self._generate_alternative_scenarios(assessment_result),
            "limitations": self._identify_limitations(assessment_result, patient_data),
            "data_quality": self._assess_data_quality(patient_data)
        }
        
        return insights
    
    def _generate_decision_path(self, assessment_result, patient_data: Dict[str, Any]) -> List[str]:
        """Generate step-by-step decision path"""
        path = [
            "1. Retrieved patient data from Beden Healthcare API",
            "2. Processed patient demographics and medical history",
            "3. Analyzed radiology images using AI models",
            "4. Correlated clinical findings with imaging results",
            "5. Applied diagnostic algorithms and clinical guidelines",
            "6. Generated differential diagnosis list",
            "7. Calculated confidence scores for each diagnosis",
            "8. Determined urgency level based on findings",
            "9. Generated treatment recommendations"
        ]
        
        return path
    
    def _identify_key_factors(self, assessment_result, patient_data: Dict[str, Any]) -> List[str]:
        """Identify key factors influencing the assessment"""
        factors = []
        
        # Patient demographics
        if patient_data.get("patient", {}).get("gender"):
            factors.append(f"Patient gender: {patient_data['patient']['gender']}")
        
        if patient_data.get("patient", {}).get("birthDate"):
            factors.append(f"Patient age: {self._calculate_age(patient_data['patient']['birthDate'])}")
        
        # Medical history
        if patient_data.get("anamnesis"):
            factors.append("Medical history available for analysis")
        
        # Existing diagnoses
        if patient_data.get("diagnoses"):
            factors.append(f"Existing diagnoses: {len(patient_data['diagnoses'])} conditions")
        
        # Radiology findings
        if hasattr(assessment_result, 'radiology_analysis') and assessment_result.radiology_analysis:
            factors.append("Radiology imaging analysis completed")
        
        return factors
    
    def _breakdown_confidence(self, assessment_result) -> Dict[str, float]:
        """Break down confidence by different factors"""
        breakdown = {
            "clinical_findings": 0.85,
            "imaging_analysis": 0.80 if hasattr(assessment_result, 'radiology_analysis') and assessment_result.radiology_analysis else 0.0,
            "patient_history": 0.75,
            "diagnostic_algorithms": 0.88,
            "overall_assessment": assessment_result.confidence_score
        }
        
        return breakdown
    
    def _generate_alternative_scenarios(self, assessment_result) -> List[str]:
        """Generate alternative diagnostic scenarios"""
        scenarios = [
            "Consider alternative diagnosis if symptoms persist",
            "Rule out other conditions with similar presentation",
            "Monitor for progression of symptoms",
            "Consider additional diagnostic tests if indicated"
        ]
        
        return scenarios
    
    def _identify_limitations(self, assessment_result, patient_data: Dict[str, Any]) -> List[str]:
        """Identify limitations of the current assessment"""
        limitations = [
            "AI analysis is for decision support only, not replacement for clinical judgment",
            "Limited by quality and completeness of input data",
            "May not capture all clinical nuances and patient-specific factors",
            "Requires validation by qualified healthcare professionals"
        ]
        
        # Add specific limitations based on available data
        if not patient_data.get("radiologyImages"):
            limitations.append("No radiology images available for analysis")
        
        if not patient_data.get("anamnesis"):
            limitations.append("Limited medical history information")
        
        return limitations
    
    def _assess_data_quality(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of input data"""
        quality = {
            "patient_demographics": "complete" if patient_data.get("patient") else "incomplete",
            "medical_history": "available" if patient_data.get("anamnesis") else "missing",
            "existing_diagnoses": "available" if patient_data.get("diagnoses") else "none",
            "radiology_images": "available" if patient_data.get("radiologyImages") else "none",
            "overall_quality": "good" if all([
                patient_data.get("patient"),
                patient_data.get("anamnesis"),
                patient_data.get("radiologyImages")
            ]) else "limited"
        }
        
        return quality
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date"""
        try:
            birth = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
            today = datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except:
            return 0
