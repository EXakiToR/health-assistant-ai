"""
FHIR R4 processor for converting patient data to FHIR format
Ensures compatibility with HIMSS Stage 6-7 requirements
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from models.patient import PatientData, Patient, Gender

logger = logging.getLogger(__name__)

class FHIRProcessor:
    """Processor for FHIR R4 data conversion and validation"""
    
    def __init__(self):
        self.fhir_version = "R4"
        
    def convert_to_fhir(self, patient_data: PatientData) -> Dict[str, Any]:
        """
        Convert patient data to FHIR R4 format
        
        Args:
            patient_data: Patient data from Beden Healthcare API
            
        Returns:
            FHIR R4 formatted patient data
        """
        try:
            fhir_patient = self._create_fhir_patient(patient_data.patient)
            fhir_observations = self._create_fhir_observations(patient_data)
            fhir_conditions = self._create_fhir_conditions(patient_data)
            fhir_diagnostic_reports = self._create_fhir_diagnostic_reports(patient_data)
            
            fhir_bundle = {
                "resourceType": "Bundle",
                "type": "collection",
                "timestamp": datetime.now().isoformat(),
                "entry": [
                    fhir_patient,
                    *fhir_observations,
                    *fhir_conditions,
                    *fhir_diagnostic_reports
                ]
            }
            
            logger.info("Successfully converted patient data to FHIR R4 format")
            return fhir_bundle
            
        except Exception as e:
            logger.error(f"Error converting to FHIR: {str(e)}")
            raise
    
    def _create_fhir_patient(self, patient: Patient) -> Dict[str, Any]:
        """Create FHIR Patient resource"""
        
        # Map gender to FHIR coding
        gender_mapping = {
            Gender.MALE: "male",
            Gender.FEMALE: "female",
            Gender.OTHER: "other",
            Gender.UNKNOWN: "unknown"
        }
        
        fhir_patient = {
            "resourceType": "Patient",
            "id": str(patient.id),
            "identifier": [
                {
                    "use": "usual",
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "MR",
                                "display": "Medical Record Number"
                            }
                        ]
                    },
                    "value": patient.identity_number
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": patient.surname,
                    "given": [patient.name]
                }
            ],
            "gender": gender_mapping.get(patient.gender, "unknown"),
            "birthDate": patient.birth_date.strftime("%Y-%m-%d"),
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
            }
        }
        
        return {
            "resource": fhir_patient,
            "request": {
                "method": "POST",
                "url": "Patient"
            }
        }
    
    def _create_fhir_observations(self, patient_data: PatientData) -> list:
        """Create FHIR Observation resources from anamnesis"""
        observations = []
        
        if patient_data.anamnesis:
            # Create observation for medical history
            observation = {
                "resource": {
                    "resourceType": "Observation",
                    "id": f"anamnesis-{patient_data.patient.id}",
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                    "code": "history",
                                    "display": "History"
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "11369-6",
                                "display": "History of Past illness"
                            }
                        ]
                    },
                    "subject": {
                        "reference": f"Patient/{patient_data.patient.id}"
                    },
                    "valueString": patient_data.anamnesis,
                    "effectiveDateTime": datetime.now().isoformat()
                },
                "request": {
                    "method": "POST",
                    "url": "Observation"
                }
            }
            observations.append(observation)
        
        return observations
    
    def _create_fhir_conditions(self, patient_data: PatientData) -> list:
        """Create FHIR Condition resources from diagnoses"""
        conditions = []
        
        for i, diagnosis in enumerate(patient_data.diagnoses):
            condition = {
                "resource": {
                    "resourceType": "Condition",
                    "id": f"condition-{patient_data.patient.id}-{i}",
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "active",
                                "display": "Active"
                            }
                        ]
                    },
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                                "display": "Confirmed"
                            }
                        ]
                    },
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                                    "code": "encounter-diagnosis",
                                    "display": "Encounter Diagnosis"
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/sid/icd-10",
                                "code": diagnosis.code,
                                "display": diagnosis.name
                            }
                        ]
                    },
                    "subject": {
                        "reference": f"Patient/{patient_data.patient.id}"
                    },
                    "recordedDate": datetime.now().isoformat()
                },
                "request": {
                    "method": "POST",
                    "url": "Condition"
                }
            }
            conditions.append(condition)
        
        return conditions
    
    def _create_fhir_diagnostic_reports(self, patient_data: PatientData) -> list:
        """Create FHIR DiagnosticReport resources from radiology images"""
        reports = []
        
        for i, radiology_image in enumerate(patient_data.radiology_images):
            # Create imaging study
            imaging_study = {
                "resource": {
                    "resourceType": "ImagingStudy",
                    "id": f"imaging-study-{patient_data.patient.id}-{i}",
                    "status": "available",
                    "modality": {
                        "system": "http://dicom.nema.org/resources/ontology/DCM",
                        "code": self._map_process_to_modality(radiology_image.process_name)
                    },
                    "subject": {
                        "reference": f"Patient/{patient_data.patient.id}"
                    },
                    "started": datetime.now().isoformat(),
                    "series": [
                        {
                            "uid": f"series-{i}",
                            "number": i,
                            "modality": {
                                "system": "http://dicom.nema.org/resources/ontology/DCM",
                                "code": self._map_process_to_modality(radiology_image.process_name)
                            },
                            "instance": [
                                {
                                    "uid": f"instance-{j}",
                                    "sopClass": {
                                        "system": "urn:ietf:rfc:3986",
                                        "code": "1.2.840.10008.5.1.4.1.1.1"
                                    },
                                    "number": j
                                }
                                for j in range(len(radiology_image.files))
                            ]
                        }
                    ]
                },
                "request": {
                    "method": "POST",
                    "url": "ImagingStudy"
                }
            }
            reports.append(imaging_study)
            
            # Create diagnostic report
            diagnostic_report = {
                "resource": {
                    "resourceType": "DiagnosticReport",
                    "id": f"diagnostic-report-{patient_data.patient.id}-{i}",
                    "status": "final",
                    "category": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                                    "code": "RAD",
                                    "display": "Radiology"
                                }
                            ]
                        }
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "18748-4",
                                "display": "Diagnostic imaging study"
                            }
                        ]
                    },
                    "subject": {
                        "reference": f"Patient/{patient_data.patient.id}"
                    },
                    "effectiveDateTime": datetime.now().isoformat(),
                    "imagingStudy": [
                        {
                            "reference": f"ImagingStudy/imaging-study-{patient_data.patient.id}-{i}"
                        }
                    ],
                    "conclusion": f"Radiology study: {radiology_image.process_name}",
                    "presentedForm": [
                        {
                            "contentType": "application/dicom",
                            "data": file.file_data,
                            "title": file.file_name
                        }
                        for file in radiology_image.files
                    ]
                },
                "request": {
                    "method": "POST",
                    "url": "DiagnosticReport"
                }
            }
            reports.append(diagnostic_report)
        
        return reports
    
    def _map_process_to_modality(self, process_name: str) -> str:
        """Map process name to DICOM modality code"""
        process_lower = process_name.lower()
        
        if "xray" in process_lower or "x-ray" in process_lower:
            return "DX"
        elif "ct" in process_lower:
            return "CT"
        elif "mri" in process_lower:
            return "MR"
        elif "ultrasound" in process_lower or "us" in process_lower:
            return "US"
        elif "mammography" in process_lower:
            return "MG"
        else:
            return "OT"  # Other
    
    def validate_fhir_data(self, fhir_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate FHIR data structure
        
        Args:
            fhir_data: FHIR data to validate
            
        Returns:
            Validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "resource_count": 0
        }
        
        try:
            if fhir_data.get("resourceType") != "Bundle":
                validation_result["errors"].append("Root resource must be a Bundle")
                validation_result["valid"] = False
            
            if "entry" not in fhir_data:
                validation_result["errors"].append("Bundle must contain entries")
                validation_result["valid"] = False
            else:
                validation_result["resource_count"] = len(fhir_data["entry"])
                
                # Validate each entry
                for entry in fhir_data["entry"]:
                    if "resource" not in entry:
                        validation_result["errors"].append("Entry must contain resource")
                        validation_result["valid"] = False
                    elif "resourceType" not in entry["resource"]:
                        validation_result["errors"].append("Resource must have resourceType")
                        validation_result["valid"] = False
            
            logger.info(f"FHIR validation completed: {validation_result['valid']}")
            
        except Exception as e:
            validation_result["errors"].append(f"Validation error: {str(e)}")
            validation_result["valid"] = False
            logger.error(f"FHIR validation failed: {str(e)}")
        
        return validation_result
