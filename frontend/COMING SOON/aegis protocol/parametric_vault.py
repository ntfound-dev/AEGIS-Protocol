# parametric_vault.py
# Parametric Insurance Vault - komponen yang missing dari PDF

import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class PayoutRecord:
    event_id: str
    policy_id: str
    amount: float
    executed_at: datetime
    recipient_dao: str

class ParametricInsuranceVault:
    """
    Parametric Insurance Vault - Dana darurat otomatis
    Sesuai PDF: "Dana darurat yang sudah disiapkan di blockchain ICP
    Otomatis mencairkan dana saat bencana terverifikasi"
    """
    
    def __init__(self, initial_balance: float = 10_000_000):
        self.balance = initial_balance
        self.policies = self._create_policies()
        self.payout_history: List[PayoutRecord] = []
        self.logger = logging.getLogger("aegis.vault")
    
    def _create_policies(self) -> Dict:
        """Create parametric policies sesuai PDF"""
        return {
            "earthquake_emergency": {
                "conditions": {"min_magnitude": 6.0, "min_confidence": 0.8},
                "payout": 2_000_000  # $2M sesuai PDF
            },
            "flood_critical": {
                "conditions": {"min_severity": 4, "min_confidence": 0.75},
                "payout": 1_500_000
            },
            "fire_major": {
                "conditions": {"min_confidence": 80, "min_area": 50},
                "payout": 1_200_000
            }
        }
    
    async def auto_payout(self, consensus_result: Dict, event_data: Dict) -> Optional[PayoutRecord]:
        """Auto payout saat kondisi terpenuhi"""
        if not consensus_result["decision"]:
            return None
            
        # Find matching policy
        policy = self._find_policy(event_data, consensus_result)
        if not policy:
            return None
            
        policy_id, policy_data = policy
        amount = policy_data["payout"]
        
        if self.balance < amount:
            self.logger.error(f"Insufficient vault balance: {self.balance}")
            return None
        
        # Execute payout
        self.balance -= amount
        
        payout = PayoutRecord(
            event_id=event_data["event_id"],
            policy_id=policy_id,
            amount=amount,
            executed_at=datetime.now(),
            recipient_dao=f"dao_{event_data['event_id']}"
        )
        
        self.payout_history.append(payout)
        self.logger.info(f"✅ Auto-payout: ${amount:,} for {event_data['event_id']}")
        
        return payout
    
    def _find_policy(self, event_data: Dict, consensus: Dict) -> Optional[tuple]:
        """Find matching policy for event"""
        for policy_id, policy in self.policies.items():
            conditions = policy["conditions"]
            
            # Check conditions
            if "min_confidence" in conditions:
                if consensus.get("confidence", 0) < conditions["min_confidence"]:
                    continue
            
            if "min_magnitude" in conditions:
                magnitude = float(event_data.get("metadata", {}).get("magnitude", 0))
                if magnitude < conditions["min_magnitude"]:
                    continue
            
            if "min_severity" in conditions:
                severity = event_data.get("severity", 1)
                if hasattr(severity, 'value'):
                    severity = severity.value
                if severity < conditions["min_severity"]:
                    continue
            
            return (policy_id, policy)
        
        return None
    
    def get_vault_status(self) -> Dict:
        """Get vault status"""
        total_payouts = sum(p.amount for p in self.payout_history)
        return {
            "balance": self.balance,
            "total_payouts": total_payouts,
            "active_policies": len(self.policies),
            "payout_count": len(self.payout_history)
        }