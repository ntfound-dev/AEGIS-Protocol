import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Array "mo:base/Array";
import R "mo:base/Result";

persistent actor class InsuranceVault(factory_id: Principal, funder_id: Principal) {

    // ---- Type Aliases ----
    public type Result<T, E> = R.Result<T, E>;

    // ---- Data Types ----
    public type ValidatedEventData = {
        event_type: Text;
        severity: Text;
        details_json: Text;
    };

    // ---- State ----
    var total_liquidity: Nat = 0;
    let authorized_factory: Principal = factory_id;
    var authorized_funders: [Principal] = [funder_id];

    // ---- Internal Helpers ----
    private func arrayContains<T>(arr: [T], val: T, eq: (T, T) -> Bool): Bool {
        for (item in arr.vals()) {
            if (eq(item, val)) { return true };
        };
        false
    };

    private func isAuthorizedFunder(who: Principal): Bool {
        arrayContains<Principal>(authorized_funders, who, Principal.equal)
    };

    private func determine_payout(event_data: ValidatedEventData): Nat {
        switch (event_data.severity) {
            case ("Critical") { 2_000_000 };
            case ("High")     {   500_000 };
            case ("Medium")   {    50_000 };
            case (_)          {         0 };
        }
    };

    // ---- Public API ----

    // Update function: memodifikasi state
    public shared(msg) func fund_vault(amount: Nat): async Result<Text, Text> {
        if (amount == 0) {
            return #err("Amount must be > 0");
        };
        if (not isAuthorizedFunder(msg.caller)) {
            return #err("Unauthorized: caller is not in the authorized funders list.");
        };

        total_liquidity += amount;
        return #ok("Vault funded successfully. New balance: " # Nat.toText(total_liquidity));
    };

    public shared(msg) func release_initial_funding(
        dao_canister_id: Principal,
        event_data: ValidatedEventData
    ): async Result<Text, Text> {
        if (msg.caller != authorized_factory) {
            return #err("Unauthorized: only the EventFactory can call this function.");
        };

        let payout_amount = determine_payout(event_data);

        if (payout_amount == 0) {
            return #ok("Event severity does not meet the policy trigger for a payout.");
        };
        if (total_liquidity < payout_amount) {
            return #err("Insufficient liquidity in the vault to cover the payout.");
        };

        total_liquidity -= payout_amount;

        return #ok(
            "Successfully released " # Nat.toText(payout_amount)
            # " to DAO " # Principal.toText(dao_canister_id)
        );
    };

    // Query function: hanya baca data, tidak memodifikasi state
    public query func get_total_liquidity(): async Nat {
        total_liquidity
    };

    public query func get_authorized_funders(): async [Principal] {
        authorized_funders
    };

    // Update function: memodifikasi daftar funders
    public shared(msg) func add_funder(p: Principal): async Result<Text, Text> {
        if (msg.caller != authorized_factory) {
            return #err("Unauthorized: only the EventFactory can add funders.");
        };
        if (arrayContains<Principal>(authorized_funders, p, Principal.equal)) {
            return #ok("Funder already authorized.");
        };
        authorized_funders := Array.append<Principal>(authorized_funders, [p]);
        return #ok("Funder added.");
    };
}
