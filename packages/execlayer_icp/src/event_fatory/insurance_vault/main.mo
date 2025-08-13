// src/insurance_vault/main.mo
// Canister ini berfungsi sebagai brankas asuransi parametrik.
// Ia memegang likuiditas dan secara otomatis mencairkannya berdasarkan pemicu (trigger)
// yang telah ditentukan, seperti tingkat keparahan bencana.

import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Result "mo:base/Result";

// Impor tipe data dari EventFactory untuk konsistensi
import EventFactory "event_factory";

actor InsuranceVault {

    // --- State dari Vault ---

    // Total likuiditas yang tersedia di dalam vault.
    private var total_liquidity: Nat = 0;

    // Principal (ID) dari EventFactory. Hanya factory yang bisa meminta pencairan dana.
    // Ini diatur saat vault pertama kali di-deploy.
    private var authorized_factory: Principal;

    // Daftar Principal yang diizinkan untuk mendanai vault ini (misalnya, penyedia likuiditas).
    private var authorized_funders: [Principal] = [];

    // --- Inisialisasi Aktor ---

    // Aktor diinisialisasi dengan ID dari EventFactory dan daftar funder awal.
    public init(factory_id: Principal, initial_funders: [Principal]) {
        authorized_factory = factory_id;
        authorized_funders = initial_funders;
        // Menambahkan diri sendiri sebagai funder untuk testing
        authorized_funders := Array.append(authorized_funders, [Principal.fromActor(self)]);
    };

    // --- Fungsi Publik (Update Calls) ---

    // Fungsi untuk penyedia likuiditas (funder) untuk menambahkan dana ke vault.
    public shared(msg) func fund_vault(amount: Nat) : async Result.Result<Text, Text> {
        // Cek apakah pemanggil adalah funder yang sah.
        if (not is_authorized_funder(msg.caller)) {
            return #err("Caller is not an authorized funder.");
        };

        // Simulasi penerimaan token (misalnya, ICP atau token ICRC-1)
        total_liquidity += amount;

        return #ok("Vault funded successfully. New balance: " # Nat.toText(total_liquidity));
    };

    // Fungsi utama yang dipanggil oleh EventFactory setelah DAO baru dibuat.
    public shared(msg) func release_initial_funding(
        dao_canister_id: Principal,
        event_data: EventFactory.ValidatedEventData
    ) : async Result.Result<Text, Text> {

        // 1. Keamanan: Pastikan hanya EventFactory yang bisa memanggil fungsi ini.
        if (msg.caller != authorized_factory) {
            return #err("Unauthorized: Only the EventFactory can call this function.");
        };

        // 2. Logika Polis: Tentukan jumlah payout berdasarkan data event.
        let payout_amount = determine_payout(event_data);

        if (payout_amount == 0) {
            return #ok("Event severity does not meet the policy trigger for a payout.");
        };

        // 3. Cek Saldo: Pastikan likuiditas cukup.
        if (total_liquidity < payout_amount) {
            return #err("Insufficient liquidity in the vault to cover the payout.");
        };

        // 4. Eksekusi: Kurangi saldo vault dan kirim dana ke DAO.
        total_liquidity -= payout_amount;

        // --- Simulasi Transfer Dana ---
        // Di dunia nyata, ini akan menjadi panggilan ke canister DAO atau canister ledger (ICRC-1)
        // untuk mentransfer token.
        // let dao_actor = actor(dao_canister_id) : EventDAO;
        // await dao_actor.receive_funding(payout_amount);
        // -----------------------------

        return #ok("Successfully released " # Nat.toText(payout_amount) # " to DAO " # Principal.toText(dao_canister_id));
    };


    // --- Fungsi Internal & Helper ---

    // Logika sederhana untuk menentukan jumlah dana yang dicairkan.
    // Ini adalah inti dari "asuransi parametrik".
    private func determine_payout(event_data: EventFactory.ValidatedEventData) : Nat {
        switch (event_data.severity) {
            case ("Critical") { return 2_000_000; }; // Payout $2 Juta (disimulasikan)
            case ("High")     { return 500_000; };   // Payout $500 Ribu
            case ("Medium")   { return 50_000; };    // Payout $50 Ribu
            case (_)          { return 0; };         // Tidak ada payout untuk severity lain
        }
    };

    // Memeriksa apakah sebuah Principal ada di dalam daftar funder yang sah.
    private query func is_authorized_funder(p: Principal) : Bool {
        for (funder in authorized_funders.vals()) {
            if (funder == p) { return true; };
        };
        return false;
    };


    // --- Fungsi Publik (Query Calls) ---

    // Melihat total likuiditas yang ada di vault.
    public shared(msg) query func get_total_liquidity() : async Nat {
        return total_liquidity;
    };

    // Melihat Principal dari EventFactory yang terdaftar.
    public shared(msg) query func get_factory_principal() : async Principal {
        return authorized_factory;
    };
}
