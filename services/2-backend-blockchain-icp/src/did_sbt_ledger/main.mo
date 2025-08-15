// File: services/2-backend-blockchain-icp/src/did_sbt_ledger/main.mo

import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Trie "mo:base/Trie";
import Result "mo:base/Result";
import Time "mo:base/Time";
import Array "mo:base/Array";
import Option "mo:base/Option";

actor class DID_SBT_Ledger(init_admin: Principal) {

    // --- PERBAIKAN: Menggunakan Trie.empty() untuk inisialisasi ---
    stable var did_registry = Trie.empty<Principal, DIDProfile>();
    stable var sbt_ledger = Trie.empty<Principal, [SBT]>();
    
    stable var next_badge_id: Nat = 0;
    stable var authorized_minters: [Principal] = [];

    // --- PERBAIKAN: Admin di-set melalui argumen constructor ---
    stable var admin: Principal = init_admin;

    public stable type DIDProfile = {
        owner: Principal;
        name: Text;
        entity_type: Text;
        contact_info: Text;
        registration_date: Time.Time;
    };

    public stable type SBT = {
        badge_id: Nat;
        issuer: Principal;
        event_name: Text;
        badge_type: Text;
        issued_at: Time.Time;
    };
    
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

    public shared(msg) func mint_sbt(recipient: Principal, event_name: Text, badge_type: Text) : async Result<Text, Text> {
        if (not is_authorized_minter(msg.caller)) { return #err("Caller is not authorized to mint SBTs."); };
        let new_badge : SBT = {
            badge_id = next_badge_id;
            issuer = msg.caller;
            event_name = event_name;
            badge_type = badge_type;
            issued_at = Time.now();
        };
        let current_badges = Option.get(sbt_ledger.get(recipient), []);
        let updated_badges = Array.append(current_badges, [new_badge]);
        sbt_ledger.put(recipient, updated_badges);
        next_badge_id += 1;
        return #ok("SBT minted successfully for " # Principal.toText(recipient));
    };
    
    public shared(msg) func authorize_minter(minter_principal: Principal) : async Result<Text, Text> {
        if (msg.caller != admin) {
            return #err("Only the admin can authorize a new minter.");
        };
        
        if (not is_authorized_minter(minter_principal)) {
            authorized_minters := Array.append(authorized_minters, [minter_principal]);
        };
        return #ok("Minter authorized.");
    };

    private func is_authorized_minter(p: Principal) : Bool {
        // --- PERBAIKAN: Iterasi langsung pada array ---
        for (minter in authorized_minters) {
            if (minter == p) { return true; };
        };
        return false;
    };

    public shared(msg) query func get_did(owner: Principal) : async ?DIDProfile {
        return did_registry.get(owner);
    };

    public shared(msg) query func get_sbts(owner: Principal) : async [SBT] {
        return Option.get(sbt_ledger.get(owner), []);
    };
}