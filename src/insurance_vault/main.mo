// Hapus import Buffer karena tidak digunakan lagi
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
    // Semua state harus dideklarasikan 'stable' secara eksplisit
     var total_liquidity: Nat = 0;

     let authorized_factory: Principal = factory_id;

    // --- PERBAIKAN STRUKTUR STATE ---
    // Pisahkan funder awal (immutable) dari funder tambahan (mutable)
    // untuk mematuhi semua aturan compiler.
     let initial_funder: Principal = funder_id;
     var additional_funders: [Principal] = [];


    // ---- Internal Helpers ----
    private func arrayContains<T>(arr: [T], val: T, eq: (T, T) -> Bool): Bool {
        for (item in arr.vals()) {
            if (eq(item, val)) { return true };
        };
        false
    };

    // Fungsi helper ini sekarang harus memeriksa kedua variabel funder
    private func isAuthorizedFunder(who: Principal): Bool {
        Principal.equal(who, initial_funder) or 
        arrayContains<Principal>(additional_funders, who, Principal.equal)
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

    public query func get_total_liquidity(): async Nat {
        total_liquidity
    };

    // Fungsi query ini sekarang harus menggabungkan kedua daftar funder
    public query func get_authorized_funders(): async [Principal] {
        // Gabungkan funder awal dengan funder tambahan
        Array.append<Principal>([initial_funder], additional_funders)
    };

    // Fungsi add_funder sekarang hanya berinteraksi dengan 'additional_funders'
    public shared(msg) func add_funder(p: Principal): async Result<Text, Text> {
        if (msg.caller != authorized_factory) {
            return #err("Unauthorized: only the EventFactory can add funders.");
        };
        
        if (isAuthorizedFunder(p)) {
            return #ok("Funder already authorized.");
        };
        
        // Tambahkan ke daftar 'additional_funders'.
        // Kita kembali menggunakan Array.append, abaikan warning performa demi correctness.
        additional_funders := Array.append<Principal>(additional_funders, [p]);
        return #ok("Funder added.");
    };
};