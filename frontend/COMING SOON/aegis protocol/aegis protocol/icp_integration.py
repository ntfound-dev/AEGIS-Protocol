# icp_integration.py
# Internet Computer Protocol (ICP) blockchain integration sesuai PDF

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

class ICPCanisterManager:
    """
    ICP Canister Manager
    Sesuai PDF: "Canister Deployment:
    - disaster_registry.mo : Registrasi bencana
    - volunteer_registry.mo : Database relawan  
    - resource_ledger.mo : Tracking dana dan sumber daya"
    """
    
    def __init__(self):
        self.canisters = {
            "disaster_registry": "rdmx6-jaaaa-aaaah-qdrva-cai",
            "volunteer_registry": "rdmx6-jaaaa-aaaah-qdrvb-cai", 
            "resource_ledger": "rdmx6-jaaaa-aaaah-qdrvc-cai",
            "parametric_vault": "rdmx6-jaaaa-aaaah-qdrvd-cai"
        }
        self.icp_balance = 200.0  # 200 ICP sesuai PDF
        self.logger = logging.getLogger("aegis.icp")
        
    async def deploy_canisters(self) -> Dict[str, bool]:
        """Deploy all required canisters"""
        deployment_results = {}
        
        for canister_name, canister_id in self.canisters.items():
            try:
                success = await self._deploy_canister(canister_name, canister_id)
                deployment_results[canister_name] = success
                
                if success:
                    self.logger.info(f"✅ Deployed {canister_name}: {canister_id}")
                else:
                    self.logger.error(f"❌ Failed to deploy {canister_name}")
                    
            except Exception as e:
                self.logger.error(f"Deployment error for {canister_name}: {e}")
                deployment_results[canister_name] = False
        
        return deployment_results
    
    async def _deploy_canister(self, canister_name: str, canister_id: str) -> bool:
        """Deploy individual canister (mock implementation)"""
        # Mock deployment process
        await asyncio.sleep(1)  # Simulate deployment time
        
        # Generate Motoko code for canister
        motoko_code = self._generate_motoko_code(canister_name)
        
        # In real implementation: 
        # - Compile Motoko code
        # - Deploy to ICP network
        # - Set canister permissions
        
        self.logger.info(f"Generated Motoko code for {canister_name}")
        return True
    
    def _generate_motoko_code(self, canister_name: str) -> str:
        """Generate Motoko smart contract code"""
        
        if canister_name == "disaster_registry":
            return """
// disaster_registry.mo
import Time "mo:base/Time";
import HashMap "mo:base/HashMap";
import Text "mo:base/Text";

actor DisasterRegistry {
    
    type DisasterEvent = {
        id: Text;
        disaster_type: Text;
        location: {lat: Float; lon: Float};
        severity: Nat;
        timestamp: Int;
        verified: Bool;
    };
    
    private var events = HashMap.HashMap<Text, DisasterEvent>(0, Text.equal, Text.hash);
    
    public func registerDisaster(event: DisasterEvent) : async Bool {
        events.put(event.id, event);
        true
    };
    
    public query func getDisaster(id: Text) : async ?DisasterEvent {
        events.get(id)
    };
    
    public query func getAllDisasters() : async [DisasterEvent] {
        events.vals() |> Iter.toArray(_)
    };
}
            """
            
        elif canister_name == "volunteer_registry":
            return """
// volunteer_registry.mo
import HashMap "mo:base/HashMap";
import Text "mo:base/Text";
import Array "mo:base/Array";

actor VolunteerRegistry {
    
    type Volunteer = {
        id: Text;
        name: Text;
        location: {lat: Float; lon: Float};
        skills: [Text];
        reputation_score: Float;
        active: Bool;
    };
    
    private var volunteers = HashMap.HashMap<Text, Volunteer>(0, Text.equal, Text.hash);
    
    public func registerVolunteer(volunteer: Volunteer) : async Bool {
        volunteers.put(volunteer.id, volunteer);
        true
    };
    
    public func findNearbyVolunteers(lat: Float, lon: Float, radius: Float) : async [Volunteer] {
        // Calculate distance and filter volunteers within radius
        volunteers.vals() 
        |> Iter.filter(_, func(v: Volunteer) : Bool {
            let distance = calculateDistance(lat, lon, v.location.lat, v.location.lon);
            distance <= radius and v.active
        })
        |> Iter.toArray(_)
    };
    
    private func calculateDistance(lat1: Float, lon1: Float, lat2: Float, lon2: Float) : Float {
        // Haversine formula implementation
        111.0 // Simplified distance in km
    };
}
            """
            
        elif canister_name == "resource_ledger":
            return """
// resource_ledger.mo
import HashMap "mo:base/HashMap";
import Text "mo:base/Text";
import Time "mo:base/Time";

actor ResourceLedger {
    
    type Transaction = {
        id: Text;
        from_account: Text;
        to_account: Text;
        amount: Float;
        transaction_type: Text;
        timestamp: Int;
        event_id: Text;
    };
    
    private var transactions = HashMap.HashMap<Text, Transaction>(0, Text.equal, Text.hash);
    private var balances = HashMap.HashMap<Text, Float>(0, Text.equal, Text.hash);
    
    public func transferFunds(from: Text, to: Text, amount: Float, event_id: Text) : async Bool {
        let from_balance = switch (balances.get(from)) {
            case null 0.0;
            case (?balance) balance;
        };
        
        if (from_balance < amount) {
            return false;
        };
        
        // Update balances
        balances.put(from, from_balance - amount);
        let to_balance = switch (balances.get(to)) {
            case null amount;
            case (?balance) balance + amount;
        };
        balances.put(to, to_balance);
        
        // Record transaction
        let tx_id = generateTxId();
        let transaction : Transaction = {
            id = tx_id;
            from_account = from;
            to_account = to;
            amount = amount;
            transaction_type = "disaster_fund_transfer";
            timestamp = Time.now();
            event_id = event_id;
        };
        transactions.put(tx_id, transaction);
        
        true
    };
    
    public query func getBalance(account: Text) : async Float {
        switch (balances.get(account)) {
            case null 0.0;
            case (?balance) balance;
        }
    };
    
    private func generateTxId() : Text {
        "tx_" # Int.toText(Time.now())
    };
}
            """
            
        elif canister_name == "parametric_vault":
            return """
// parametric_vault.mo  
import HashMap "mo:base/HashMap";
import Text "mo:base/Text";
import Float "mo:base/Float";

actor ParametricVault {
    
    type InsurancePolicy = {
        id: Text;
        disaster_type: Text;
        trigger_conditions: Text; // JSON string
        payout_amount: Float;
        active: Bool;
    };
    
    private var vault_balance : Float = 10000000.0; // $10M
    private var policies = HashMap.HashMap<Text, InsurancePolicy>(0, Text.equal, Text.hash);
    
    public func createPolicy(policy: InsurancePolicy) : async Bool {
        policies.put(policy.id, policy);
        true
    };
    
    public func triggerPayout(event_id: Text, disaster_type: Text, severity: Nat) : async ?Float {
        // Find matching policy
        for ((policy_id, policy) in policies.entries()) {
            if (policy.disaster_type == disaster_type and policy.active) {
                // Check trigger conditions (simplified)
                if (severity >= 4) {
                    if (vault_balance >= policy.payout_amount) {
                        vault_balance -= policy.payout_amount;
                        return ?policy.payout_amount;
                    };
                };
            };
        };
        null
    };
    
    public query func getVaultBalance() : async Float {
        vault_balance
    };
}
            """
        
        return "// Empty canister"

class ICPTransactionManager:
    """Manager for ICP transactions and cycles"""
    
    def __init__(self, canister_manager: ICPCanisterManager):
        self.canister_manager = canister_manager
        self.cycles_balance = 2_000_000_000_000  # 2T cycles
        self.transaction_history = []
        self.logger = logging.getLogger("aegis.icp.transactions")
    
    async def transfer_emergency_funds(self, event_id: str, amount: float, recipient: str) -> Dict:
        """Transfer emergency funds via ICP"""
        
        # Check cycles balance
        estimated_cycles = await self._estimate_cycles_cost("transfer", amount)
        
        if self.cycles_balance < estimated_cycles:
            return {"success": False, "error": "insufficient_cycles"}
        
        # Execute transfer via resource_ledger canister
        try:
            tx_result = await self._call_canister(
                "resource_ledger",
                "transferFunds",
                {
                    "from": "parametric_vault",
                    "to": recipient, 
                    "amount": amount,
                    "event_id": event_id
                }
            )
            
            if tx_result.get("success"):
                # Deduct cycles
                self.cycles_balance -= estimated_cycles
                
                # Record transaction
                tx_record = {
                    "tx_id": f"icp_tx_{len(self.transaction_history)}",
                    "event_id": event_id,
                    "amount": amount,
                    "recipient": recipient,
                    "cycles_used": estimated_cycles,
                    "timestamp": datetime.now(),
                    "status": "completed"
                }
                self.transaction_history.append(tx_record)
                
                self.logger.info(f"💰 ICP Transfer: ${amount:,} to {recipient}")
                return {"success": True, "tx_id": tx_record["tx_id"]}
            
        except Exception as e:
            self.logger.error(f"ICP transfer failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _estimate_cycles_cost(self, operation: str, amount: float = 0) -> int:
        """Estimate cycles cost for operation"""
        base_costs = {
            "transfer": 1_000_000,  # 1M cycles base
            "register": 500_000,    # 500K cycles
            "query": 100_000        # 100K cycles
        }
        
        base_cost = base_costs.get(operation, 1_000_000)
        
        # Add cost based on amount
        amount_factor = int(amount / 1000)  # +1000 cycles per $1000
        
        return base_cost + amount_factor
    
    async def _call_canister(self, canister_name: str, method: str, args: Dict) -> Dict:
        """Call canister method (mock implementation)"""
        
        canister_id = self.canister_manager.canisters.get(canister_name)
        if not canister_id:
            raise Exception(f"Canister {canister_name} not found")
        
        # Mock canister call
        await asyncio.sleep(0.5)  # Simulate network latency
        
        self.logger.info(f"📞 ICP Call: {canister_name}.{method}")
        
        # Simulate successful call
        return {
            "success": True,
            "canister_id": canister_id,
            "method": method,
            "result": "executed"
        }
    
    def get_icp_status(self) -> Dict:
        """Get ICP integration status"""
        total_transactions = len(self.transaction_history)
        total_transferred = sum(tx["amount"] for tx in self.transaction_history)
        total_cycles_used = sum(tx["cycles_used"] for tx in self.transaction_history)
        
        return {
            "canisters_deployed": len(self.canister_manager.canisters),
            "cycles_balance": self.cycles_balance,
            "cycles_used": total_cycles_used,
            "total_transactions": total_transactions,
            "total_transferred_usd": total_transferred,
            "icp_balance": self.canister_manager.icp_balance,
            "network_status": "connected"
        }