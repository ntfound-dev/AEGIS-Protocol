import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Array "mo:base/Array";
import Result "mo:base/Result";
import Time "mo:base/Time";

persistent actor class DID_SBT_Ledger(init_admin : Principal) {

    // ======================================================
    // ================ TYPE DEFINITIONS ====================
    // ======================================================

    /// DID Profile: represents a digital identity profile
    public type DIDProfile = {
        owner : Principal;
        name : Text;
        entity_type : Text;
        contact_info : Text;
        registration_date : Time.Time;
    };

    /// SBT (Soulbound Token): represents a non-transferable badge
    public type SBT = {
        badge_id : Nat;
        issuer : Principal;
        event_name : Text;
        badge_type : Text;
        issued_at : Time.Time;
    };

    // ======================================================
    // ================ STATE VARIABLES =====================
    // ======================================================

    /// Registry of all DID profiles (principal -> profile)
    var did_registry : [(Principal, DIDProfile)] = [];

    /// Ledger of all SBTs (principal -> list of badges)
    var sbt_ledger : [(Principal, [SBT])] = [];

    /// Unique counter for badge IDs
    var next_badge_id : Nat = 0;

    /// List of principals authorized to mint SBTs
    var authorized_minters : [Principal] = [];

    /// The main admin (set during actor initialization)
    var admin : Principal = init_admin;

    // ======================================================
    // ================ PUBLIC FUNCTIONS ====================
    // ======================================================

    /// ------------------------------------------------------
    /// Function : register_did
    /// Purpose  : Register or update the DID profile of the caller
    /// Params   : 
    ///   - name (Text)        -> Name of the entity
    ///   - entity_type (Text) -> Type of entity
    ///   - contact_info (Text)-> Contact details
    /// Return   : async Text  -> Status message
    /// ------------------------------------------------------
    public shared(msg) func register_did(name : Text, entity_type : Text, contact_info : Text) : async Text {
        let profile : DIDProfile = {
            owner = msg.caller;
            name = name;
            entity_type = entity_type;
            contact_info = contact_info;
            registration_date = Time.now();
        };

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

    /// ------------------------------------------------------
    /// Function : mint_sbt
    /// Purpose  : Mint a new SBT for a recipient
    /// Params   :
    ///   - recipient (Principal) -> The recipient of the badge
    ///   - event_name (Text)     -> Name of the event
    ///   - badge_type (Text)     -> Type of the badge
    /// Return   : async Result<Text, Text> -> Ok message or Error
    /// ------------------------------------------------------
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

    /// ------------------------------------------------------
    /// Function : authorize_minter
    /// Purpose  : Grant minting rights to a new principal
    /// Params   :
    ///   - minter_principal (Principal) -> Candidate minter
    /// Return   : async Result<Text, Text> -> Ok message or Error
    /// ------------------------------------------------------
    public shared(msg) func authorize_minter(minter_principal : Principal) : async Result.Result<Text, Text> {
        if (msg.caller != admin) {
            return #err("Only the admin can authorize a new minter.");
        };

        if (not is_authorized_minter(minter_principal)) {
            authorized_minters := Array.append(authorized_minters, [minter_principal]);
        };
        return #ok("Minter authorized.");
    };

    /// ------------------------------------------------------
    /// Function : get_did
    /// Purpose  : Retrieve the DID profile of a specific principal
    /// Params   :
    ///   - owner (Principal) -> Owner of the DID
    /// Return   : async ?DIDProfile -> Some(profile) or null
    /// ------------------------------------------------------
    public query func get_did(owner : Principal) : async ?DIDProfile {
        for ((p, profile) in did_registry.vals()) {
            if (p == owner) { return ?profile; };
        };
        return null;
    };

    /// ------------------------------------------------------
    /// Function : get_sbts
    /// Purpose  : Retrieve all SBTs owned by a specific principal
    /// Params   :
    ///   - owner (Principal) -> Owner of the badges
    /// Return   : async [SBT] -> List of SBTs, empty if none exist
    /// ------------------------------------------------------
    public query func get_sbts(owner : Principal) : async [SBT] {
        for ((p, badges) in sbt_ledger.vals()) {
            if (p == owner) { return badges; };
        };
        return [];
    };

    // ======================================================
    // ================ PRIVATE FUNCTIONS ===================
    // ======================================================

    /// ------------------------------------------------------
    /// Function : is_authorized_minter
    /// Purpose  : Check whether a principal has minting rights
    /// Params   : 
    ///   - p (Principal) -> The principal to check
    /// Return   : Bool -> true if authorized, false otherwise
    /// ------------------------------------------------------
    private func is_authorized_minter(p : Principal) : Bool {
        for (minter in authorized_minters.vals()) {
            if (minter == p) { return true; };
        };
        return false;
    };
};
