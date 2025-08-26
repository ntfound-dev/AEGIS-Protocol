# simulator.py
# Simulation and testing framework (FIXED VERSION)

import asyncio
import time
from typing import List, Dict

class DisasterSimulator:
    """Simulator for testing agent performance"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.simulation_scenarios = self._load_scenarios()
    
    def _load_scenarios(self) -> List[Dict]:
        """Load disaster simulation scenarios"""
        return [
            {
                "name": "Jakarta_Flood_2025",
                "disaster_type": "flood",
                "location": {"lat": -6.2088, "lon": 106.8456},
                "severity": "high",
                "duration": "6_hours",
                "affected_population": 50000,
                "data_sources": ["petabencana", "social_media", "satellite"]
            },
            {
                "name": "Cianjur_Earthquake_M6.2",
                "disaster_type": "earthquake",
                "location": {"lat": -6.8, "lon": 107.1},
                "severity": "critical",
                "duration": "instant",
                "affected_population": 25000,
                "data_sources": ["bmkg", "social_media", "seismic_network"]
            },
            {
                "name": "Kalimantan_Forest_Fire",
                "disaster_type": "fire",
                "location": {"lat": -2.5, "lon": 118.0},
                "severity": "emergency",
                "duration": "72_hours",
                "affected_population": 15000,
                "data_sources": ["nasa_firms", "satellite", "air_quality"]
            }
        ]
    
    async def run_simulation(self, scenario_name: str) -> Dict:
        """Run disaster simulation"""
        scenario = next((s for s in self.simulation_scenarios if s["name"] == scenario_name), None)
        if not scenario:
            raise ValueError(f"Scenario {scenario_name} not found")
        
        print(f"🎯 Starting simulation: {scenario_name}")
        start_time = time.time()
        
        # Generate synthetic data
        raw_data = self._generate_synthetic_data(scenario)
        
        # Process through orchestrator
        event_id = await self.orchestrator.process_raw_data(raw_data)
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Simulate mission completion with FIXED participants data
        participants = self._generate_mock_participants()
        await self.orchestrator.complete_mission(event_id, "success", participants)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Collect results
        results = {
            "scenario": scenario_name,
            "event_id": event_id,
            "processing_time_seconds": processing_time,
            "pipeline_status": self.orchestrator.event_pipeline.get(event_id, "unknown"),
            "system_status": self.orchestrator.get_system_status(),
            "success": True
        }
        
        print(f"✅ Simulation completed in {processing_time:.2f}s")
        return results
    
    def _generate_synthetic_data(self, scenario: Dict) -> Dict:
        """Generate synthetic disaster data for testing"""
        if scenario["disaster_type"] == "earthquake":
            return {
                "source_type": "bmkg_earthquake",
                "gempa": {
                    "Tanggal": "25 Des 2024",
                    "Jam": "14:30:15 WIB", 
                    "Magnitude": "6.2",
                    "Kedalaman": "10 km",
                    "Lintang": str(scenario["location"]["lat"]),
                    "Bujur": str(scenario["location"]["lon"]),
                    "Wilayah": "Cianjur, Jawa Barat"
                }
            }
        elif scenario["disaster_type"] == "flood":
            return {
                "source_type": "petabencana_flood",
                "geometry": {
                    "type": "Point",
                    "coordinates": [scenario["location"]["lon"], scenario["location"]["lat"]]
                },
                "properties": {
                    "state": "flood",
                    "level": 150,
                    "area": "Jakarta Pusat"
                }
            }
        elif scenario["disaster_type"] == "fire":
            return {
                "source_type": "nasa_firms_fire",
                "latitude": scenario["location"]["lat"],
                "longitude": scenario["location"]["lon"],
                "brightness": 345.2,
                "confidence": 85,
                "frp": 12.5
            }
    
    def _generate_mock_participants(self) -> List[Dict]:
        """Generate mock participants for testing - FIXED VERSION"""
        return [
            {
                "id": "vol_001",
                "role": "volunteer",
                "arrival_time": 3.5,  # hours - Fixed: now properly defined as float
                "contribution": "first_aid",
                "donation_percentile": 0.0  # Fixed: now properly defined as float
            },
            {
                "id": "ngo_001", 
                "role": "ngo",
                "arrival_time": 2.0,  # Fixed: now properly defined as float
                "contribution": "coordination",
                "donation_percentile": 0.0  # Fixed: now properly defined as float
            },
            {
                "id": "donor_001",
                "role": "donor",
                "arrival_time": None,  # OK to be None for donors
                "contribution": "funding",
                "donation_percentile": 99.2  # Fixed: now properly defined as float
            },
            {
                "id": "validator_001",
                "role": "validator",
                "arrival_time": 1.0,  # Fixed: added proper arrival time
                "contribution": "validation",
                "donation_percentile": 0.0,  # Fixed: added proper value
                "accuracy": 0.96  # Fixed: added accuracy for validator hero SBT
            }
        ]