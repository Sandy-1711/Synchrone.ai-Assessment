"""
Contract Scoring Algorithm
Implements weighted scoring system (0-100 points)
"""

from typing import Dict, Any, List


class ContractScorer:
    # Scoring weights (total = 100)
    WEIGHTS = {
        "financial_completeness": 30,
        "party_identification": 25,
        "payment_terms_clarity": 20,
        "sla_definition": 15,
        "contact_information": 10
    }
    
    def calculate_score(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall score and category scores
        Returns score, category breakdown, missing fields, and confidence levels
        """
        category_scores = {}
        missing_fields = []
        confidence_levels = {}
        
        # 1. Financial Completeness (30 points)
        financial_score, financial_missing, financial_confidence = self._score_financial_details(
            parsed_data.get("financial_details", {})
        )
        category_scores["financial_completeness"] = financial_score
        missing_fields.extend(financial_missing)
        confidence_levels["financial_details"] = financial_confidence
        
        # 2. Party Identification (25 points)
        party_score, party_missing, party_confidence = self._score_party_identification(
            parsed_data.get("party_identification", {})
        )
        category_scores["party_identification"] = party_score
        missing_fields.extend(party_missing)
        confidence_levels["party_identification"] = party_confidence
        
        # 3. Payment Terms Clarity (20 points)
        payment_score, payment_missing, payment_confidence = self._score_payment_terms(
            parsed_data.get("payment_structure", {})
        )
        category_scores["payment_terms_clarity"] = payment_score
        missing_fields.extend(payment_missing)
        confidence_levels["payment_structure"] = payment_confidence
        
        # 4. SLA Definition (15 points)
        sla_score, sla_missing, sla_confidence = self._score_sla_terms(
            parsed_data.get("sla_terms", {})
        )
        category_scores["sla_definition"] = sla_score
        missing_fields.extend(sla_missing)
        confidence_levels["sla_terms"] = sla_confidence
        
        # 5. Contact Information (10 points)
        contact_score, contact_missing, contact_confidence = self._score_contact_info(
            parsed_data.get("account_information", {})
        )
        category_scores["contact_information"] = contact_score
        missing_fields.extend(contact_missing)
        confidence_levels["account_information"] = contact_confidence
        
        # Calculate overall score
        overall_score = sum(category_scores.values())
        
        return {
            "overall_score": round(overall_score, 2),
            "category_scores": category_scores,
            "missing_fields": missing_fields,
            "confidence_levels": confidence_levels
        }
    
    def _score_financial_details(self, financial: Dict[str, Any]) -> tuple:
        """Score financial completeness (30 points max)"""
        score = 0
        missing = []
        
        # Currency (3 points)
        if financial.get("currency"):
            score += 3
        else:
            missing.append("Financial Details: Currency")
        
        # Line items (10 points)
        line_items = financial.get("line_items", [])
        if line_items:
            # Score based on completeness of line items
            complete_items = sum(1 for item in line_items 
                               if item.get("description") and item.get("unit_price"))
            score += min(10, (complete_items / len(line_items)) * 10)
        else:
            missing.append("Financial Details: Line Items")
        
        # Total value (8 points)
        if financial.get("total_value") is not None:
            score += 8
        else:
            missing.append("Financial Details: Total Value")
        
        # Tax information (5 points)
        if financial.get("tax_rate") or financial.get("tax_amount"):
            score += 5
        else:
            missing.append("Financial Details: Tax Information")
        
        # Subtotal (4 points)
        if financial.get("subtotal") is not None:
            score += 4
        else:
            missing.append("Financial Details: Subtotal")
        
        # Determine confidence level
        confidence = self._calculate_confidence(score, 30)
        
        return score, missing, confidence
    
    def _score_party_identification(self, parties: Dict[str, Any]) -> tuple:
        """Score party identification (25 points max)"""
        score = 0
        missing = []
        
        customer = parties.get("customer", {})
        vendor = parties.get("vendor", {})
        
        # Customer information (12.5 points)
        customer_score = 0
        if customer.get("name"):
            customer_score += 4
        else:
            missing.append("Party Identification: Customer Name")
        
        if customer.get("legal_entity") or customer.get("registration_number"):
            customer_score += 3.5
        else:
            missing.append("Party Identification: Customer Legal Entity")
        
        if customer.get("address"):
            customer_score += 2.5
        else:
            missing.append("Party Identification: Customer Address")
        
        if customer.get("signatory"):
            customer_score += 2.5
        else:
            missing.append("Party Identification: Customer Signatory")
        
        # Vendor information (12.5 points)
        vendor_score = 0
        if vendor.get("name"):
            vendor_score += 4
        else:
            missing.append("Party Identification: Vendor Name")
        
        if vendor.get("legal_entity") or vendor.get("registration_number"):
            vendor_score += 3.5
        else:
            missing.append("Party Identification: Vendor Legal Entity")
        
        if vendor.get("address"):
            vendor_score += 2.5
        else:
            missing.append("Party Identification: Vendor Address")
        
        if vendor.get("signatory"):
            vendor_score += 2.5
        else:
            missing.append("Party Identification: Vendor Signatory")
        
        score = customer_score + vendor_score
        confidence = self._calculate_confidence(score, 25)
        
        return score, missing, confidence
    
    def _score_payment_terms(self, payment: Dict[str, Any]) -> tuple:
        """Score payment terms clarity (20 points max)"""
        score = 0
        missing = []
        
        # Payment terms (8 points)
        if payment.get("payment_terms"):
            score += 8
        else:
            missing.append("Payment Structure: Payment Terms")
        
        # Payment schedule or due dates (6 points)
        if payment.get("payment_schedule") or payment.get("due_dates"):
            score += 6
        else:
            missing.append("Payment Structure: Payment Schedule")
        
        # Payment method (4 points)
        if payment.get("payment_method"):
            score += 4
        else:
            missing.append("Payment Structure: Payment Method")
        
        # Banking details (2 points)
        if payment.get("bank_details"):
            score += 2
        else:
            missing.append("Payment Structure: Bank Details")
        
        confidence = self._calculate_confidence(score, 20)
        
        return score, missing, confidence
    
    def _score_sla_terms(self, sla: Dict[str, Any]) -> tuple:
        """Score SLA definition (15 points max)"""
        score = 0
        missing = []
        
        # Performance metrics (6 points)
        if sla.get("performance_metrics") or sla.get("uptime_guarantee"):
            score += 6
        else:
            missing.append("SLA Terms: Performance Metrics")
        
        # Response/resolution times (5 points)
        if sla.get("response_time") or sla.get("resolution_time"):
            score += 5
        else:
            missing.append("SLA Terms: Response/Resolution Times")
        
        # Support terms (2 points)
        if sla.get("support_hours"):
            score += 2
        else:
            missing.append("SLA Terms: Support Hours")
        
        # Penalties (2 points)
        if sla.get("penalties"):
            score += 2
        else:
            missing.append("SLA Terms: Penalty Clauses")
        
        confidence = self._calculate_confidence(score, 15)
        
        return score, missing, confidence
    
    def _score_contact_info(self, account: Dict[str, Any]) -> tuple:
        """Score contact information (10 points max)"""
        score = 0
        missing = []
        
        # Billing contact (5 points)
        billing_complete = bool(
            account.get("billing_contact") or 
            account.get("billing_email") or 
            account.get("billing_phone")
        )
        if billing_complete:
            score += 5
        else:
            missing.append("Contact Information: Billing Contact")
        
        # Technical contact (3 points)
        technical_complete = bool(
            account.get("technical_contact") or 
            account.get("technical_email")
        )
        if technical_complete:
            score += 3
        else:
            missing.append("Contact Information: Technical Contact")
        
        # Account number (2 points)
        if account.get("account_number"):
            score += 2
        else:
            missing.append("Contact Information: Account Number")
        
        confidence = self._calculate_confidence(score, 10)
        
        return score, missing, confidence
    
    def _calculate_confidence(self, score: float, max_score: float) -> str:
        """Calculate confidence level based on score percentage"""
        percentage = (score / max_score) * 100
        
        if percentage >= 90:
            return "high"
        elif percentage >= 70:
            return "medium"
        elif percentage >= 50:
            return "low"
        else:
            return "very_low"