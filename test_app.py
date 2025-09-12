#!/usr/bin/env python3
"""
Test script for AI Clinical Assessment Engine
Tests basic functionality without requiring external dependencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from models.patient import Patient, PatientData, RadiologyImage
        from models.assessment import AssessmentResult, ClinicalFinding
        from services.api_client import BedenHealthcareAPIClient
        from services.ai_engine import ClinicalAIEngine
        from services.fhir_processor import FHIRProcessor
        from services.diagnostic_engine import DiagnosticEngine
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_models():
    """Test model creation and validation"""
    try:
        from models.patient import Patient, Gender
        from datetime import datetime
        
        # Test Patient model
        patient = Patient(
            id=1,
            identityNumber="12345678901",
            name="John",
            surname="Doe",
            gender=Gender.MALE,
            birthDate=datetime(1980, 1, 1)
        )
        
        print(f"✅ Patient model created: {patient.name} {patient.surname}")
        return True
    except Exception as e:
        print(f"❌ Model test error: {e}")
        return False

def test_services():
    """Test service initialization"""
    try:
        from services.api_client import BedenHealthcareAPIClient
        from services.ai_engine import ClinicalAIEngine
        from services.fhir_processor import FHIRProcessor
        from services.diagnostic_engine import DiagnosticEngine
        
        # Initialize services
        api_client = BedenHealthcareAPIClient()
        ai_engine = ClinicalAIEngine()
        fhir_processor = FHIRProcessor()
        diagnostic_engine = DiagnosticEngine()
        
        print("✅ All services initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Service test error: {e}")
        return False

def test_icd10_search():
    """Test ICD-10 code search"""
    try:
        from services.diagnostic_engine import DiagnosticEngine
        
        engine = DiagnosticEngine()
        results = engine.search_icd10_codes("diabetes")
        
        print(f"✅ ICD-10 search returned {len(results)} results")
        if results:
            print(f"   Example: {results[0]['code']} - {results[0]['name']}")
        return True
    except Exception as e:
        print(f"❌ ICD-10 test error: {e}")
        return False

def test_snomed_search():
    """Test SNOMED-CT code search"""
    try:
        from services.diagnostic_engine import DiagnosticEngine
        
        engine = DiagnosticEngine()
        results = engine.search_snomed_codes("pain")
        
        print(f"✅ SNOMED-CT search returned {len(results)} results")
        if results:
            print(f"   Example: {results[0]['code']} - {results[0]['name']}")
        return True
    except Exception as e:
        print(f"❌ SNOMED-CT test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing AI Clinical Assessment Engine")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Model Test", test_models),
        ("Service Test", test_services),
        ("ICD-10 Test", test_icd10_search),
        ("SNOMED-CT Test", test_snomed_search)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   Test failed: {test_name}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python main.py")
        print("3. Open browser: http://localhost:8000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
