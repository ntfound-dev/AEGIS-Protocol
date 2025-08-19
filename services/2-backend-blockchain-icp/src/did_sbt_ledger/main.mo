import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Array "mo:base/Array";
import Result "mo:base/Result";
import Time "mo:base/Time";

type DIDProfile = {
    owner : Principal;
    name : Text;
    entity_type : Text;
    contact_info : Text;
    registration_date : Time.Time;
};

type SBT = {
    badge_id : Nat;
    issuer : Principal;
    event_name : Text;
    badge_type : Text;
    issued_at : Time.Time;
};

persistent actor class DID_SBT_Ledger(init_admin : Principal) {
     var did_registry : [(Principal, DIDProfile)] = [];
     var sbt_ledger : [(Principal, [SBT])] = [];
     var next_badge_id : Nat = 0;
     var authorized_minters : [Principal] = [];
     var admin : Principal = init_admin;



persistent actor class DID_SBT_Ledger(init_admin : Principal) {

    // Types moved inside the actor to satisfy the moc restriction
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

    // State (kept as before)
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
        did_registry := Array.filter(
            did_registry,
            func(entry : (Principal, DIDProfile)) : Bool { entry.0 != msg.caller }
        );
        did_registry := Array.append(did_registry, [(msg.caller, profile)]);
        return "DID Profile registered/updated successfully.";
    };

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
        var updated : [(Principal, [SBT])] = [];
        for ((p, badges) in sbt_ledger.vals()) {
            if (p == recipient) {
                updated := Array.append(updated, [(p, Array.append(badges, [new_badge]))]);
                found := true;
            } else {
                updated := Array.append(updated, [(p, badges)]);
            }
        };
        if (not found) {
            updated := Array.append(updated, [(recipient, [new_badge])]);
        };
        sbt_ledger := updated;
        next_badge_id += 1;
        return #ok("SBT minted successfully for " # Principal.toText(recipient));
    };

    public shared(msg) func authorize_minter(minter_principal : Principal) : async Result.Result<Text, Text> {
        if (msg.caller != admin) {
            return #err("Only the admin can authorize a new minter.");
        };

        if (not is_authorized_minter(minter_principal)) {
            authorized_minters := Array.append(authorized_minters, [minter_principal]);
        };
        return #ok("Minter authorized.");
    };

    private func is_authorized_minter(p : Principal) : Bool {
        for (minter in authorized_minters.vals()) {
            if (minter == p) { return true; };
        };
        return false;
    };

    public query func get_did(owner : Principal) : async ?DIDProfile {
        for ((p, profile) in did_registry.vals()) {
            if (p == owner) { return ?profile; };
        };
        return null;
    };

    public query func get_sbts(owner : Principal) : async [SBT] {
        for ((p, badges) in sbt_ledger.vals()) {
            if (p == owner) { return badges; };
        };
        return [];
    };
};
};