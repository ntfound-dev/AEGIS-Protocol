# main.py
# Main execution file (FIXED VERSION)

import asyncio
import logging
from datetime import datetime

from orchestrator import AegisOrchestrator
from asi_integration import ASIIntegrationLayer
from simulator import DisasterSimulator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main execution function - demonstrates full system"""
    
    print("🛡️  AEGIS PROTOCOL - AI AGENT SYSTEM INITIALIZATION")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = AegisOrchestrator()
    
    # Initialize ASI integration
    asi_layer = ASIIntegrationLayer(orchestrator)
    await asi_layer.connect_to_asi("https://asi-one.api", "demo_api_key")
    
    # Initialize simulator  
    simulator = DisasterSimulator(orchestrator)
    
    print("\n🚀 RUNNING SIMULATION SCENARIOS")
    print("-" * 40)
    
    # Run test scenarios
    scenarios = ["Jakarta_Flood_2025", "Cianjur_Earthquake_M6.2", "Kalimantan_Forest_Fire"]
    
    for scenario in scenarios:
        try:
            result = await simulator.run_simulation(scenario)
            print(f"📊 {scenario}: {result['processing_time_seconds']:.2f}s")
        except Exception as e:
            print(f"❌ Error in {scenario}: {e}")
            logging.error(f"Simulation error: {e}", exc_info=True)
    
    # Display final system status
    print("\n📈 FINAL SYSTEM STATUS")
    print("-" * 40)
    status = orchestrator.get_system_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    print("\n✅ AEGIS PROTOCOL AGENTS READY FOR ASI:ONE INTEGRATION")
    
    return orchestrator, asi_layer

# Manual testing function
async def test_individual_components():
    """Test individual components manually"""
    
    print("\n🔬 TESTING INDIVIDUAL COMPONENTS")
    print("-" * 40)
    
    orchestrator = AegisOrchestrator()
    
    # Test earthquake data parsing
    earthquake_data = {
        "source_type": "bmkg_earthquake",
        "gempa": {
            "Tanggal": "15 Aug 2025",
            "Jam": "10:30:00 WIB", 
            "Magnitude": "5.8",
            "Kedalaman": "15 km",
            "Lintang": "-6.5",
            "Bujur": "106.8",
            "Wilayah": "Jakarta, DKI Jakarta"
        }
    }
    
    print("Testing earthquake parsing...")
    event_id = await orchestrator.process_raw_data(earthquake_data)
    print(f"✅ Event created: {event_id}")
    
    # Wait for processing
    await asyncio.sleep(3)
    
    # Test mission completion
    test_participants = [
        {
            "id": "test_vol_001",
            "role": "volunteer", 
            "arrival_time": 2.5,
            "contribution": "search_rescue",
            "donation_percentile": 10.0,
            "accuracy": None
        },
        {
            "id": "test_donor_001",
            "role": "donor", 
            "arrival_time": None,
            "contribution": "funding", 
            "donation_percentile": 95.0,
            "accuracy": None
        }
    ]
    
    print("Testing mission completion...")
    completion_result = await orchestrator.complete_mission(
        event_id, "success", test_participants
    )
    print(f"✅ Mission completed: {completion_result}")
    
    return orchestrator

if __name__ == "__main__":
    # Run main simulation
    try:
        orchestrator, asi_layer = asyncio.run(main())
        print("\n🎉 System initialization completed successfully!")
        
        # Optionally run individual component tests
        print("\n" + "="*60)
        asyncio.run(test_individual_components())
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        logging.error(f"Main execution error: {e}", exc_info=True)