"""
Contract Parser using LLM for intelligent data extraction
"""

import json
import re
from typing import Dict, Any, List
from app.utils.llm_client import LLMClient


class ContractParser:
    def __init__(self):
        self.llm_client = LLMClient()
        
    def parse_contract(self, text: str) -> Dict[str, Any]:
        """
        Parse contract text and extract structured data using LLM
        """
        # Create comprehensive prompt for extraction
        prompt = self._create_extraction_prompt(text)
        
        # Get LLM response
        response = self.llm_client.extract_data(prompt)
        
        # Parse JSON response
        try:
            extracted_data = json.loads(response)
        except json.JSONDecodeError:
            print("LLM response.text output:\n", response)  # log the issue

            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group(1))
            else:
                # Fallback: basic extraction
                extracted_data = self._fallback_extraction(text)
        
        # Post-process and validate data
        return self._post_process_data(extracted_data)
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create detailed extraction prompt for LLM"""
        return f"""
You MUST return ONLY valid minified JSON.
No explanation. No markdown. No backticks. No comments.
If data not found, use null.

CONTRACT TEXT:
{text}

EXTRACT THE FOLLOWING (return null if not found):

{{
    "party_identification": {{
        "customer": {{
            "name": "Company name",
            "legal_entity": "Legal entity type",
            "registration_number": "Company registration number",
            "address": "Full address",
            "signatory": "Name of person signing",
            "signatory_role": "Title/role"
        }},
        "vendor": {{
            "name": "Vendor company name",
            "legal_entity": "Legal entity type",
            "registration_number": "Registration number",
            "address": "Full address",
            "signatory": "Name of person signing",
            "signatory_role": "Title/role"
        }},
        "third_parties": []
    }},
    "account_information": {{
        "account_number": "Account or customer number",
        "billing_contact": "Billing contact name",
        "billing_email": "Billing email",
        "billing_phone": "Billing phone",
        "technical_contact": "Technical contact name",
        "technical_email": "Technical email",
        "technical_phone": "Technical phone"
    }},
    "financial_details": {{
        "currency": "USD/EUR/etc",
        "line_items": [
            {{
                "description": "Product/service description",
                "quantity": 1,
                "unit_price": 100.00,
                "total": 100.00
            }}
        ],
        "subtotal": 0.00,
        "tax_rate": 0.00,
        "tax_amount": 0.00,
        "total_value": 0.00,
        "additional_fees": []
    }},
    "payment_structure": {{
        "payment_terms": "Net 30/Net 60/etc",
        "payment_method": "Wire transfer/Credit card/etc",
        "payment_schedule": [
            {{
                "due_date": "2024-01-01",
                "amount": 100.00,
                "description": "Initial payment"
            }}
        ],
        "due_dates": ["2024-01-01"],
        "bank_details": {{
            "bank_name": "Bank name",
            "account_number": "Account number",
            "routing_number": "Routing number",
            "swift_code": "SWIFT code"
        }}
    }},
    "revenue_classification": {{
        "has_recurring": true,
        "has_one_time": false,
        "billing_cycle": "monthly/quarterly/annual/one-time",
        "subscription_model": "Description of subscription",
        "auto_renewal": true,
        "renewal_terms": "Renewal terms description"
    }},
    "sla_terms": {{
        "uptime_guarantee": "99.9%",
        "response_time": "4 hours",
        "resolution_time": "24 hours",
        "performance_metrics": [
            {{
                "metric": "Uptime",
                "target": "99.9%",
                "measurement": "Monthly"
            }}
        ],
        "penalties": [
            {{
                "condition": "Uptime below 99%",
                "penalty": "10% credit",
                "calculation": "Description"
            }}
        ],
        "support_hours": "24/7/365",
        "escalation_procedures": "Description of escalation"
    }}
}}

Return ONLY the JSON object, no other text.
"""
    
    def _fallback_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback extraction using regex patterns"""
        return {
            "party_identification": {
                "customer": self._extract_party_info(text, "customer"),
                "vendor": self._extract_party_info(text, "vendor")
            },
            "account_information": {},
            "financial_details": {
                "line_items": [],
                "total_value": self._extract_total_value(text)
            },
            "payment_structure": {
                "payment_terms": self._extract_payment_terms(text)
            },
            "revenue_classification": {},
            "sla_terms": {}
        }
    
    def _extract_party_info(self, text: str, party_type: str) -> Dict[str, Any]:
        """Extract party information using patterns"""
        party_info = {}
        
        # Look for company names (simple pattern)
        company_pattern = r'([A-Z][A-Za-z\s&]+(?:Inc\.|LLC|Ltd\.|Corp\.|Corporation))'
        matches = re.findall(company_pattern, text)
        if matches:
            party_info["name"] = matches[0] if party_type == "customer" else matches[1] if len(matches) > 1 else None
        
        return party_info
    
    def _extract_total_value(self, text: str) -> float:
        """Extract total contract value"""
        # Look for currency amounts
        patterns = [
            r'\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'USD\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'total[:\s]+\$?\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return the largest value found
                values = [float(m.replace(',', '')) for m in matches]
                return max(values)
        
        return None
    
    def _extract_payment_terms(self, text: str) -> str:
        """Extract payment terms"""
        terms_pattern = r'Net\s+(\d+)'
        match = re.search(terms_pattern, text, re.IGNORECASE)
        if match:
            return f"Net {match.group(1)}"
        
        return None
    
    def _post_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate extracted data"""
        # Ensure all required sections exist
        required_sections = [
            "party_identification",
            "account_information",
            "financial_details",
            "payment_structure",
            "revenue_classification",
            "sla_terms"
        ]
        
        for section in required_sections:
            if section not in data:
                data[section] = {}
        
        # Clean empty values
        data = self._clean_empty_values(data)
        
        return data
    
    def _clean_empty_values(self, obj: Any) -> Any:
        """Recursively remove None and empty string values"""
        if isinstance(obj, dict):
            return {
                k: self._clean_empty_values(v)
                for k, v in obj.items()
                if v is not None and v != "" and v != []
            }
        elif isinstance(obj, list):
            return [self._clean_empty_values(item) for item in obj if item is not None]
        else:
            return obj