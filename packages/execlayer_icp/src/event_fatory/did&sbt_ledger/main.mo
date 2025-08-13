// src/did_sbt_ledger/main.mo
// Canister ini berfungsi sebagai registri untuk Decentralized Identities (DID)
// dan sebagai ledger untuk Soulbound Tokens (SBTs), yaitu lencana reputasi on-chain.

import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Map "mo:base/HashMap";
import Result "mo:base/Result";
import Time "mo:base/Time";

actor DID_SBT_Ledger {

    // --- Definisi Tipe Data ---

    // Struktur untuk profil identitas digital (DID)
    public type DIDProfile = {
        owner: Principal;
        name: Text;
        entity_type: Text; // Contoh: "NGO", "Volunteer", "Donor"
        contact_info: Text;
        registration_date: Time.Time;
        // Di dunia nyata, ini bisa berisi link ke verifikasi eksternal (misal, VCs)
    };

    // Struktur untuk Soulbound Token (SBT)
    public type SBT = {
        badge_id: Nat;
        issuer: Principal; // Principal dari EventDAO yang menerbitkan
        event_name: Text;  // Contoh: "Haiti Earthquake 2025"
        badge_type: Text;  // Contoh: "First Responder", "Top 1% Donor", "Logistics Expert"
        issued_at: Time.Time;
    };

    // --- State dari Ledger ---

    // Menyimpan profil DID, dipetakan dari Principal pemilik.
    private var did_registry = Map.fromArray<Principal, DIDProfile>([]);

    // Menyimpan SBT, dipetakan dari Principal pemilik ke array SBT mereka.
    private var sbt_ledger = Map.fromArray<Principal, [SBT]>([]);
    private var next_badge_id: Nat = 0;

    // Daftar Principal (misalnya EventDAO yang sudah diarsipkan) yang diizinkan untuk mencetak SBT.
    private var authorized_minters: [Principal] = [];
    
    // Admin yang bisa menambahkan minter baru.
    private let admin: Principal;

    // --- Inisialisasi Aktor ---
    public init() {
        admin = msg.caller; // Principal yang men-deploy canister ini menjadi admin.
    };

    // --- Fungsi Publik (Update Calls) ---

    // Fungsi untuk mendaftarkan atau memperbarui profil DID.
    public shared(msg) func register_did(name: Text, entity_type: Text, contact_info: Text) : async Text {
        let profile : DIDProfile = {
            owner = msg.caller;
            name = name;
            entity_type = entity_type;
            contact_info = contact_info;
            registration_date = Time.now();
        };
        did_registry.put(msg.caller, profile);
        return "DID Profile registered/updated successfully.";
    };

    // Fungsi untuk mencetak (mint) SBT baru untuk seorang partisipan.
    public shared(msg) func mint_sbt(recipient: Principal, event_name: Text, badge_type: Text) : async Result.Result<Text, Text> {
        // Keamanan: Hanya minter yang sah yang bisa memanggil fungsi ini.
        if (not is_authorized_minter(msg.caller)) {
            return #err("Caller is not authorized to mint SBTs.");
        };

        let new_badge : SBT = {
            badge_id = next_badge_id;
            issuer = msg.caller;
            event_name = event_name;
            badge_type = badge_type;
            issued_at = Time.now();
        };

        // Tambahkan badge baru ke ledger milik penerima.
        let current_badges = sbt_ledger.get(recipient) ?? [];
        let updated_badges = Array.append(current_badges, [new_badge]);
        sbt_ledger.put(recipient, updated_badges);

        next_badge_id += 1;
        return #ok("SBT minted successfully for " # Principal.toText(recipient));
    };
    
    // Fungsi khusus admin untuk menambahkan EventDAO sebagai minter yang sah.
    public shared(msg) func authorize_minter(minter_principal: Principal) : async Result.Result<Text, Text> {
        if (msg.caller != admin) {
            return #err("Only the admin can authorize a new minter.");
        };
        authorized_minters := Array.append(authorized_minters, [minter_principal]);
        return #ok("Minter authorized.");
    };


    // --- Fungsi Internal & Helper ---

    private query func is_authorized_minter(p: Principal) : Bool {
        for (minter in authorized_minters.vals()) {
            if (minter == p) { return true; };
        };
        return false;
    };


    // --- Fungsi Publik (Query Calls) ---

    // Mengambil profil DID dari sebuah Principal.
    public shared(msg) query func get_did(owner: Principal) : async ?DIDProfile {
        return did_registry.get(owner);
    };

    // Mengambil semua SBT yang dimiliki oleh sebuah Principal.
    public shared(msg) query func get_sbts(owner: Principal) : async [SBT] {
        return sbt_ledger.get(owner) ?? [];
    };
}
