import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Array "mo:base/Array";
import Result "mo:base/Result";
import Time "mo:base/Time";

persistent actor class DID_SBT_Ledger(init_admin : Principal) {

    // Tipe data sekarang didefinisikan DI DALAM actor class
    public type DIDProfile = {
        owner : Principal;
        name : Text;
        entity_type : Text;
        contact_info : Text;
        registration_date : Time.Time;
    };

    public type SBT = {
        badge_id : Nat;
        issuer : Principal;
        event_name : Text;
        badge_type : Text;
        issued_at : Time.Time;
    };

    // State dari canister
    var did_registry : [(Principal, DIDProfile)] = [];
    var sbt_ledger : [(Principal, [SBT])] = [];
    var next_badge_id : Nat = 0;
    var authorized_minters : [Principal] = [];
    var admin : Principal = init_admin;


    // Fungsi registrasi DID
    public shared(msg) func register_did(name : Text, entity_type : Text, contact_info : Text) : async Text {
        let profile : DIDProfile = {
            owner = msg.caller;
            name = name;
            entity_type = entity_type;
            contact_info = contact_info;
            registration_date = Time.now();
        };
        // This is not an efficient way to update an array, but keeping it for consistency with original code.
        var new_registry : [(Principal, DIDProfile)] = [];
        for (entry in did_registry.vals()) {
            if (entry.0 != msg.caller) {
                new_registry := Array.append(new_registry, [entry]);
            };
        };
        new_registry := Array.append(new_registry, [(msg.caller, profile)]);
        did_registry := new_registry;
        return "DID Profile registered/updated successfully.";
    };

    // Fungsi untuk membuat SBT
    public shared(msg) func mint_sbt(recipient : Principal, event_name : Text, badge_type : Text) : async Result.Result<Text, Text> {
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
        
        var found = false;
        var updated_ledger : [(Principal, [SBT])] = [];
        for ((p, badges) in sbt_ledger.vals()) {
            if (p == recipient) {
                updated_ledger := Array.append(updated_ledger, [(p, Array.append(badges, [new_badge]))]);
                found := true;
            } else {
                updated_ledger := Array.append(updated_ledger, [(p, badges)]);
            }
        };

        if (not found) {
            updated_ledger := Array.append(updated_ledger, [(recipient, [new_badge])]);
        };
        
        sbt_ledger := updated_ledger;
        next_badge_id += 1;
        return #ok("SBT minted successfully for " # Principal.toText(recipient));
    };

    // Fungsi untuk memberi otorisasi pada minter
    public shared(msg) func authorize_minter(minter_principal : Principal) : async Result.Result<Text, Text> {
        if (msg.caller != admin) {
            return #err("Only the admin can authorize a new minter.");
        };

        if (not is_authorized_minter(minter_principal)) {
            authorized_minters := Array.append(authorized_minters, [minter_principal]);
        };
        return #ok("Minter authorized.");
    };

    // Fungsi privat untuk mengecek otorisasi
    private func is_authorized_minter(p : Principal) : Bool {
        for (minter in authorized_minters.vals()) {
            if (minter == p) { return true; };
        };
        return false;
    };

    // Query untuk mendapatkan profil DID
    public query func get_did(owner : Principal) : async ?DIDProfile {
        for ((p, profile) in did_registry.vals()) {
            if (p == owner) { return ?profile; };
        };
        return null;
    };

    // Query untuk mendapatkan SBT milik seseorang
    public query func get_sbts(owner : Principal) : async [SBT] {
        for ((p, badges) in sbt_ledger.vals()) {
            if (p == owner) { return badges; };
        };
        return [];
    };
};