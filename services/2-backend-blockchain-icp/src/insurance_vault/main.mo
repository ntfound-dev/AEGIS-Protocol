// File: services/2-backend-blockchain-icp/src/insurance_vault/main.mo

import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Result "mo:base/Result";
import Array "mo:base/Array";

// Impor tipe data dari EventFactory untuk konsistensi
import EventFactory "mo:../event_factory/main";

actor InsuranceVault {

    private var total_liquidity: Nat = 0;
    private var authorized_factory: Principal;
    private var authorized_funders: [Principal] = [];

    public init(factory_id: Principal, initial_funders: [Principal]) {
        authorized_factory = factory_id;
        authorized_funders = initial_funders;
    };

    public shared(msg) func fund_vault(amount: Nat) : async Result.Result<Text, Text> {
        if (not is_authorized_funder(msg.caller)) {
            return #err("Caller is not an authorized funder.");
        };

        total_liquidity += amount;
        return #ok("Vault funded successfully. New balance: " # Nat.toText(total_liquidity));
    };

    public shared(msg) func release_initial_funding(
        dao_canister_id: Principal,
        event_data: EventFactory.ValidatedEventData
    ) : async Result.Result<Text, Text> {
        if (msg.caller != authorized_factory) {
            return #err("Unauthorized: Only the EventFactory can call this function.");
        };

        let payout_amount = determine_payout(event_data);
        if (payout_amount == 0) {
            return #ok("Event severity does not meet the policy trigger for a payout.");
        };

        if (total_liquidity < payout_amount) {
            return #err("Insufficient liquidity in the vault to cover the payout.");
        };

        total_liquidity -= payout_amount;
        return #ok("Successfully released " # Nat.toText(payout_amount) # " to DAO " # Principal.toText(dao_canister_id));
    };

    private func determine_payout(event_data: EventFactory.ValidatedEventData) : Nat {
        switch (event_data.severity) {
            case ("Critical") { return 2_000_000; };
            case ("High")     { return 500_000; };
            case ("Medium")   { return 50_000; };
            case (_)          { return 0; };
        }
    };

    private query func is_authorized_funder(p: Principal) : Bool {
        for (funder in authorized_funders.vals()) {
            if (funder == p) { return true; };
        };
        return false;
    };

    public shared(msg) query func get_total_liquidity() : async Nat {
        return total_liquidity;
    };
}