#!/usr/bin/env python3
"""
Demo script for AI Clinical Assessment Engine
Demonstrates the key features and capabilities
"""

import asyncio
import json
from datetime import datetime
from models.patient import Patient, Gender, PatientData, RadiologyImage, FileData, Diagnosis
from models.assessment import AssessmentResult, UrgencyLevel
from services.diagnostic_engine import DiagnosticEngine
from services.ai_engine import ClinicalAIEngine
from services.fhir_processor import FHIRProcessor

async def demo_clinical_assessment():
    """Demonstrate the clinical assessment process"""
    print("🏥 AI Clinical Assessment Engine Demo")
    print("=" * 50)
    
    # Create sample patient data
    print("\n📋 Creating sample patient data...")
    patient = Patient(
        id=1,
        identityNumber="12345678901",
        name="John",
        surname="Doe",
        gender=Gender.MALE,
        birthDate=datetime(1980, 1, 1)
    )
    
    # Create sample diagnoses
    diagnoses = [
        Diagnosis(code="I25.9", name="Chronic ischemic heart disease, unspecified"),
        Diagnosis(code="E11.9", name="Type 2 diabetes mellitus without complications")
    ]
    
    # Create sample radiology images
    radiology_images = [
        RadiologyImage(
            processName="Chest X-ray",
            files=[
                FileData(
                    fileName="chest_xray_001.jpg",
                    fileData="base64_encoded_image_data_here"
                )
            ]
        )
    ]
    
    # Create complete patient data
    patient_data = PatientData(
        patient=patient,
        anamnesis="Patient presents with chest pain and shortness of breath. History of diabetes and hypertension.",
        diagnoses=diagnoses,
        radiologyImages=radiology_images
    )
    
    print(f"✅ Patient: {patient.name} {patient.surname} (ID: {patient.id})")
    print(f"✅ Medical History: {patient_data.anamnesis}")
    print(f"✅ Existing Diagnoses: {len(diagnoses)} conditions")
    print(f"✅ Radiology Images: {len(radiology_images)} studies")
    
    # Initialize services
    print("\n🔧 Initializing AI services...")
    ai_engine = ClinicalAIEngine()
    fhir_processor = FHIRProcessor()
    diagnostic_engine = DiagnosticEngine()
    
    print("✅ AI Engine initialized")
    print("✅ FHIR Processor initialized")
    print("✅ Diagnostic Engine initialized")
    
    # Process FHIR data
    print("\n📊 Converting to FHIR R4 format...")
    fhir_data = fhir_processor.convert_to_fhir(patient_data)
    print(f"✅ FHIR Bundle created with {len(fhir_data['entry'])} resources")
    
    # Analyze radiology images
    print("\n🔍 Analyzing radiology images...")
    radiology_analysis = await ai_engine.analyze_radiology_images(radiology_images)
    for analysis in radiology_analysis:
        print(f"✅ {analysis.process_name}: {len(analysis.findings)} findings, severity: {analysis.severity}")
    
    # Generate clinical assessment
    print("\n🧠 Generating clinical assessment...")
    assessment_result = await diagnostic_engine.generate_assessment(
        patient_data=fhir_data,
        radiology_analysis=radiology_analysis,
        assessment_type="comprehensive"
    )
    
    print(f"✅ Assessment completed")
    print(f"   Confidence Score: {assessment_result.confidence_score:.2f}")
    print(f"   Urgency Level: {assessment_result.urgency_level.value if hasattr(assessment_result.urgency_level, 'value') else assessment_result.urgency_level}")
    print(f"   Follow-up Required: {assessment_result.follow_up_required}")
    
    # Display results
    print("\n📋 Assessment Results:")
    print("-" * 30)
    
    if assessment_result.primary_diagnosis:
        print(f"Primary Diagnosis: {assessment_result.primary_diagnosis.name}")
        print(f"  Code: {assessment_result.primary_diagnosis.code}")
        print(f"  Confidence: {assessment_result.primary_diagnosis.confidence:.2f}")
    
    if assessment_result.differential_diagnoses:
        print(f"\nDifferential Diagnoses ({len(assessment_result.differential_diagnoses)}):")
        for i, diagnosis in enumerate(assessment_result.differential_diagnoses[:3], 1):
            print(f"  {i}. {diagnosis.name} (confidence: {diagnosis.confidence:.2f})")
    
    if assessment_result.clinical_findings:
        print(f"\nClinical Findings ({len(assessment_result.clinical_findings)}):")
        for finding in assessment_result.clinical_findings[:3]:
            print(f"  - {finding.finding_type}: {finding.description}")
    
    if assessment_result.treatment_recommendations:
        print(f"\nTreatment Recommendations:")
        for rec in assessment_result.treatment_recommendations[:3]:
            print(f"  - {rec}")
    
    # Demonstrate ICD-10 and SNOMED-CT search
    print("\n🔍 Medical Coding Search:")
    print("-" * 30)
    
    icd10_results = diagnostic_engine.search_icd10_codes("diabetes")
    print(f"ICD-10 search for 'diabetes': {len(icd10_results)} results")
    if icd10_results:
        print(f"  Example: {icd10_results[0]['code']} - {icd10_results[0]['name']}")
    
    snomed_results = diagnostic_engine.search_snomed_codes("pain")
    print(f"SNOMED-CT search for 'pain': {len(snomed_results)} results")
    if snomed_results:
        print(f"  Example: {snomed_results[0]['code']} - {snomed_results[0]['name']}")
    
    # Generate explainable AI insights
    print("\n🤖 Explainable AI Insights:")
    print("-" * 30)
    # Create a simple patient data dict for explainable AI
    patient_data_dict = {
        "patient": {
            "id": patient_data.patient.id,
            "name": patient_data.patient.name,
            "surname": patient_data.patient.surname,
            "gender": patient_data.patient.gender.value,
            "birthDate": patient_data.patient.birth_date.isoformat()
        },
        "anamnesis": patient_data.anamnesis,
        "diagnoses": [{"code": d.code, "name": d.name} for d in patient_data.diagnoses],
        "radiologyImages": [{"processName": img.process_name, "files": [{"fileName": f.file_name} for f in img.files]} for img in patient_data.radiology_images]
    }
    explainable_ai = ai_engine.generate_explainable_insights(assessment_result, patient_data_dict)
    
    if explainable_ai.get("decision_path"):
        print("Decision Path:")
        for i, step in enumerate(explainable_ai["decision_path"][:5], 1):
            print(f"  {i}. {step}")
    
    if explainable_ai.get("key_factors"):
        print("\nKey Factors:")
        for factor in explainable_ai["key_factors"][:3]:
            print(f"  - {factor}")
    
    print("\n🎉 Demo completed successfully!")
    print("\nTo run the full application:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the server: python main.py")
    print("3. Open browser: http://localhost:8000")
    print("4. Try the API: http://localhost:8000/api/docs")

if __name__ == "__main__":
    asyncio.run(demo_clinical_assessment())
