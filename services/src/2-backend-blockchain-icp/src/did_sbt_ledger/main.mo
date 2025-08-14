// File: services/2-backend-blockchain-icp/src/did_sbt_ledger/main.mo

import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Map "mo:base/HashMap";
import Result "mo:base/Result";
import Time "mo:base/Time";
import Array "mo:base/Array";

actor DID_SBT_Ledger {

    public type DIDProfile = {
        owner: Principal;
        name: Text;
        entity_type: Text;
        contact_info: Text;
        registration_date: Time.Time;
    };

    public type SBT = {
        badge_id: Nat;
        issuer: Principal;
        event_name: Text;
        badge_type: Text;
        issued_at: Time.Time;
    };

    private var did_registry = Map.fromArray<Principal, DIDProfile>([]);
    private var sbt_ledger = Map.fromArray<Principal, [SBT]>([]);
    private var next_badge_id: Nat = 0;
    private var authorized_minters: [Principal] = [];
    private let admin: Principal;

    public init() {
        admin = msg.caller;
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

    public shared(msg) func mint_sbt(recipient: Principal, event_name: Text, badge_type: Text) : async Result.Result<Text, Text> {
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

        let current_badges = sbt_ledger.get(recipient) ?? [];
        let updated_badges = Array.append(current_badges, [new_badge]);
        sbt_ledger.put(recipient, updated_badges);

        next_badge_id += 1;
        return #ok("SBT minted successfully for " # Principal.toText(recipient));
    };
    
    public shared(msg) func authorize_minter(minter_principal: Principal) : async Result.Result<Text, Text> {
        if (msg.caller != admin) {
            return #err("Only the admin can authorize a new minter.");
        };
        // Cek dulu agar tidak duplikat
        if (not is_authorized_minter(minter_principal)) {
            authorized_minters := Array.append(authorized_minters, [minter_principal]);
        };
        return #ok("Minter authorized.");
    };

    private query func is_authorized_minter(p: Principal) : Bool {
        for (minter in authorized_minters.vals()) {
            if (minter == p) { return true; };
        };
        return false;
    };

    public shared(msg) query func get_did(owner: Principal) : async ?DIDProfile {
        return did_registry.get(owner);
    };

    public shared(msg) query func get_sbts(owner: Principal) : async [SBT] {
        return sbt_ledger.get(owner) ?? [];
    };
}