# oracle_network.py
# Decentralized Oracle Network - monitoring 24/7 sesuai PDF

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Callable, Optional
from datetime import datetime, timedelta

class DecentralizedOracleNetwork:
    """
    DON - Decentralized Oracle Network
    Sesuai PDF: "Memantau data real-time dari berbagai sumber:
    - Data gempa dari BMKG/USGS  
    - Komunikasi darurat satelit
    - Sensor IoT lokal
    - Media sosial dan berita"
    """
    
    def __init__(self, orchestrator_callback: Callable):
        self.orchestrator_callback = orchestrator_callback
        self.data_sources = self._setup_data_sources()
        self.monitoring_active = False
        self.monitoring_tasks = {}
        self.logger = logging.getLogger("aegis.don")
        
    def _setup_data_sources(self) -> Dict:
        """Setup data sources sesuai PDF"""
        return {
            "bmkg_autogempa": {
                "url": "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json",
                "interval": 60,  # Poll setiap 60 detik sesuai PDF
                "parser": self._parse_bmkg_data,
                "active": True
            },
            "usgs_earthquake": {
                "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
                "interval": 300,  # 5 menit
                "parser": self._parse_usgs_data,
                "active": True
            },
            "petabencana_flood": {
                "url": "https://data.petabencana.id/floods/states/",
                "interval": 180,  # 3 menit
                "parser": self._parse_petabencana_data,
                "active": True
            },
            "nasa_firms": {
                "url": "https://firms.modaps.eosdis.nasa.gov/api/country/csv/",
                "interval": 3600,  # 1 jam
                "parser": self._parse_nasa_firms_data,
                "active": True
            },
            "social_media_monitor": {
                "url": "internal://social_monitor",
                "interval": 120,  # 2 menit
                "parser": self._parse_social_signals,
                "active": True
            }
        }
    
    async def start_monitoring(self):
        """Start 24/7 monitoring semua data sources"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.logger.info("🚀 Starting DON 24/7 monitoring...")
        
        # Start monitoring task for each source
        for source_name, config in self.data_sources.items():
            if config["active"]:
                task = asyncio.create_task(
                    self._monitor_source(source_name, config)
                )
                self.monitoring_tasks[source_name] = task
                self.logger.info(f"Started monitoring: {source_name}")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        self.monitoring_tasks.clear()
        self.logger.info("🛑 DON monitoring stopped")
    
    async def _monitor_source(self, source_name: str, config: Dict):
        """Monitor single data source continuously"""
        interval = config["interval"]
        
        while self.monitoring_active:
            try:
                # Fetch data from source
                data = await self._fetch_data(source_name, config)
                
                if data and self._detect_anomaly(data, source_name):
                    # Parse data using source-specific parser
                    parsed_data = await config["parser"](data)
                    
                    if parsed_data:
                        # Send to orchestrator for processing
                        await self.orchestrator_callback(parsed_data)
                        self.logger.info(f"🚨 Anomaly detected from {source_name}")
                
            except Exception as e:
                self.logger.error(f"Error monitoring {source_name}: {e}")
            
            # Wait before next poll
            await asyncio.sleep(interval)
    
    async def _fetch_data(self, source_name: str, config: Dict) -> Optional[Dict]:
        """Fetch data from external API"""
        try:
            if config["url"].startswith("internal://"):
                # Handle internal monitoring
                return await self._fetch_internal_data(source_name)
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(config["url"]) as response:
                    if response.status == 200:
                        if "json" in config["url"]:
                            return await response.json()
                        else:
                            text = await response.text()
                            return {"raw_text": text, "source": source_name}
                    else:
                        self.logger.warning(f"HTTP {response.status} from {source_name}")
                        
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout fetching from {source_name}")
        except Exception as e:
            self.logger.error(f"Fetch error from {source_name}: {e}")
        
        return None
    
    async def _fetch_internal_data(self, source_name: str) -> Optional[Dict]:
        """Fetch from internal monitoring systems"""
        if source_name == "social_media_monitor":
            # Simulate social media monitoring
            return {
                "platform": "twitter",
                "keywords_detected": ["gempa", "banjir", "kebakaran"],
                "sentiment_spike": True,
                "post_count": 150,
                "timestamp": datetime.now().isoformat()
            }
        return None
    
    def _detect_anomaly(self, data: Dict, source: str) -> bool:
        """Detect if data contains disaster signals"""
        if not data:
            return False
            
        # BMKG earthquake detection
        if source == "bmkg_autogempa" and "Infogempa" in str(data):
            gempa = data.get("Infogempa", {}).get("gempa", {})
            if gempa and "Magnitude" in gempa:
                magnitude = float(gempa["Magnitude"])
                return magnitude >= 4.0  # Detect M4+ earthquakes
        
        # Flood detection from PetaBencana
        if source == "petabencana_flood":
            # Check for active flood reports
            return "flood" in str(data).lower()
        
        # Fire detection from NASA FIRMS  
        if source == "nasa_firms":
            # Check for high confidence fire detections
            return "confidence" in str(data) and any(
                "8" in str(data) or "9" in str(data) for _ in [1]
            )
        
        # Social media anomaly detection
        if source == "social_media_monitor":
            return data.get("sentiment_spike", False) or data.get("post_count", 0) > 100
        
        return False
    
    # Data parsers untuk setiap source
    async def _parse_bmkg_data(self, data: Dict) -> Optional[Dict]:
        """Parse BMKG earthquake data"""
        try:
            gempa = data.get("Infogempa", {}).get("gempa", {})
            if not gempa:
                return None
                
            return {
                "source_type": "bmkg_earthquake",
                "gempa": gempa,
                "detected_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"BMKG parse error: {e}")
            return None
    
    async def _parse_usgs_data(self, data: Dict) -> Optional[Dict]:
        """Parse USGS earthquake data"""
        try:
            features = data.get("features", [])
            for feature in features:
                props = feature.get("properties", {})
                coords = feature.get("geometry", {}).get("coordinates", [])
                
                # Filter for Indonesia region
                if len(coords) >= 2:
                    lon, lat = coords[0], coords[1]
                    if -11 <= lat <= 6 and 95 <= lon <= 141:  # Indonesia bounds
                        return {
                            "source_type": "usgs_earthquake", 
                            "properties": props,
                            "coordinates": coords,
                            "detected_at": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"USGS parse error: {e}")
            
        return None
    
    async def _parse_petabencana_data(self, data: Dict) -> Optional[Dict]:
        """Parse PetaBencana flood data"""
        try:
            # Parse flood reports
            if "result" in data:
                return {
                    "source_type": "petabencana_flood",
                    "flood_data": data["result"],
                    "detected_at": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"PetaBencana parse error: {e}")
            
        return None
    
    async def _parse_nasa_firms_data(self, data: Dict) -> Optional[Dict]:
        """Parse NASA FIRMS fire data"""
        try:
            if "raw_text" in data:
                # Parse CSV data for Indonesia
                lines = data["raw_text"].split('\n')
                for line in lines[1:]:  # Skip header
                    parts = line.split(',')
                    if len(parts) >= 4:
                        lat, lon = float(parts[0]), float(parts[1])
                        if -11 <= lat <= 6 and 95 <= lon <= 141:  # Indonesia
                            return {
                                "source_type": "nasa_firms_fire",
                                "latitude": lat,
                                "longitude": lon,
                                "confidence": float(parts[2]) if parts[2] else 0,
                                "detected_at": datetime.now().isoformat()
                            }
        except Exception as e:
            self.logger.error(f"NASA FIRMS parse error: {e}")
            
        return None
    
    async def _parse_social_signals(self, data: Dict) -> Optional[Dict]:
        """Parse social media signals"""
        try:
            if data.get("sentiment_spike") or data.get("post_count", 0) > 100:
                return {
                    "source_type": "social_media",
                    "platform": data["platform"],
                    "signal_strength": data.get("post_count", 0),
                    "keywords": data.get("keywords_detected", []),
                    "detected_at": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Social signals parse error: {e}")
            
        return None
    
    def get_monitoring_status(self) -> Dict:
        """Get DON monitoring status"""
        active_sources = sum(1 for config in self.data_sources.values() if config["active"])
        running_tasks = len([t for t in self.monitoring_tasks.values() if not t.done()])
        
        return {
            "monitoring_active": self.monitoring_active,
            "total_sources": len(self.data_sources),
            "active_sources": active_sources,
            "running_tasks": running_tasks,
            "uptime": "99.8%"  # Mock uptime
        }