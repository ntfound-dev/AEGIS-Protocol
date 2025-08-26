# disaster_parsers.py
# Disaster detection and parsing agents

from typing import Dict, Any, Optional, Callable, List
import hashlib
from datetime import datetime

from base_agent import BaseAgent, AgentType, DisasterEvent, DisasterType, AlertLevel

class DisasterParserAgent(BaseAgent):
    """Parses raw disaster data from multiple sources"""
    
    def __init__(self, agent_id: str, data_sources: List[str]):
        super().__init__(agent_id, AgentType.DISASTER_PARSER)
        self.data_sources = data_sources
        self.parsing_rules = self._load_parsing_rules()
    
    def _load_parsing_rules(self) -> Dict[str, Callable]:
        """Define parsing rules for different data sources"""
        return {
            "bmkg_earthquake": self._parse_bmkg_earthquake,
            "petabencana_flood": self._parse_petabencana_flood,
            "nasa_firms_fire": self._parse_nasa_firms,
            "social_media": self._parse_social_signals
        }
    
    async def process(self, raw_data: Dict[str, Any]) -> Optional[DisasterEvent]:
        """Parse raw data into structured disaster event"""
        source_type = raw_data.get("source_type")
        
        if source_type not in self.parsing_rules:
            return None
            
        try:
            # Parse using specific rule
            parsed_event = await self.parsing_rules[source_type](raw_data)
            
            # Generate unique event ID
            event_hash = hashlib.md5(
                f"{parsed_event.disaster_type.value}_{parsed_event.location}_{parsed_event.timestamp}".encode()
            ).hexdigest()
            parsed_event.event_id = f"evt_{event_hash[:12]}"
            
            self.logger.info(f"Parsed disaster event: {parsed_event.event_id}")
            return parsed_event
            
        except Exception as e:
            self.logger.error(f"Failed to parse data: {e}")
            return None
    
    async def _parse_bmkg_earthquake(self, data: Dict) -> DisasterEvent:
        """Parse BMKG earthquake data"""
        return DisasterEvent(
            event_id="",  # Will be set in process()
            disaster_type=DisasterType.EARTHQUAKE,
            location={
                "lat": float(data["gempa"]["Lintang"]), 
                "lon": float(data["gempa"]["Bujur"])
            },
            severity=self._map_magnitude_to_severity(float(data["gempa"]["Magnitude"])),
            timestamp=datetime.now(),
            confidence_score=0.95,  # BMKG is highly reliable
            data_sources=["bmkg_autogempa"],
            metadata={
                "magnitude": data["gempa"]["Magnitude"],
                "depth": data["gempa"]["Kedalaman"],
                "region": data["gempa"]["Wilayah"]
            }
        )
    
    async def _parse_petabencana_flood(self, data: Dict) -> DisasterEvent:
        """Parse PetaBencana flood data"""
        return DisasterEvent(
            event_id="",
            disaster_type=DisasterType.FLOOD,
            location={
                "lat": data["geometry"]["coordinates"][1],
                "lon": data["geometry"]["coordinates"][0]
            },
            severity=AlertLevel.HIGH,
            timestamp=datetime.now(),
            confidence_score=0.85,
            data_sources=["petabencana"],
            metadata=data["properties"]
        )
    
    async def _parse_nasa_firms(self, data: Dict) -> DisasterEvent:
        """Parse NASA FIRMS fire data"""
        return DisasterEvent(
            event_id="",
            disaster_type=DisasterType.FIRE,
            location={"lat": data["latitude"], "lon": data["longitude"]},
            severity=self._map_confidence_to_severity(data["confidence"]),
            timestamp=datetime.now(),
            confidence_score=data["confidence"] / 100.0,
            data_sources=["nasa_firms"],
            metadata={
                "brightness": data["brightness"],
                "frp": data["frp"]  # Fire Radiative Power
            }
        )
    
    async def _parse_social_signals(self, data: Dict) -> DisasterEvent:
        """Parse social media signals"""
        return DisasterEvent(
            event_id="",
            disaster_type=DisasterType(data["predicted_type"]),
            location=data["estimated_location"],
            severity=AlertLevel.MEDIUM,
            timestamp=datetime.now(),
            confidence_score=data["ai_confidence"],
            data_sources=["social_media"],
            metadata={
                "post_count": data["post_count"],
                "sentiment_score": data["sentiment"]
            }
        )
    
    def _map_magnitude_to_severity(self, magnitude: float) -> AlertLevel:
        """Map earthquake magnitude to alert level"""
        if magnitude >= 7.0: return AlertLevel.EMERGENCY
        elif magnitude >= 6.0: return AlertLevel.CRITICAL
        elif magnitude >= 5.0: return AlertLevel.HIGH
        elif magnitude >= 4.0: return AlertLevel.MEDIUM
        else: return AlertLevel.LOW
    
    def _map_confidence_to_severity(self, confidence: float) -> AlertLevel:
        """Map confidence score to alert level"""
        if confidence >= 90: return AlertLevel.CRITICAL
        elif confidence >= 70: return AlertLevel.HIGH
        elif confidence >= 50: return AlertLevel.MEDIUM
        else: return AlertLevel.LOW