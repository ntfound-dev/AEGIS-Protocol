# communications.py
# Communications and notification agent

from typing import List, Dict
from base_agent import BaseAgent, AgentType, EventDAO

class CommunicationsAgent(BaseAgent):
    """Handles notifications and public communications"""
    
    def __init__(self, agent_id: str, notification_channels: List[str]):
        super().__init__(agent_id, AgentType.COMMUNICATIONS)
        self.notification_channels = notification_channels
        self.volunteer_database = {}  # volunteer_id -> contact_info
        self.ngo_database = {}        # ngo_id -> contact_info
    
    async def process(self, event_dao: EventDAO) -> Dict[str, int]:
        """Send notifications about new disaster event"""
        notification_stats = {"whatsapp": 0, "email": 0, "push": 0, "sms": 0}
        
        # Get event details (in real implementation, fetch from event registry)
        event_details = await self._get_event_details(event_dao.event_id)
        
        # Notify volunteers in affected area
        nearby_volunteers = await self._find_nearby_volunteers(event_details["location"])
        for volunteer in nearby_volunteers:
            await self._send_whatsapp_notification(volunteer, event_details, event_dao)
            notification_stats["whatsapp"] += 1
        
        # Notify registered NGOs
        relevant_ngos = await self._find_relevant_ngos(event_details["disaster_type"])
        for ngo in relevant_ngos:
            await self._send_email_notification(ngo, event_details, event_dao)
            notification_stats["email"] += 1
        
        # Broadcast to public channels
        await self._broadcast_public_alert(event_details, event_dao)
        
        self.logger.info(f"Sent {sum(notification_stats.values())} notifications for {event_dao.dao_id}")
        return notification_stats
    
    async def _send_whatsapp_notification(self, volunteer: Dict, event: Dict, dao: EventDAO):
        """Send WhatsApp notification to volunteer"""
        message = f"""
🚨 AEGIS PROTOCOL ALERT 🚨

Disaster Type: {event["disaster_type"]}
Location: {event["location_name"]}
Severity: {event["severity"]}

Event DAO: {dao.dao_id}
Available Funds: ${dao.treasury_balance:,.0f}

Your help is needed! Join the response effort:
- Register participation in Event DAO
- Coordinate with other volunteers
- Receive AI-optimized logistics routes

Response Time Target: <4 hours
        """
        # Implement WhatsApp Cloud API call here
        self.logger.info(f"WhatsApp sent to volunteer {volunteer['id']}")
    
    async def _find_nearby_volunteers(self, location: Dict) -> List[Dict]:
        """Find volunteers within affected radius"""
        # Implement geospatial query
        return [
            {"id": "vol_001", "name": "Ahmad", "distance": 2.5},
            {"id": "vol_002", "name": "Sari", "distance": 3.1},
            {"id": "vol_003", "name": "Budi", "distance": 4.2}
        ]
    
    async def _get_event_details(self, event_id: str) -> Dict:
        """Get event details for notifications"""
        # Mock event details
        return {
            "disaster_type": "Earthquake",
            "location": {"lat": -6.2088, "lon": 106.8456},
            "location_name": "Jakarta Pusat",
            "severity": "HIGH",
            "estimated_affected": 50000
        }
    
    async def _find_relevant_ngos(self, disaster_type: str) -> List[Dict]:
        """Find NGOs specialized in disaster type"""
        return [
            {"id": "ngo_001", "name": "PMI Jakarta", "specialty": "emergency_response"},
            {"id": "ngo_002", "name": "ACT Foundation", "specialty": "disaster_relief"}
        ]
    
    async def _send_email_notification(self, ngo: Dict, event: Dict, dao: EventDAO):
        """Send email notification to NGO"""
        self.logger.info(f"Email sent to NGO {ngo['id']}")
    
    async def _broadcast_public_alert(self, event: Dict, dao: EventDAO):
        """Broadcast public alert through various channels"""
        self.logger.info(f"Public alert broadcasted for {dao.dao_id}")