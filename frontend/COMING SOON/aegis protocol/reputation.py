# reputation.py
# Reputation management and SBT minting agent (FIXED VERSION)

from typing import Dict, List
from datetime import datetime
from base_agent import BaseAgent, AgentType

class ReputationManagerAgent(BaseAgent):
    """Manages reputation system and SBT (Soulbound Token) minting"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.REPUTATION_MANAGER)
        self.reputation_ledger = {}  # participant_id -> reputation data
        self.sbt_templates = self._load_sbt_templates()
    
    def _load_sbt_templates(self) -> Dict[str, Dict]:
        """Define SBT templates for different achievements"""
        return {
            "first_responder": {
                "name": "First Responder",
                "description": "Arrived within first 4 hours of disaster alert",
                "reputation_boost": 50,
                "rarity": "common"
            },
            "top_donor": {
                "name": "Guardian Angel",
                "description": "Top 1% donor in disaster response",
                "reputation_boost": 100,
                "rarity": "rare"
            },
            "validator_hero": {
                "name": "Oracle Validator",
                "description": "95%+ accuracy in disaster validation",
                "reputation_boost": 75,
                "rarity": "uncommon"
            },
            "mission_complete": {
                "name": "Mission Accomplished",
                "description": "Participated in successful disaster response",
                "reputation_boost": 25,
                "rarity": "common"
            }
        }
    
    async def process(self, event_completion: Dict) -> List[Dict]:
        """Process event completion and mint SBTs"""
        event_id = event_completion["event_id"]
        participants = event_completion["participants"]
        mission_outcome = event_completion["outcome"]
        
        minted_sbts = []
        
        for participant in participants:
            # Determine which SBTs to mint based on participation
            eligible_sbts = await self._calculate_eligible_sbts(
                participant, event_completion
            )
            
            for sbt_type in eligible_sbts:
                sbt = await self._mint_sbt(participant["id"], sbt_type, event_id)
                minted_sbts.append(sbt)
                
                # Update reputation
                await self._update_reputation(
                    participant["id"], 
                    self.sbt_templates[sbt_type]["reputation_boost"]
                )
        
        self.logger.info(f"Minted {len(minted_sbts)} SBTs for event {event_id}")
        return minted_sbts
    
    async def _calculate_eligible_sbts(self, participant: Dict, event: Dict) -> List[str]:
        """Calculate which SBTs participant is eligible for - FIXED VERSION"""
        eligible = []
        
        # Mission completion SBT for all participants
        if event["outcome"] == "success":
            eligible.append("mission_complete")
        
        # First responder SBT - FIXED: Handle None values properly
        arrival_time = participant.get("arrival_time")
        if arrival_time is not None and arrival_time <= 4:  # 4 hours
            eligible.append("first_responder")
        
        # Top donor SBT - FIXED: Handle None values properly
        donation_percentile = participant.get("donation_percentile")
        if donation_percentile is not None and donation_percentile >= 99:
            eligible.append("top_donor")
        
        # Validator hero SBT - FIXED: Handle None values properly
        accuracy = participant.get("accuracy")
        if (participant.get("role") == "validator" and 
            accuracy is not None and accuracy >= 0.95):
            eligible.append("validator_hero")
        
        return eligible
    
    async def _mint_sbt(self, participant_id: str, sbt_type: str, event_id: str) -> Dict:
        """Mint Soulbound Token"""
        sbt_template = self.sbt_templates[sbt_type]
        
        sbt = {
            "token_id": f"sbt_{participant_id}_{sbt_type}_{event_id}",
            "recipient": participant_id,
            "type": sbt_type,
            "name": sbt_template["name"],
            "description": sbt_template["description"],
            "event_id": event_id,
            "minted_at": datetime.now(),
            "rarity": sbt_template["rarity"],
            "transferable": False  # Soulbound
        }
        
        # In real implementation: write to blockchain
        self.logger.info(f"Minted SBT {sbt_type} for {participant_id}")
        return sbt
    
    async def _update_reputation(self, participant_id: str, boost: int):
        """Update participant reputation score"""
        if participant_id not in self.reputation_ledger:
            self.reputation_ledger[participant_id] = {"score": 0, "history": []}
        
        self.reputation_ledger[participant_id]["score"] += boost
        self.reputation_ledger[participant_id]["history"].append({
            "boost": boost,
            "timestamp": datetime.now()
        })