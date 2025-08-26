# event_dao.py
# Event DAO factory and management

from typing import Dict, Optional
from datetime import datetime

from base_agent import BaseAgent, AgentType, EventDAO

class EventFactoryAgent(BaseAgent):
    """Creates Event DAOs when disasters are confirmed"""
    
    def __init__(self, agent_id: str, initial_funding: float = 2_000_000):
        super().__init__(agent_id, AgentType.EVENT_FACTORY)
        self.initial_funding = initial_funding
        self.active_daos = {}  # dao_id -> EventDAO
        self.parametric_vault_balance = 10_000_000  # $10M vault
    
    async def process(self, consensus_result: Dict) -> Optional[EventDAO]:
        """Create Event DAO when consensus confirms disaster"""
        if not consensus_result["decision"] or consensus_result["confidence"] < 0.8:
            return None
        
        event_id = consensus_result["event_id"]
        dao_id = f"dao_{event_id}"
        
        # Check vault balance
        if self.parametric_vault_balance < self.initial_funding:
            self.logger.error("Insufficient vault balance for emergency funding")
            return None
        
        # Create Event DAO
        event_dao = EventDAO(
            dao_id=dao_id,
            event_id=event_id,
            status="active",
            treasury_balance=self.initial_funding,
            participants=[],
            proposals=[],
            created_at=datetime.now()
        )
        
        # Transfer funds from vault
        self.parametric_vault_balance -= self.initial_funding
        self.active_daos[dao_id] = event_dao
        
        self.logger.info(f"Created Event DAO {dao_id} with ${self.initial_funding:,.0f} initial funding")
        
        # Trigger communications agent
        await self._notify_communications_agent(event_dao)
        
        return event_dao
    
    async def _notify_communications_agent(self, event_dao: EventDAO):
        """Notify communications agent to broadcast event"""
        # In real implementation, send message to communications agent
        self.logger.info(f"Notifying communications agent about {event_dao.dao_id}")