# validators.py
# Validation and consensus agents

from typing import List, Dict, Optional
from datetime import datetime
import random

from base_agent import BaseAgent, AgentType, DisasterEvent, DisasterType, ValidationResult

class ValidatorAgent(BaseAgent):
    """AI Validator that stakes tokens on disaster predictions"""
    
    def __init__(self, agent_id: str, model_type: str, stake_amount: float = 1000.0):
        super().__init__(agent_id, AgentType.VALIDATOR)
        self.model_type = model_type  # "earthquake_specialist", "flood_detector", etc.
        self.initial_stake = stake_amount
        self.stake_balance = stake_amount
        self.validation_history = []
    
    async def process(self, event: DisasterEvent) -> ValidationResult:
        """Validate disaster event and stake tokens"""
        
        # Determine stake amount based on confidence
        stake_amount = self._calculate_stake_amount(event)
        
        # Run AI validation model
        prediction, confidence, reasoning = await self._run_validation_model(event)
        
        # Create validation result
        result = ValidationResult(
            validator_id=self.agent_id,
            event_id=event.event_id,
            confidence=confidence,
            stake_amount=stake_amount,
            prediction=prediction,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
        
        # Stake tokens
        if await self.stake_tokens(stake_amount):
            self.validation_history.append(result)
            self.logger.info(f"Validated event {event.event_id}: {prediction} ({confidence:.2f})")
        
        return result
    
    async def _run_validation_model(self, event: DisasterEvent) -> tuple[bool, float, str]:
        """Run AI validation model - integrate with ASI:one here"""
        
        # Simulate different validation logic based on disaster type and model specialty
        if self.model_type == "earthquake_specialist" and event.disaster_type == DisasterType.EARTHQUAKE:
            # High confidence for earthquake events
            base_confidence = 0.9 * event.confidence_score
            prediction = event.severity.value >= 3
            reasoning = f"Earthquake specialist model: magnitude analysis, depth correlation"
            
        elif self.model_type == "multi_modal_detector":
            # General purpose validator
            base_confidence = 0.75 * event.confidence_score
            prediction = event.confidence_score > 0.7
            reasoning = f"Multi-modal analysis: {', '.join(event.data_sources)}"
            
        elif self.model_type == "social_signal_analyzer":
            # Social media specialist
            if "social_media" in event.data_sources:
                base_confidence = 0.6 * event.confidence_score
                prediction = event.confidence_score > 0.5
                reasoning = "Social media sentiment and keyword analysis"
            else:
                base_confidence = 0.3
                prediction = False
                reasoning = "No social media signals available"
        
        else:
            # Default validation
            base_confidence = 0.5 * event.confidence_score
            prediction = event.confidence_score > 0.6
            reasoning = "General validation model"
        
        # Add some noise to simulate real AI uncertainty
        final_confidence = min(1.0, max(0.0, base_confidence + random.uniform(-0.1, 0.1)))
        
        return prediction, final_confidence, reasoning
    
    def _calculate_stake_amount(self, event: DisasterEvent) -> float:
        """Calculate how much to stake based on confidence and event severity"""
        base_stake = self.initial_stake * 0.1  # 10% of initial stake
        confidence_multiplier = event.confidence_score
        severity_multiplier = event.severity.value / 5.0
        
        return min(self.stake_balance * 0.5, base_stake * confidence_multiplier * severity_multiplier)

class ConsensusManagerAgent(BaseAgent):
    """Manages consensus mechanism for disaster validation"""
    
    def __init__(self, agent_id: str, consensus_threshold: float = 0.7):
        super().__init__(agent_id, AgentType.CONSENSUS_MANAGER)
        self.consensus_threshold = consensus_threshold
        self.pending_validations = {}  # event_id -> List[ValidationResult]
        self.consensus_results = {}    # event_id -> final decision
    
    async def process(self, validation_result: ValidationResult) -> Optional[Dict]:
        """Process validation result and check for consensus"""
        event_id = validation_result.event_id
        
        # Add to pending validations
        if event_id not in self.pending_validations:
            self.pending_validations[event_id] = []
        
        self.pending_validations[event_id].append(validation_result)
        
        # Check if we have enough validations
        validations = self.pending_validations[event_id]
        if len(validations) >= 3:  # Minimum 3 validators
            consensus_result = await self._calculate_consensus(event_id, validations)
            
            if consensus_result:
                self.consensus_results[event_id] = consensus_result
                # Distribute rewards/penalties
                await self._distribute_rewards(validations, consensus_result["decision"])
                return consensus_result
        
        return None
    
    async def _calculate_consensus(self, event_id: str, validations: List[ValidationResult]) -> Optional[Dict]:
        """Calculate weighted consensus based on stakes and confidence"""
        total_stake_positive = 0
        total_stake_negative = 0
        weighted_confidence = 0
        total_weight = 0
        
        for validation in validations:
            weight = validation.stake_amount * validation.confidence
            total_weight += weight
            weighted_confidence += validation.confidence * weight
            
            if validation.prediction:
                total_stake_positive += validation.stake_amount
            else:
                total_stake_negative += validation.stake_amount
        
        # Calculate final decision
        total_stake = total_stake_positive + total_stake_negative
        positive_ratio = total_stake_positive / total_stake if total_stake > 0 else 0
        
        decision = positive_ratio >= self.consensus_threshold
        final_confidence = weighted_confidence / total_weight if total_weight > 0 else 0
        
        consensus_result = {
            "event_id": event_id,
            "decision": decision,
            "confidence": final_confidence,
            "positive_ratio": positive_ratio,
            "total_validators": len(validations),
            "timestamp": datetime.now()
        }
        
        self.logger.info(f"Consensus reached for {event_id}: {decision} ({final_confidence:.2f})")
        return consensus_result
    
    async def _distribute_rewards(self, validations: List[ValidationResult], final_decision: bool):
        """Distribute rewards to correct validators, penalties to incorrect ones"""
        for validation in validations:
            # Reward correct predictions
            if validation.prediction == final_decision:
                reward = validation.stake_amount * 1.2  # 20% profit
                # In real implementation, call validator.receive_reward(reward)
                self.logger.info(f"Rewarding validator {validation.validator_id}: +{reward}")
            else:
                # Penalty for incorrect predictions (lose stake)
                penalty = validation.stake_amount
                self.logger.info(f"Penalty for validator {validation.validator_id}: -{penalty}")