# orchestrator.py
# Main orchestrator that coordinates all agents

import asyncio
from typing import Dict, Optional, Any, List
import logging

from datetime import datetime

from base_agent import DisasterEvent, ValidationResult, DisasterType
from disaster_parsers import DisasterParserAgent
from validators import ValidatorAgent, ConsensusManagerAgent
from event_dao import EventFactoryAgent
from communications import CommunicationsAgent
from logistics import LogisticsAIAgent
from reputation import ReputationManagerAgent

class AegisOrchestrator:
    """Main orchestrator that coordinates all agents"""
    
    def __init__(self):
        self.agents = {}
        self.event_pipeline = {}  # event_id -> pipeline status
        self.active_events = {}   # event_id -> DisasterEvent
        self.logger = logging.getLogger("aegis.orchestrator")
        self.setup_agents()
    
    def setup_agents(self):
        """Initialize all agents in the system"""
        
        # Disaster Parser Agents
        self.agents["bmkg_parser"] = DisasterParserAgent(
            "bmkg_parser", ["bmkg_earthquake"]
        )
        self.agents["flood_parser"] = DisasterParserAgent(
            "flood_parser", ["petabencana_flood"]
        )
        self.agents["fire_parser"] = DisasterParserAgent(
            "fire_parser", ["nasa_firms_fire"]
        )
        self.agents["social_parser"] = DisasterParserAgent(
            "social_parser", ["social_media"]
        )
        
        # Validator Agents (Different AI Models)
        self.agents["earthquake_validator"] = ValidatorAgent(
            "earthquake_validator", "earthquake_specialist", 10000.0
        )
        self.agents["multimodal_validator"] = ValidatorAgent(
            "multimodal_validator", "multi_modal_detector", 8000.0
        )
        self.agents["social_validator"] = ValidatorAgent(
            "social_validator", "social_signal_analyzer", 5000.0
        )
        
        # Core System Agents
        self.agents["consensus_manager"] = ConsensusManagerAgent(
            "consensus_manager", 0.7
        )
        self.agents["event_factory"] = EventFactoryAgent(
            "event_factory", 2_000_000
        )
        self.agents["communications"] = CommunicationsAgent(
            "communications", ["whatsapp", "email", "push", "sms"]
        )
        self.agents["logistics_ai"] = LogisticsAIAgent("logistics_ai")
        self.agents["reputation_manager"] = ReputationManagerAgent("reputation_manager")
        
        self.logger.info("All agents initialized successfully")
    
    async def process_raw_data(self, raw_data: Dict[str, Any]) -> Optional[str]:
        """Main entry point for processing incoming disaster data"""
        
        # Step 1: Parse raw data into structured event
        disaster_event = await self._parse_disaster_data(raw_data)
        if not disaster_event:
            return None
        
        self.active_events[disaster_event.event_id] = disaster_event
        self.event_pipeline[disaster_event.event_id] = "parsing_complete"
        
        # Step 2: Start validation process
        await self._initiate_validation_process(disaster_event)
        
        return disaster_event.event_id
    
    async def _parse_disaster_data(self, raw_data: Dict[str, Any]) -> Optional[DisasterEvent]:
        """Route raw data to appropriate parser agent"""
        source_type = raw_data.get("source_type")
        
        # Route to appropriate parser
        if source_type == "bmkg_earthquake":
            return await self.agents["bmkg_parser"].process(raw_data)
        elif source_type == "petabencana_flood":
            return await self.agents["flood_parser"].process(raw_data)
        elif source_type == "nasa_firms_fire":
            return await self.agents["fire_parser"].process(raw_data)
        elif source_type == "social_media":
            return await self.agents["social_parser"].process(raw_data)
        else:
            self.logger.warning(f"Unknown source type: {source_type}")
            return None
    
    async def _initiate_validation_process(self, event: DisasterEvent):
        """Start the AI validation process"""
        self.event_pipeline[event.event_id] = "validation_started"
        
        # Send event to all relevant validators
        validation_tasks = []
        
        # Always use multimodal validator
        validation_tasks.append(
            self.agents["multimodal_validator"].process(event)
        )
        
        # Use specialized validators based on disaster type
        if event.disaster_type == DisasterType.EARTHQUAKE:
            validation_tasks.append(
                self.agents["earthquake_validator"].process(event)
            )
        
        # Use social validator if social media data is available
        if "social_media" in event.data_sources:
            validation_tasks.append(
                self.agents["social_validator"].process(event)
            )
        
        # Run validations concurrently
        validation_results = await asyncio.gather(*validation_tasks)
        
        # Send results to consensus manager
        for result in validation_results:
            await self._process_validation_result(result)
    
    async def _process_validation_result(self, validation_result: ValidationResult):
        """Process individual validation result"""
        consensus_result = await self.agents["consensus_manager"].process(validation_result)
        
        if consensus_result:
            event_id = consensus_result["event_id"]
            self.event_pipeline[event_id] = "consensus_reached"
            
            # If disaster confirmed, create Event DAO
            if consensus_result["decision"]:
                await self._create_event_dao(consensus_result)
            else:
                self.event_pipeline[event_id] = "false_alarm"
                self.logger.info(f"Event {event_id} determined to be false alarm")
    
    async def _create_event_dao(self, consensus_result: Dict):
        """Create Event DAO and initiate response"""
        event_id = consensus_result["event_id"]
        
        # Create DAO through event factory
        event_dao = await self.agents["event_factory"].process(consensus_result)
        
        if event_dao:
            self.event_pipeline[event_id] = "dao_created"
            
            # Trigger communications
            await self._initiate_communications(event_dao)
            
            # Generate logistics plan
            await self._generate_logistics_plan(event_dao)
    
    async def _initiate_communications(self, event_dao):
        """Initiate emergency communications"""
        notification_stats = await self.agents["communications"].process(event_dao)
        
        self.event_pipeline[event_dao.event_id] = "notifications_sent"
        self.logger.info(f"Communications initiated for {event_dao.dao_id}: {notification_stats}")
    
    async def _generate_logistics_plan(self, event_dao):
        """Generate AI logistics plan"""
        event = self.active_events[event_dao.event_id]
        
        dao_request = {
            "event_id": event_dao.event_id,
            "event_location": event.location,
            "required_supplies": ["medical_kits", "food", "water", "blankets"],
            "volunteers": [],  # Will be populated as volunteers register
            "evacuation_needed": event.severity.value >= 4
        }
        
        logistics_plan = await self.agents["logistics_ai"].process(dao_request)
        self.event_pipeline[event_dao.event_id] = "logistics_planned"
        
        self.logger.info(f"Logistics plan generated for {event_dao.dao_id}")
    
    async def complete_mission(self, event_id: str, outcome: str, participants: List[Dict]):
        """Complete disaster response mission and mint SBTs"""
        if event_id not in self.event_pipeline:
            return False
        
        event_completion = {
            "event_id": event_id,
            "outcome": outcome,  # "success", "partial", "failed"
            "participants": participants,
            "completion_time": datetime.now()
        }
        
        # Process through reputation manager
        minted_sbts = await self.agents["reputation_manager"].process(event_completion)
        
        self.event_pipeline[event_id] = "mission_completed"
        self.logger.info(f"Mission completed for {event_id}: {len(minted_sbts)} SBTs minted")
        
        return True
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        active_events = len([e for e in self.event_pipeline.values() 
                           if e not in ["mission_completed", "false_alarm"]])
        
        total_stake = sum([agent.stake_balance for agent in self.agents.values() 
                          if hasattr(agent, 'stake_balance')])
        
        vault_balance = self.agents["event_factory"].parametric_vault_balance
        
        return {
            "system_status": "operational",
            "active_events": active_events,
            "total_validator_stake": total_stake,
            "vault_balance": vault_balance,
            "agent_count": len(self.agents),
            "uptime": "99.8%"
        }