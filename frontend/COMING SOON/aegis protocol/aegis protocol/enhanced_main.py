# enhanced_main.py
# Main file dengan semua komponen baru terintegrasi

import asyncio
import logging
from datetime import datetime

# Import existing components
from orchestrator import AegisOrchestrator
from asi_integration import ASIIntegrationLayer
from simulator import DisasterSimulator

# Import new components
from parametric_vault import ParametricInsuranceVault
from oracle_network import DecentralizedOracleNetwork
from performance_monitor import PerformanceMonitor
from governance_system import GovernanceSystem, ProposalType
from icp_integration import ICPCanisterManager, ICPTransactionManager

class EnhancedAegisSystem:
    """Enhanced Aegis System dengan semua komponen lengkap sesuai PDF"""
    
    def __init__(self):
        # Core system
        self.orchestrator = AegisOrchestrator()
        self.asi_layer = ASIIntegrationLayer(self.orchestrator)
        self.simulator = DisasterSimulator(self.orchestrator)
        
        # New components
        self.vault = ParametricInsuranceVault()
        self.don = DecentralizedOracleNetwork(self._on_don_detection)
        self.performance_monitor = PerformanceMonitor()
        self.governance = GovernanceSystem()
        self.icp_manager = ICPCanisterManager()
        self.icp_transactions = ICPTransactionManager(self.icp_manager)
        
        self.logger = logging.getLogger("aegis.enhanced")
        
    async def initialize_system(self):
        """Initialize enhanced system dengan semua komponen"""
        
        self.logger.info("🚀 INITIALIZING ENHANCED AEGIS PROTOCOL")
        self.logger.info("=" * 60)
        
        # 1. Connect ASI
        await self.asi_layer.connect_to_asi("https://asi-one.api", "demo_key")
        
        # 2. Deploy ICP Canisters
        self.logger.info("📦 Deploying ICP Canisters...")
        deployment_results = await self.icp_manager.deploy_canisters()
        deployed_count = sum(1 for result in deployment_results.values() if result)
        self.logger.info(f"✅ {deployed_count}/4 canisters deployed successfully")
        
        # 3. Initialize Parametric Vault
        self.logger.info(f"💰 Parametric Vault initialized: ${self.vault.balance:,}")
        
        # 4. Start DON monitoring
        self.logger.info("🔍 Starting Decentralized Oracle Network...")
        await self.don.start_monitoring()
        
        # 5. Setup performance monitoring
        self.logger.info("📊 Performance monitoring active")
        
        self.logger.info("✅ ENHANCED AEGIS SYSTEM READY")
        
    async def _on_don_detection(self, detection_data: dict):
        """Callback when DON detects disaster"""
        self.logger.info(f"🚨 DON Detection: {detection_data.get('source_type')}")
        
        # Start performance tracking
        event_id = await self.orchestrator.process_raw_data(detection_data)
        if event_id:
            self.performance_monitor.start_tracking(event_id, "detection")
            self.performance_monitor.end_tracking(event_id, "detection")
            
        return event_id
    
    async def run_enhanced_demo(self):
        """Run enhanced demo dengan semua fitur"""
        
        print("\n🎯 ENHANCED DEMO - FULL AEGIS PROTOCOL")
        print("=" * 50)
        
        # Scenario 1: Real-time detection + Auto payout
        await self._demo_realtime_response()
        
        # Scenario 2: Governance voting
        await self._demo_governance_voting()
        
        # Scenario 3: Performance monitoring
        await self._demo_performance_tracking()
        
        # Final system status
        await self._show_enhanced_status()
    
    async def _demo_realtime_response(self):
        """Demo real-time detection dan auto payout"""
        
        print("\n📡 DEMO 1: Real-time Detection & Auto Payout")
        print("-" * 40)
        
        # Simulate earthquake detection
        earthquake_data = {
            "source_type": "bmkg_earthquake",
            "gempa": {
                "Tanggal": "16 Aug 2025",
                "Jam": "14:30:00 WIB",
                "Magnitude": "6.1", 
                "Kedalaman": "12 km",
                "Lintang": "-6.8",
                "Bujur": "107.1",
                "Wilayah": "Cianjur, Jawa Barat"
            },
            "detected_at": datetime.now().isoformat()
        }
        
        # Track performance
        start_time = datetime.now()
        event_id = await self.orchestrator.process_raw_data(earthquake_data)
        
        if event_id:
            self.performance_monitor.start_tracking(event_id, "detection")
            self.performance_monitor.end_tracking(event_id, "detection")
            
            print(f"✅ Event detected: {event_id}")
            
            # Wait for consensus
            await asyncio.sleep(3)
            
            # Simulate consensus result
            consensus_result = {
                "event_id": event_id,
                "decision": True,
                "confidence": 0.92,
                "disaster_type": "earthquake"
            }
            
            # Auto payout from vault
            event_data = {
                "event_id": event_id,
                "disaster_type": "earthquake",
                "severity": 4,
                "metadata": {"magnitude": "6.1"}
            }
            
            payout_record = await self.vault.auto_payout(consensus_result, event_data)
            
            if payout_record:
                print(f"💰 Auto-payout executed: ${payout_record.amount:,}")
                
                # Transfer via ICP
                icp_transfer = await self.icp_transactions.transfer_emergency_funds(
                    event_id, payout_record.amount, f"dao_{event_id}"
                )
                
                if icp_transfer["success"]:
                    print(f"🔗 ICP Transfer completed: {icp_transfer['tx_id']}")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"⚡ Total response time: {elapsed:.2f} seconds")
    
    async def _demo_governance_voting(self):
        """Demo governance voting dalam Event DAO"""
        
        print("\n🗳️  DEMO 2: DAO Governance & Voting")
        print("-" * 40)
        
        dao_id = "dao_evt_demo_123"
        
        # Create fund allocation proposal
        proposal = await self.governance.create_proposal(
            dao_id=dao_id,
            proposer_id="ngo_001",
            proposal_type=ProposalType.FUND_ALLOCATION,
            title="Emergency Medical Supplies",
            description="Allocate $500k for medical supplies and field hospital setup",
            requested_amount=500_000,
            target_recipient="medical_team_jakarta"
        )
        
        if proposal:
            print(f"📋 Proposal created: {proposal.proposal_id}")
            print(f"   Amount: ${proposal.requested_amount:,}")
            print(f"   Voting ends: {proposal.voting_ends_at.strftime('%H:%M')}")
            
            # Simulate voting
            voters = [
                ("vol_001", "yes"),
                ("donor_001", "yes"), 
                ("ngo_002", "yes"),
                ("validator_001", "no")
            ]
            
            for voter_id, choice in voters:
                from governance_system import VoteChoice
                vote_choice = VoteChoice.YES if choice == "yes" else VoteChoice.NO
                
                success = await self.governance.cast_vote(
                    proposal.proposal_id, voter_id, vote_choice, dao_id
                )
                
                if success:
                    print(f"   🗳️  {voter_id} voted: {choice}")
            
            # Finalize proposal
            await asyncio.sleep(1)
            result = await self.governance.finalize_proposal(proposal.proposal_id)
            
            if result:
                print(f"📊 Voting result: {result['status'].upper()}")
                print(f"   Yes votes: {result['results']['yes_percentage']:.1%}")
    
    async def _demo_performance_tracking(self):
        """Demo performance tracking dan SLA monitoring"""
        
        print("\n📊 DEMO 3: Performance & SLA Monitoring")
        print("-" * 40)
        
        # Run multiple scenarios untuk performance data
        scenarios = ["Jakarta_Flood_2025", "Cianjur_Earthquake_M6.2"]
        
        for scenario in scenarios:
            try:
                start_time = datetime.now()
                
                # Track detection
                event_id = f"perf_test_{scenario.lower()}"
                self.performance_monitor.start_tracking(event_id, "detection")
                await asyncio.sleep(0.5)  # Simulate detection time
                self.performance_monitor.end_tracking(event_id, "detection")
                
                # Track notification
                self.performance_monitor.start_tracking(event_id, "notification")
                await asyncio.sleep(1.2)  # Simulate notification time
                self.performance_monitor.end_tracking(event_id, "notification")
                
                # Track DAO creation
                self.performance_monitor.start_tracking(event_id, "dao_creation")
                await asyncio.sleep(0.8)  # Simulate DAO creation
                self.performance_monitor.end_tracking(event_id, "dao_creation")
                
                # Record physical response
                self.performance_monitor.record_physical_response(event_id, "vol_001", 3.2)
                
                # Generate report
                metrics = self.performance_monitor.generate_performance_report(event_id)
                
            except Exception as e:
                print(f"❌ Performance test failed for {scenario}: {e}")
        
        # Show overall performance stats
        stats = self.performance_monitor.get_system_performance_stats()
        print(f"📈 System Performance Summary:")
        print(f"   Average detection: {stats['averages']['detection_time']}s")
        print(f"   Average notification: {stats['averages']['notification_time']}s")
        print(f"   SLA compliance: {stats['sla_compliance_rates']['detection']}")
    
    async def _show_enhanced_status(self):
        """Show comprehensive system status"""
        
        print("\n📋 ENHANCED SYSTEM STATUS")
        print("=" * 50)
        
        # Orchestrator status
        orchestrator_status = self.orchestrator.get_system_status()
        print(f"🎛️  Orchestrator: {orchestrator_status['system_status']}")
        print(f"   Active events: {orchestrator_status['active_events']}")
        
        # DON status
        don_status = self.don.get_monitoring_status()
        print(f"📡 DON Monitoring: {don_status['monitoring_active']}")
        print(f"   Active sources: {don_status['active_sources']}/{don_status['total_sources']}")
        
        # Vault status
        vault_status = self.vault.get_vault_status()
        print(f"💰 Parametric Vault: ${vault_status['balance']:,}")
        print(f"   Total payouts: ${vault_status['total_payouts']:,}")
        
        # ICP status
        icp_status = self.icp_transactions.get_icp_status()
        print(f"🔗 ICP Integration: {icp_status['network_status']}")
        print(f"   Canisters: {icp_status['canisters_deployed']}")
        print(f"   Cycles balance: {icp_status['cycles_balance']:,}")
        
        # Performance stats
        perf_stats = self.performance_monitor.get_system_performance_stats()
        if perf_stats.get('total_events_tracked', 0) > 0:
            print(f"📊 Performance: Detection {perf_stats['sla_compliance_rates']['detection']} SLA")
        
        print(f"\n✅ AEGIS PROTOCOL FULLY OPERATIONAL")
        print(f"   🎯 Target: <30s detection, <60s notification, <4h response")
        print(f"   💎 Features: AI validation, auto-payout, DAO governance")
        print(f"   🌐 Network: DON monitoring, ICP blockchain, ASI integration")

# New integration wrapper for backward compatibility
async def run_enhanced_system():
    """Run enhanced system dengan semua fitur baru"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize enhanced system
        enhanced_system = EnhancedAegisSystem()
        await enhanced_system.initialize_system()
        
        # Run enhanced demo
        await enhanced_system.run_enhanced_demo()
        
        return enhanced_system
        
    except Exception as e:
        logging.error(f"Enhanced system failed: {e}")
        raise

# Compatibility function dengan original main
async def main():
    """Main function yang menggabungkan original + enhanced"""
    
    print("🛡️  AEGIS PROTOCOL - ENHANCED SYSTEM")
    print("=" * 60)
    
    # Run enhanced system
    enhanced_system = await run_enhanced_system()
    
    # Keep DON monitoring active
    print("\n🔄 DON monitoring active... (Press Ctrl+C to stop)")
    
    try:
        while True:
            await asyncio.sleep(60)  # Check every minute
            
            # Periodic system health check
            don_status = enhanced_system.don.get_monitoring_status()
            if not don_status["monitoring_active"]:
                print("⚠️  DON monitoring stopped, restarting...")
                await enhanced_system.don.start_monitoring()
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping enhanced system...")
        await enhanced_system.don.stop_monitoring()
        print("✅ System stopped gracefully")

if __name__ == "__main__":
    asyncio.run(main())