// File: src/insurance_vault/main.mo

import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Array "mo:base/Array";
import R "mo:base/Result";
import _Debug "mo:base/Debug"; 

persistent actor class InsuranceVault(init_factory_id: Principal, init_funder_id: Principal, init_admin_id: Principal) {

    // ---- Type Aliases ----
    public type Result<T, E> = R.Result<T, E>;

    // ---- Data Types ----
    // Tipe ini digunakan oleh event_factory saat memanggil release_initial_funding
    public type ValidatedEventData = {
        event_type: Text;
        severity: Text;
        details_json: Text;
    };

    // =====================================================================
    //                            STATE
    // =====================================================================

    // Total dana yang tersimpan di dalam vault.
    var total_liquidity: Nat = 0;

    // Principal ID dari event_factory yang sah.
    // Ditetapkan saat canister dibuat dan tidak bisa diubah (immutable).
    let authorized_factory: Principal = init_factory_id;

    // Funder pertama yang diotorisasi.
    // Ditetapkan saat canister dibuat dan tidak bisa diubah (immutable).
    let initial_funder: Principal = init_funder_id;

    // Daftar funder tambahan yang bisa diotorisasi nanti.
    var additional_funders: [Principal] = [];
    
    // Admin canister, yang bisa menambahkan funder tambahan.
    // Diatur ke principal yang men-deploy canister ini.
    let admin: Principal = init_admin_id;


    // =====================================================================
    //                         INTERNAL HELPERS
    // =====================================================================

    // Fungsi helper untuk memeriksa apakah sebuah principal ada di dalam array.
    private func arrayContains(arr: [Principal], val: Principal): Bool {
        for (item in arr.vals()) {
            if (Principal.equal(item, val)) { return true };
        };
        return false;
    };

    // Memeriksa apakah sebuah principal adalah funder yang sah (baik initial maupun additional).
    private func isAuthorizedFunder(who: Principal): Bool {
        Principal.equal(who, initial_funder) or
        arrayContains(additional_funders, who)
    };

    // Menentukan jumlah dana awal berdasarkan tingkat keparahan event.
    private func determine_payout(event_data: ValidatedEventData): Nat {
        switch (event_data.severity) {
            case ("Tinggi")   { 100_000_000 }; // Contoh payout
            case ("Sedang")   {  50_000_000 };
            case ("Rendah")   {  10_000_000 };
            case (_)          {           0 };
        }
    };

    // =====================================================================
    //                            PUBLIC API
    // =====================================================================

    /// Menambahkan principal baru ke dalam daftar funder tambahan yang sah.
    /// Hanya bisa dipanggil oleh admin canister.
    public shared(msg) func add_funder(funder_to_add: Principal): async Result<Text, Text> {
        if (msg.caller != admin) {
            return #err("Unauthorized: only the admin can add new funders.");
        };
        
        if (isAuthorizedFunder(funder_to_add)) {
            return #ok("Funder already authorized.");
        };
        
        additional_funders := Array.append<Principal>(additional_funders, [funder_to_add]);
        return #ok("Funder added successfully.");
    };

    /// Menyetorkan dana ke dalam vault.
    /// Hanya bisa dipanggil oleh funder yang sudah diotorisasi.
    public shared(msg) func fund_vault(amount: Nat): async Result<Text, Text> {
        if (amount == 0) {
            return #err("Amount must be greater than 0.");
        };
        if (not isAuthorizedFunder(msg.caller)) {
            return #err("Unauthorized: caller is not an authorized funder.");
        };

        total_liquidity += amount;
        return #ok("Vault funded successfully. New balance: " # Nat.toText(total_liquidity));
    };

    /// Mencairkan dana awal dari vault ke sebuah event_dao yang baru.
    /// Hanya bisa dipanggil oleh event_factory yang sah.
    public shared(msg) func release_initial_funding(
        dao_canister_id: Principal,
        event_data: ValidatedEventData
    ): async Result<Text, Text> {
        if (msg.caller != authorized_factory) {
            return #err("Unauthorized: only the authorized EventFactory can call this function.");
        };

        let payout_amount = determine_payout(event_data);

        if (payout_amount == 0) {
            return #ok("Event severity does not meet policy for a payout.");
        };
        if (total_liquidity < payout_amount) {
            return #err("Insufficient liquidity in the vault.");
        };

        total_liquidity -= payout_amount;

        // Di dunia nyata, di sini akan ada panggilan inter-canister untuk mentransfer dana.
        // Untuk saat ini, kita hanya mencatat pengurangannya.

        return #ok(
            "Successfully released " # Nat.toText(payout_amount)
            # " to DAO " # Principal.toText(dao_canister_id)
        );
    };

    // ---- Queries ----

    /// Mengembalikan jumlah total dana yang tersimpan di dalam vault.
    public query func get_total_liquidity(): async Nat {
        total_liquidity
    };

    /// Mengembalikan daftar gabungan semua principal yang diizinkan untuk mendanai vault.
    public query func get_authorized_funders(): async [Principal] {
        Array.append<Principal>([initial_funder], additional_funders)
    };
};