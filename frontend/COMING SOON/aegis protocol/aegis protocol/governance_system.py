# governance_system.py
# Governance dan voting system untuk Event DAO sesuai PDF

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class ProposalType(Enum):
    FUND_ALLOCATION = "fund_allocation"
    RESOURCE_REQUEST = "resource_request"  
    LOGISTICS_CHANGE = "logistics_change"
    EMERGENCY_DECISION = "emergency_decision"
    MISSION_COMPLETION = "mission_completion"

class VoteChoice(Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

@dataclass
class Proposal:
    proposal_id: str
    dao_id: str
    proposer_id: str
    proposal_type: ProposalType
    title: str
    description: str
    requested_amount: Optional[float]
    target_recipient: Optional[str]
    created_at: datetime
    voting_ends_at: datetime
    status: str = "active"  # active, passed, failed, executed
    votes: Dict[str, Dict] = None  # voter_id -> {choice, voting_power, timestamp}
    
    def __post_init__(self):
        if self.votes is None:
            self.votes = {}

class GovernanceSystem:
    """
    Governance System untuk Event DAO
    Sesuai PDF: "Partisipan mendapat token voting untuk menentukan alokasi bantuan"
    "Semua keputusan dibuat melalui voting transparan"
    """
    
    def __init__(self):
        self.active_proposals: Dict[str, Proposal] = {}
        self.voting_power_rules = self._setup_voting_rules()
        self.proposal_requirements = self._setup_proposal_requirements()
        self.logger = logging.getLogger("aegis.governance")
    
    def _setup_voting_rules(self) -> Dict:
        """Setup voting power rules"""
        return {
            "donor": {
                "base_power": 1,
                "donation_multiplier": 0.1,  # +0.1 per $1000 donated
                "max_power": 10
            },
            "volunteer": {
                "base_power": 2,  # Volunteers get more base power
                "response_time_bonus": 1,  # +1 if arrived <4 hours
                "max_power": 5
            },
            "ngo": {
                "base_power": 3,  # NGOs get highest base power
                "reputation_multiplier": 0.5,
                "max_power": 8
            },
            "validator": {
                "base_power": 1,
                "accuracy_multiplier": 2,  # +2 for high accuracy
                "max_power": 4
            }
        }
    
    def _setup_proposal_requirements(self) -> Dict:
        """Setup proposal requirements"""
        return {
            ProposalType.FUND_ALLOCATION: {
                "min_voting_power": 5,  # Minimum voting power to propose
                "passing_threshold": 0.6,  # 60% yes votes needed
                "min_participation": 0.3,  # 30% of eligible voters must participate
                "voting_period_hours": 6
            },
            ProposalType.RESOURCE_REQUEST: {
                "min_voting_power": 2,
                "passing_threshold": 0.5,  # 50% yes votes needed
                "min_participation": 0.25,
                "voting_period_hours": 4
            },
            ProposalType.LOGISTICS_CHANGE: {
                "min_voting_power": 3,
                "passing_threshold": 0.55,
                "min_participation": 0.3,
                "voting_period_hours": 2
            },
            ProposalType.EMERGENCY_DECISION: {
                "min_voting_power": 1,
                "passing_threshold": 0.51,
                "min_participation": 0.2,
                "voting_period_hours": 1  # Emergency = fast voting
            },
            ProposalType.MISSION_COMPLETION: {
                "min_voting_power": 2,
                "passing_threshold": 0.66,  # 66% for mission completion
                "min_participation": 0.4,
                "voting_period_hours": 12
            }
        }
    
    async def create_proposal(self, dao_id: str, proposer_id: str, proposal_type: ProposalType, 
                            title: str, description: str, requested_amount: Optional[float] = None,
                            target_recipient: Optional[str] = None) -> Optional[Proposal]:
        """Create new proposal for voting"""
        
        # Check if proposer has enough voting power
        voting_power = await self._calculate_voting_power(proposer_id, dao_id)
        min_power = self.proposal_requirements[proposal_type]["min_voting_power"]
        
        if voting_power < min_power:
            self.logger.warning(f"Insufficient voting power: {voting_power} < {min_power}")
            return None
        
        # Create proposal
        proposal_id = f"prop_{dao_id}_{len(self.active_proposals)}"
        voting_hours = self.proposal_requirements[proposal_type]["voting_period_hours"]
        
        proposal = Proposal(
            proposal_id=proposal_id,
            dao_id=dao_id,
            proposer_id=proposer_id,
            proposal_type=proposal_type,
            title=title,
            description=description,
            requested_amount=requested_amount,
            target_recipient=target_recipient,
            created_at=datetime.now(),
            voting_ends_at=datetime.now() + timedelta(hours=voting_hours)
        )
        
        self.active_proposals[proposal_id] = proposal
        
        self.logger.info(f"📋 New proposal created: {proposal_id}")
        self.logger.info(f"   Type: {proposal_type.value}")
        self.logger.info(f"   Amount: ${requested_amount:,}" if requested_amount else "")
        self.logger.info(f"   Voting ends: {proposal.voting_ends_at}")
        
        # Auto-broadcast to DAO members
        await self._broadcast_proposal(proposal)
        
        return proposal
    
    async def cast_vote(self, proposal_id: str, voter_id: str, choice: VoteChoice, 
                       dao_id: str) -> bool:
        """Cast vote on proposal"""
        
        if proposal_id not in self.active_proposals:
            return False
            
        proposal = self.active_proposals[proposal_id]
        
        # Check if voting is still open
        if datetime.now() > proposal.voting_ends_at:
            return False
            
        # Calculate voter's voting power
        voting_power = await self._calculate_voting_power(voter_id, dao_id)
        
        # Record vote
        proposal.votes[voter_id] = {
            "choice": choice.value,
            "voting_power": voting_power,
            "timestamp": datetime.now()
        }
        
        self.logger.info(f"🗳️ Vote cast: {voter_id} -> {choice.value} (power: {voting_power})")
        
        # Check if proposal can be finalized early
        await self._check_early_finalization(proposal)
        
        return True
    
    async def _calculate_voting_power(self, participant_id: str, dao_id: str) -> float:
        """Calculate voting power based on participant role and contribution"""
        
        # Get participant info (mock implementation)
        participant = await self._get_participant_info(participant_id, dao_id)
        
        if not participant:
            return 0
            
        role = participant.get("role", "donor")
        rules = self.voting_power_rules.get(role, self.voting_power_rules["donor"])
        
        base_power = rules["base_power"]
        max_power = rules["max_power"]
        
        # Calculate role-specific bonuses
        if role == "donor":
            donation_amount = participant.get("donation_amount", 0)
            bonus = (donation_amount / 1000) * rules["donation_multiplier"]
            
        elif role == "volunteer":
            arrival_time = participant.get("arrival_time", 10)  # hours
            bonus = rules["response_time_bonus"] if arrival_time <= 4 else 0
            
        elif role == "ngo":
            reputation = participant.get("reputation_score", 0)
            bonus = reputation * rules["reputation_multiplier"]
            
        elif role == "validator":
            accuracy = participant.get("accuracy", 0)
            bonus = rules["accuracy_multiplier"] if accuracy >= 0.9 else 0
            
        else:
            bonus = 0
        
        total_power = min(base_power + bonus, max_power)
        return round(total_power, 2)
    
    async def finalize_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Finalize proposal voting and determine result"""
        
        if proposal_id not in self.active_proposals:
            return None
            
        proposal = self.active_proposals[proposal_id]
        
        # Check if voting period ended
        if datetime.now() < proposal.voting_ends_at:
            return None
            
        # Calculate results
        results = await self._calculate_vote_results(proposal)
        
        # Determine if proposal passes
        requirements = self.proposal_requirements[proposal.proposal_type]
        
        passed = (results["yes_percentage"] >= requirements["passing_threshold"] and
                 results["participation_rate"] >= requirements["min_participation"])
        
        proposal.status = "passed" if passed else "failed"
        
        result = {
            "proposal_id": proposal_id,
            "status": proposal.status,
            "results": results,
            "finalized_at": datetime.now()
        }
        
        self.logger.info(f"📊 Proposal {proposal_id} finalized: {proposal.status.upper()}")
        self.logger.info(f"   Yes: {results['yes_percentage']:.1%}")
        self.logger.info(f"   Participation: {results['participation_rate']:.1%}")
        
        # Execute if passed
        if passed:
            await self._execute_proposal(proposal)
        
        return result
    
    async def _calculate_vote_results(self, proposal: Proposal) -> Dict:
        """Calculate voting results"""
        
        total_yes_power = sum(vote["voting_power"] for vote in proposal.votes.values() 
                             if vote["choice"] == "yes")
        total_no_power = sum(vote["voting_power"] for vote in proposal.votes.values() 
                            if vote["choice"] == "no")
        total_abstain_power = sum(vote["voting_power"] for vote in proposal.votes.values() 
                                 if vote["choice"] == "abstain")
        
        total_voting_power = total_yes_power + total_no_power + total_abstain_power
        eligible_voting_power = await self._get_total_eligible_voting_power(proposal.dao_id)
        
        return {
            "total_votes": len(proposal.votes),
            "yes_power": total_yes_power,
            "no_power": total_no_power,
            "abstain_power": total_abstain_power,
            "total_voting_power": total_voting_power,
            "eligible_voting_power": eligible_voting_power,
            "yes_percentage": total_yes_power / total_voting_power if total_voting_power > 0 else 0,
            "participation_rate": total_voting_power / eligible_voting_power if eligible_voting_power > 0 else 0
        }
    
    async def _execute_proposal(self, proposal: Proposal):
        """Execute passed proposal"""
        
        if proposal.proposal_type == ProposalType.FUND_ALLOCATION:
            await self._execute_fund_allocation(proposal)
            
        elif proposal.proposal_type == ProposalType.RESOURCE_REQUEST:
            await self._execute_resource_request(proposal)
            
        elif proposal.proposal_type == ProposalType.MISSION_COMPLETION:
            await self._execute_mission_completion(proposal)
            
        proposal.status = "executed"
        self.logger.info(f"✅ Executed proposal: {proposal.proposal_id}")
    
    async def _execute_fund_allocation(self, proposal: Proposal):
        """Execute fund allocation proposal"""
        self.logger.info(f"💰 Allocating ${proposal.requested_amount:,} to {proposal.target_recipient}")
        # In real implementation: transfer funds via smart contract
    
    async def _execute_resource_request(self, proposal: Proposal):
        """Execute resource request proposal"""
        self.logger.info(f"📦 Approving resource request: {proposal.description}")
        # In real implementation: trigger resource allocation
    
    async def _execute_mission_completion(self, proposal: Proposal):
        """Execute mission completion proposal"""
        self.logger.info(f"🎯 Mission completion approved for DAO {proposal.dao_id}")
        # In real implementation: trigger SBT minting and DAO closure
    
    async def _check_early_finalization(self, proposal: Proposal):
        """Check if proposal can be finalized early (unanimous vote)"""
        
        if len(proposal.votes) < 3:  # Need minimum votes
            return
            
        # Check for unanimous yes votes
        all_yes = all(vote["choice"] == "yes" for vote in proposal.votes.values())
        total_power = sum(vote["voting_power"] for vote in proposal.votes.values())
        eligible_power = await self._get_total_eligible_voting_power(proposal.dao_id)
        
        participation = total_power / eligible_power if eligible_power > 0 else 0
        
        if all_yes and participation >= 0.5:  # 50% participation + unanimous
            self.logger.info(f"🚀 Early finalization: {proposal.proposal_id} (unanimous)")
            await self.finalize_proposal(proposal.proposal_id)
    
    async def _get_participant_info(self, participant_id: str, dao_id: str) -> Optional[Dict]:
        """Get participant information (mock)"""
        # Mock participant data
        mock_participants = {
            "vol_001": {"role": "volunteer", "arrival_time": 3.5, "reputation_score": 4.2},
            "ngo_001": {"role": "ngo", "reputation_score": 4.8},
            "donor_001": {"role": "donor", "donation_amount": 50000},
            "validator_001": {"role": "validator", "accuracy": 0.95}
        }
        return mock_participants.get(participant_id)
    
    async def _get_total_eligible_voting_power(self, dao_id: str) -> float:
        """Calculate total eligible voting power for DAO"""
        # Mock calculation - in real implementation, query all DAO participants
        return 25.0  # Mock total eligible power
    
    async def _broadcast_proposal(self, proposal: Proposal):
        """Broadcast new proposal to all DAO members"""
        self.logger.info(f"📢 Broadcasting proposal {proposal.proposal_id} to DAO members")
        # In real implementation: send notifications to all DAO participants
    
    def get_dao_governance_stats(self, dao_id: str) -> Dict:
        """Get governance statistics for DAO"""
        dao_proposals = [p for p in self.active_proposals.values() if p.dao_id == dao_id]
        
        total_proposals = len(dao_proposals)
        passed_proposals = len([p for p in dao_proposals if p.status == "passed"])
        active_proposals = len([p for p in dao_proposals if p.status == "active"])
        
        return {
            "dao_id": dao_id,
            "total_proposals": total_proposals,
            "passed_proposals": passed_proposals, 
            "active_proposals": active_proposals,
            "pass_rate": passed_proposals / total_proposals if total_proposals > 0 else 0,
            "governance_activity": "high" if total_proposals > 5 else "medium" if total_proposals > 2 else "low"
        }