"""
Diagnostic Engine for Clinical Assessment
Provides ICD-10, SNOMED-CT integration and diagnostic reasoning
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from models.assessment import (
    AssessmentResult, ClinicalFinding, FindingType, Diagnosis, 
    DiagnosticEvidence, UrgencyLevel, ExplainableAI
)
from models.patient import RadiologyAnalysis

logger = logging.getLogger(__name__)

class DiagnosticEngine:
    """Engine for clinical diagnostic assessment and reasoning"""
    
    def __init__(self):
        self.icd10_codes = self._load_icd10_codes()
        self.snomed_codes = self._load_snomed_codes()
        self.diagnostic_rules = self._load_diagnostic_rules()
        
    def _load_icd10_codes(self) -> Dict[str, Dict[str, Any]]:
        """Load ICD-10 code database"""
        # In a real implementation, this would load from a comprehensive database
        return {
            "I25.9": {"name": "Chronic ischemic heart disease, unspecified", "category": "cardiovascular"},
            "J44.1": {"name": "Chronic obstructive pulmonary disease with acute exacerbation", "category": "respiratory"},
            "M79.3": {"name": "Panniculitis, unspecified", "category": "musculoskeletal"},
            "R50.9": {"name": "Fever, unspecified", "category": "symptoms"},
            "Z00.00": {"name": "Encounter for general adult medical examination without abnormal findings", "category": "examination"},
            "K21.9": {"name": "Gastro-esophageal reflux disease without esophagitis", "category": "digestive"},
            "F32.9": {"name": "Major depressive disorder, single episode, unspecified", "category": "mental"},
            "E11.9": {"name": "Type 2 diabetes mellitus without complications", "category": "endocrine"},
            "N18.6": {"name": "End stage renal disease", "category": "genitourinary"},
            "C78.00": {"name": "Secondary malignant neoplasm of unspecified lung", "category": "neoplasms"}
        }
    
    def _load_snomed_codes(self) -> Dict[str, Dict[str, Any]]:
        """Load SNOMED-CT code database"""
        # In a real implementation, this would load from a comprehensive database
        return {
            "44054006": {"name": "Diabetes mellitus", "category": "disorder"},
            "195967001": {"name": "Asthma", "category": "disorder"},
            "38341003": {"name": "Hypertensive disorder, systemic arterial", "category": "disorder"},
            "22253000": {"name": "Pain", "category": "symptom"},
            "386053000": {"name": "Decision to admit", "category": "procedure"},
            "225358003": {"name": "Chest pain", "category": "symptom"},
            "267036007": {"name": "Dyspnea", "category": "symptom"},
            "25064002": {"name": "Headache", "category": "symptom"},
            "161891005": {"name": "History of myocardial infarction", "category": "history"},
            "271737000": {"name": "Abnormal chest X-ray", "category": "finding"}
        }
    
    def _load_diagnostic_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load diagnostic reasoning rules"""
        return {
            "chest_pain": [
                {
                    "conditions": ["chest pain", "chest discomfort"],
                    "differential": ["I25.9", "J44.1", "R50.9"],
                    "urgency": "high",
                    "required_tests": ["ECG", "chest X-ray", "troponin"]
                }
            ],
            "shortness_breath": [
                {
                    "conditions": ["dyspnea", "shortness of breath", "breathing difficulty"],
                    "differential": ["J44.1", "I25.9", "C78.00"],
                    "urgency": "high",
                    "required_tests": ["chest X-ray", "ABG", "pulse oximetry"]
                }
            ],
            "fever": [
                {
                    "conditions": ["fever", "elevated temperature", "pyrexia"],
                    "differential": ["R50.9", "J44.1", "K21.9"],
                    "urgency": "medium",
                    "required_tests": ["blood culture", "CBC", "chest X-ray"]
                }
            ]
        }
    
    async def generate_assessment(
        self, 
        patient_data: Dict[str, Any], 
        radiology_analysis: Optional[List[RadiologyAnalysis]] = None,
        assessment_type: str = "comprehensive"
    ) -> AssessmentResult:
        """
        Generate comprehensive clinical assessment
        
        Args:
            patient_data: FHIR-formatted patient data
            radiology_analysis: Results from radiology AI analysis
            assessment_type: Type of assessment to perform
            
        Returns:
            AssessmentResult with diagnostic findings
        """
        try:
            logger.info("Starting diagnostic assessment generation")
            
            # Extract clinical findings from patient data
            clinical_findings = await self._extract_clinical_findings(patient_data)
            
            # Add radiology findings if available
            if radiology_analysis:
                radiology_findings = self._extract_radiology_findings(radiology_analysis)
                clinical_findings.extend(radiology_findings)
            
            # Generate differential diagnoses
            differential_diagnoses = await self._generate_differential_diagnoses(clinical_findings)
            
            # Determine primary diagnosis
            primary_diagnosis = self._determine_primary_diagnosis(differential_diagnoses)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(clinical_findings, differential_diagnoses)
            
            # Determine urgency level
            urgency_level = self._determine_urgency_level(clinical_findings, differential_diagnoses)
            
            # Generate risk factors
            risk_factors = self._identify_risk_factors(patient_data, clinical_findings)
            
            # Determine follow-up requirements
            follow_up_required, follow_up_timeline = self._determine_follow_up(
                differential_diagnoses, urgency_level
            )
            
            # Generate treatment recommendations
            treatment_recommendations = self._generate_treatment_recommendations(
                differential_diagnoses, clinical_findings
            )
            
            # Generate monitoring requirements
            monitoring_requirements = self._generate_monitoring_requirements(
                differential_diagnoses, urgency_level
            )
            
            # Identify contraindications
            contraindications = self._identify_contraindications(patient_data, differential_diagnoses)
            
            # Identify red flags
            red_flags = self._identify_red_flags(clinical_findings, differential_diagnoses)
            
            assessment_result = AssessmentResult(
                primary_diagnosis=primary_diagnosis,
                differential_diagnoses=differential_diagnoses,
                clinical_findings=clinical_findings,
                confidence_score=confidence_score,
                urgency_level=urgency_level,
                radiology_analysis=radiology_analysis[0] if radiology_analysis else None,
                risk_factors=risk_factors,
                follow_up_required=follow_up_required,
                follow_up_timeline=follow_up_timeline,
                treatment_recommendations=treatment_recommendations,
                monitoring_requirements=monitoring_requirements,
                contraindications=contraindications,
                red_flags=red_flags
            )
            
            logger.info("Diagnostic assessment generation completed")
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error generating assessment: {str(e)}")
            raise
    
    async def _extract_clinical_findings(self, patient_data: Dict[str, Any]) -> List[ClinicalFinding]:
        """Extract clinical findings from patient data"""
        findings = []
        
        # Extract from anamnesis
        if "entry" in patient_data:
            for entry in patient_data["entry"]:
                resource = entry.get("resource", {})
                
                if resource.get("resourceType") == "Observation":
                    # Extract from observation
                    if "valueString" in resource:
                        finding = ClinicalFinding(
                            finding_type=FindingType.SYMPTOM,
                            description=resource["valueString"],
                            confidence=0.8,
                            source="anamnesis",
                            icd10_codes=self._find_related_icd10_codes(resource["valueString"]),
                            snomed_codes=self._find_related_snomed_codes(resource["valueString"])
                        )
                        findings.append(finding)
                
                elif resource.get("resourceType") == "Condition":
                    # Extract from existing conditions
                    code_info = resource.get("code", {}).get("coding", [{}])[0]
                    finding = ClinicalFinding(
                        finding_type=FindingType.SIGN,
                        description=code_info.get("display", "Unknown condition"),
                        confidence=0.9,
                        source="existing_diagnosis",
                        icd10_codes=[code_info.get("code", "")],
                        snomed_codes=self._find_related_snomed_codes(code_info.get("display", ""))
                    )
                    findings.append(finding)
        
        return findings
    
    def _extract_radiology_findings(self, radiology_analysis: List[RadiologyAnalysis]) -> List[ClinicalFinding]:
        """Extract clinical findings from radiology analysis"""
        findings = []
        
        for analysis in radiology_analysis:
            for finding_text in analysis.findings:
                finding = ClinicalFinding(
                    finding_type=FindingType.IMAGING,
                    description=finding_text,
                    confidence=analysis.confidence_scores.get(finding_text, 0.7),
                    source=f"radiology_{analysis.process_name}",
                    icd10_codes=self._find_related_icd10_codes(finding_text),
                    snomed_codes=self._find_related_snomed_codes(finding_text)
                )
                findings.append(finding)
        
        return findings
    
    async def _generate_differential_diagnoses(self, clinical_findings: List[ClinicalFinding]) -> List[Diagnosis]:
        """Generate differential diagnoses based on clinical findings"""
        differential_diagnoses = []
        
        # Analyze findings for diagnostic patterns
        finding_texts = [f.description.lower() for f in clinical_findings]
        
        # Check against diagnostic rules
        for rule_name, rules in self.diagnostic_rules.items():
            for rule in rules:
                if any(condition in " ".join(finding_texts) for condition in rule["conditions"]):
                    for icd10_code in rule["differential"]:
                        if icd10_code in self.icd10_codes:
                            diagnosis = Diagnosis(
                                code=icd10_code,
                                name=self.icd10_codes[icd10_code]["name"],
                                confidence=self._calculate_diagnosis_confidence(clinical_findings, icd10_code),
                                evidence=self._generate_evidence(clinical_findings, icd10_code),
                                probability=self._calculate_diagnosis_probability(clinical_findings, icd10_code),
                                differential_rank=len(differential_diagnoses) + 1
                            )
                            differential_diagnoses.append(diagnosis)
        
        # Sort by confidence and probability
        differential_diagnoses.sort(key=lambda x: (x.confidence + x.probability) / 2, reverse=True)
        
        return differential_diagnoses[:5]  # Return top 5 differential diagnoses
    
    def _determine_primary_diagnosis(self, differential_diagnoses: List[Diagnosis]) -> Optional[Diagnosis]:
        """Determine primary diagnosis from differential list"""
        if not differential_diagnoses:
            return None
        
        # Return highest confidence diagnosis
        return differential_diagnoses[0]
    
    def _calculate_confidence_score(self, clinical_findings: List[ClinicalFinding], differential_diagnoses: List[Diagnosis]) -> float:
        """Calculate overall confidence score"""
        if not clinical_findings and not differential_diagnoses:
            return 0.0
        
        # Weight clinical findings and diagnoses
        findings_score = sum(f.confidence for f in clinical_findings) / len(clinical_findings) if clinical_findings else 0.0
        diagnoses_score = sum(d.confidence for d in differential_diagnoses) / len(differential_diagnoses) if differential_diagnoses else 0.0
        
        # Weighted average
        return (findings_score * 0.6 + diagnoses_score * 0.4)
    
    def _determine_urgency_level(self, clinical_findings: List[ClinicalFinding], differential_diagnoses: List[Diagnosis]) -> UrgencyLevel:
        """Determine urgency level based on findings and diagnoses"""
        # Check for high-urgency keywords
        high_urgency_keywords = ["acute", "severe", "critical", "emergency", "chest pain", "shortness of breath"]
        medium_urgency_keywords = ["moderate", "worsening", "persistent"]
        
        all_text = " ".join([f.description.lower() for f in clinical_findings])
        
        if any(keyword in all_text for keyword in high_urgency_keywords):
            return UrgencyLevel.HIGH
        elif any(keyword in all_text for keyword in medium_urgency_keywords):
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW
    
    def _identify_risk_factors(self, patient_data: Dict[str, Any], clinical_findings: List[ClinicalFinding]) -> List[str]:
        """Identify risk factors from patient data"""
        risk_factors = []
        
        # Age-based risk factors
        if "entry" in patient_data:
            for entry in patient_data["entry"]:
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Patient":
                    birth_date = resource.get("birthDate")
                    if birth_date:
                        age = self._calculate_age(birth_date)
                        if age > 65:
                            risk_factors.append("Advanced age (>65 years)")
                        elif age > 50:
                            risk_factors.append("Middle age (50-65 years)")
        
        # Condition-based risk factors
        for finding in clinical_findings:
            if "diabetes" in finding.description.lower():
                risk_factors.append("Diabetes mellitus")
            elif "hypertension" in finding.description.lower():
                risk_factors.append("Hypertension")
            elif "smoking" in finding.description.lower():
                risk_factors.append("Smoking history")
        
        return risk_factors
    
    def _determine_follow_up(self, differential_diagnoses: List[Diagnosis], urgency_level: UrgencyLevel) -> tuple:
        """Determine follow-up requirements"""
        if urgency_level == UrgencyLevel.HIGH:
            return True, "24-48 hours"
        elif urgency_level == UrgencyLevel.MEDIUM:
            return True, "1-2 weeks"
        elif differential_diagnoses:
            return True, "2-4 weeks"
        else:
            return False, None
    
    def _generate_treatment_recommendations(self, differential_diagnoses: List[Diagnosis], clinical_findings: List[ClinicalFinding]) -> List[str]:
        """Generate treatment recommendations"""
        recommendations = []
        
        if differential_diagnoses:
            primary = differential_diagnoses[0]
            recommendations.append(f"Consider treatment for {primary.name}")
            recommendations.append("Monitor response to treatment")
            recommendations.append("Adjust therapy based on clinical response")
        
        recommendations.append("Patient education on condition and management")
        recommendations.append("Lifestyle modifications as appropriate")
        
        return recommendations
    
    def _generate_monitoring_requirements(self, differential_diagnoses: List[Diagnosis], urgency_level: UrgencyLevel) -> List[str]:
        """Generate monitoring requirements"""
        monitoring = []
        
        if urgency_level == UrgencyLevel.HIGH:
            monitoring.extend([
                "Continuous vital signs monitoring",
                "Frequent clinical assessment",
                "Laboratory monitoring as indicated"
            ])
        elif urgency_level == UrgencyLevel.MEDIUM:
            monitoring.extend([
                "Regular vital signs",
                "Symptom monitoring",
                "Follow-up laboratory tests"
            ])
        else:
            monitoring.extend([
                "Routine follow-up",
                "Symptom monitoring",
                "Annual screening as appropriate"
            ])
        
        return monitoring
    
    def _identify_contraindications(self, patient_data: Dict[str, Any], differential_diagnoses: List[Diagnosis]) -> List[str]:
        """Identify contraindications"""
        contraindications = []
        
        # Check for drug allergies or contraindications
        # This would typically come from patient history or medication lists
        contraindications.append("Verify drug allergies before prescribing")
        contraindications.append("Check for drug interactions")
        
        return contraindications
    
    def _identify_red_flags(self, clinical_findings: List[ClinicalFinding], differential_diagnoses: List[Diagnosis]) -> List[str]:
        """Identify red flags requiring immediate attention"""
        red_flags = []
        
        red_flag_keywords = [
            "severe", "acute", "sudden", "worsening", "unable to", 
            "chest pain", "shortness of breath", "loss of consciousness"
        ]
        
        for finding in clinical_findings:
            if any(keyword in finding.description.lower() for keyword in red_flag_keywords):
                red_flags.append(f"Red flag: {finding.description}")
        
        return red_flags
    
    def _find_related_icd10_codes(self, text: str) -> List[str]:
        """Find related ICD-10 codes for text"""
        related_codes = []
        text_lower = text.lower()
        
        for code, info in self.icd10_codes.items():
            if any(keyword in text_lower for keyword in info["name"].lower().split()):
                related_codes.append(code)
        
        return related_codes
    
    def _find_related_snomed_codes(self, text: str) -> List[str]:
        """Find related SNOMED-CT codes for text"""
        related_codes = []
        text_lower = text.lower()
        
        for code, info in self.snomed_codes.items():
            if any(keyword in text_lower for keyword in info["name"].lower().split()):
                related_codes.append(code)
        
        return related_codes
    
    def _calculate_diagnosis_confidence(self, clinical_findings: List[ClinicalFinding], icd10_code: str) -> float:
        """Calculate confidence for a specific diagnosis"""
        # Simple heuristic based on finding matches
        if not clinical_findings:
            return 0.5
        
        matching_findings = 0
        for finding in clinical_findings:
            if icd10_code in finding.icd10_codes:
                matching_findings += 1
        
        return min(0.9, 0.5 + (matching_findings * 0.1))
    
    def _generate_evidence(self, clinical_findings: List[ClinicalFinding], icd10_code: str) -> List[DiagnosticEvidence]:
        """Generate evidence for a diagnosis"""
        evidence = []
        
        for finding in clinical_findings:
            if icd10_code in finding.icd10_codes:
                evidence.append(DiagnosticEvidence(
                    evidence_type="clinical_finding",
                    description=finding.description,
                    strength=finding.confidence,
                    source=finding.source
                ))
        
        return evidence
    
    def _calculate_diagnosis_probability(self, clinical_findings: List[ClinicalFinding], icd10_code: str) -> float:
        """Calculate probability for a diagnosis"""
        # Similar to confidence but may use different weighting
        return self._calculate_diagnosis_confidence(clinical_findings, icd10_code)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date"""
        try:
            birth = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
            today = datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except:
            return 0
    
    def search_icd10_codes(self, query: str) -> List[Dict[str, Any]]:
        """Search ICD-10 codes"""
        results = []
        query_lower = query.lower()
        
        for code, info in self.icd10_codes.items():
            if query_lower in code.lower() or query_lower in info["name"].lower():
                results.append({
                    "code": code,
                    "name": info["name"],
                    "category": info["category"]
                })
        
        return results[:10]  # Return top 10 results
    
    def search_snomed_codes(self, query: str) -> List[Dict[str, Any]]:
        """Search SNOMED-CT codes"""
        results = []
        query_lower = query.lower()
        
        for code, info in self.snomed_codes.items():
            if query_lower in code or query_lower in info["name"].lower():
                results.append({
                    "code": code,
                    "name": info["name"],
                    "category": info["category"]
                })
        
        return results[:10]  # Return top 10 results
    
    def generate_recommendations(self, assessment_result: AssessmentResult) -> List[str]:
        """Generate clinical recommendations based on assessment"""
        recommendations = []
        
        if assessment_result.primary_diagnosis:
            recommendations.append(f"Primary diagnosis: {assessment_result.primary_diagnosis.name}")
        
        if assessment_result.differential_diagnoses:
            recommendations.append("Consider differential diagnoses:")
            for i, diagnosis in enumerate(assessment_result.differential_diagnoses[:3], 1):
                recommendations.append(f"  {i}. {diagnosis.name} (confidence: {diagnosis.confidence:.2f})")
        
        if assessment_result.urgency_level == UrgencyLevel.HIGH:
            recommendations.append("URGENT: Immediate medical attention required")
        elif assessment_result.urgency_level == UrgencyLevel.MEDIUM:
            recommendations.append("MODERATE: Follow-up within 1-2 weeks recommended")
        
        if assessment_result.red_flags:
            recommendations.append("RED FLAGS identified:")
            for flag in assessment_result.red_flags:
                recommendations.append(f"  - {flag}")
        
        if assessment_result.treatment_recommendations:
            recommendations.append("Treatment recommendations:")
            for rec in assessment_result.treatment_recommendations:
                recommendations.append(f"  - {rec}")
        
        return recommendations
