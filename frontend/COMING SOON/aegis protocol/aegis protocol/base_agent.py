# base_agent.py
# Base classes and data structures for Aegis Protocol

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import logging

# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================

class AgentType(Enum):
    DISASTER_PARSER = "disaster_parser"
    VALIDATOR = "validator"
    CONSENSUS_MANAGER = "consensus_manager"
    EVENT_FACTORY = "event_factory"
    COMMUNICATIONS = "communications"
    LOGISTICS_AI = "logistics_ai"
    REPUTATION_MANAGER = "reputation_manager"

class DisasterType(Enum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    TSUNAMI = "tsunami"
    VOLCANIC = "volcanic"
    LANDSLIDE = "landslide"

class AlertLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class DisasterEvent:
    """Core disaster event data structure"""
    event_id: str
    disaster_type: DisasterType
    location: Dict[str, float]  # {"lat": -6.2088, "lon": 106.8456}
    severity: AlertLevel
    timestamp: datetime
    confidence_score: float
    data_sources: List[str]
    affected_population: Optional[int] = None
    estimated_damage: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """AI Validator result structure"""
    validator_id: str
    event_id: str
    confidence: float
    stake_amount: float
    prediction: bool  # True = disaster confirmed, False = false alarm
    reasoning: str
    timestamp: datetime

@dataclass
class EventDAO:
    """Event DAO structure for disaster response"""
    dao_id: str
    event_id: str
    status: str  # "active", "funded", "completed", "archived"
    treasury_balance: float
    participants: List[str]
    proposals: List[Dict]
    created_at: datetime
    resolution_target: Optional[datetime] = None

# ============================================================================
# BASE AGENT CLASS
# ============================================================================

class BaseAgent:
    """Base class for all Aegis Protocol agents"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, asi_interface=None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.asi_interface = asi_interface
        self.stake_balance = 0.0
        self.reputation_score = 0.0
        self.is_active = True
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger(f"aegis.{self.agent_type.value}.{self.agent_id}")
        return logger
    
    async def process(self, data: Any) -> Any:
        """Override in subclasses"""
        raise NotImplementedError
    
    async def stake_tokens(self, amount: float) -> bool:
        """Stake tokens for validation"""
        if amount <= self.stake_balance:
            self.stake_balance -= amount
            return True
        return False
    
    async def receive_reward(self, amount: float):
        """Receive reward for correct validation"""
        self.stake_balance += amount
        self.reputation_score += 0.1
    
    async def penalty(self, amount: float):
        """Penalty for incorrect validation"""
        self.stake_balance = max(0, self.stake_balance - amount)
        self.reputation_score = max(0, self.reputation_score - 0.2)