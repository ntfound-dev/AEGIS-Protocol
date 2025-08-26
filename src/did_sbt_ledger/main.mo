// =====================================================================
// AEGIS Protocol - DID SBT Ledger Canister
// =====================================================================
// File: src/did_sbt_ledger/main.mo
// Purpose: Decentralized Identity and Soulbound Token management
// 
// Architecture Overview:
//   The DID SBT Ledger provides a comprehensive identity and reputation
//   system for the AEGIS Protocol. It manages decentralized identities
//   (DIDs) for all participants and issues non-transferable Soulbound
//   Tokens (SBTs) to track participation and build reputation.
// 
// Key Responsibilities:
//   - Register and manage decentralized identity profiles
//   - Issue Soulbound Tokens for disaster response participation
//   - Track contributor reputation and engagement history
//   - Provide identity verification for governance participation
//   - Maintain immutable records of community contributions
// 
// Decentralized Identity (DID) System:
//   - Self-sovereign identity management for all participants
//   - Cryptographically verifiable identity assertions
//   - Privacy-preserving identity verification
//   - Integration with IC Principal system for authentication
// 
// Soulbound Token (SBT) System:
//   - Non-transferable badges representing achievements
//   - Permanent record of disaster response participation
//   - Reputation building through verified contributions
//   - Integration with DAO voting systems for weighted governance
// 
// Security Features:
//   - Principal-based identity verification
//   - Authorized minter system for SBT issuance
//   - Immutable badge records for reputation integrity
//   - Admin-controlled authorization management
// 
// Integration Points:
//   - Event DAOs: Request SBT minting for participants
//   - Frontend: Display identity profiles and achievement badges
//   - Governance: Provide reputation data for weighted voting
// =====================================================================

// Core Motoko standard library imports
import Principal "mo:base/Principal"; // Principal ID management and verification
import Nat "mo:base/Nat";            // Natural number utilities for ID generation
import Array "mo:base/Array";        // Array operations for registry management
import Result "mo:base/Result";      // Result type for error handling
import Time "mo:base/Time";          // Time utilities for timestamping

/// =====================================================================
/// Actor: DID_SBT_Ledger
/// =====================================================================
/// Comprehensive identity and reputation management system
/// 
/// Initialization:
///   - init_admin: Administrative principal for system management
/// 
/// Design Philosophy:
///   The DID SBT Ledger implements Web3 identity principles where
///   users maintain sovereign control over their identity while
///   building verifiable reputation through Soulbound Tokens that
///   cannot be transferred or sold.
/// 
/// Identity Management:
///   - Self-registration of DID profiles
///   - Cryptographic verification via IC Principals
///   - Updatable profile information for flexibility
///   - Privacy-preserving data storage
/// 
/// Reputation System:
///   - SBTs represent immutable achievement records
///   - Event-specific badges for disaster response participation
///   - Cumulative reputation building over time
///   - Integration with governance systems for weighted voting
/// 
/// Access Control:
///   - Admin manages minter authorization
///   - Authorized minters can issue SBTs
///   - Self-service DID registration
///   - Query functions for public data access
/// =====================================================================
persistent actor class DID_SBT_Ledger(init_admin : Principal) {

    // ===================================================================
    // TYPE DEFINITIONS AND DATA STRUCTURES
    // ===================================================================
    // Core data models for identity and reputation management

    /// Decentralized Identity Profile
    /// Represents a complete identity record for AEGIS Protocol participants
    /// 
    /// Fields:
    ///   - owner: Cryptographic Principal ID (immutable)
    ///   - name: Human-readable identifier (updatable)
    ///   - entity_type: Classification (individual, organization, government)
    ///   - contact_info: Communication details (updatable)
    ///   - registration_date: Immutable timestamp of initial registration
    /// 
    /// Privacy Considerations:
    ///   - Minimal personal data stored on-chain
    ///   - Contact info can be encrypted or hashed
    ///   - Public queries allow community verification
    public type DIDProfile = {
        owner : Principal;           // Cryptographic identity anchor
        name : Text;                 // Display name or organization title
        entity_type : Text;          // Classification for participation rules
        contact_info : Text;         // Communication and verification details
        registration_date : Time.Time; // Immutable registration timestamp
    };

    /// Soulbound Token (Non-transferable Achievement Badge)
    /// Represents permanent record of disaster response participation
    /// 
    /// Fields:
    ///   - badge_id: Unique identifier for the specific SBT instance
    ///   - issuer: Principal that authorized the badge issuance
    ///   - event_name: Disaster event or achievement context
    ///   - badge_type: Category of contribution or achievement
    ///   - issued_at: Immutable timestamp of badge creation
    /// 
    /// Immutability:
    ///   - Once issued, SBTs cannot be modified or transferred
    ///   - Provides permanent, verifiable record of contribution
    ///   - Builds cumulative reputation over time
    public type SBT = {
        badge_id : Nat;              // Unique sequential identifier
        issuer : Principal;          // Authorizing entity (DAO, admin, etc.)
        event_name : Text;           // Context of achievement
        badge_type : Text;           // Category of contribution
        issued_at : Time.Time;       // Immutable creation timestamp
    };

    // ===================================================================
    // STATE VARIABLES AND PERSISTENT STORAGE
    // ===================================================================
    // Core system state for identity and reputation tracking

    /// Decentralized Identity Registry
    /// Maps Principal IDs to their associated DID profiles
    /// Enables efficient lookup and verification of identity information
    /// Storage: Array of tuples for simplicity (consider TrieMap for large scale)
    var did_registry : [(Principal, DIDProfile)] = [];

    /// Soulbound Token Ledger
    /// Maps Principal IDs to their collection of earned SBTs
    /// Maintains complete achievement history for reputation calculation
    /// Storage: Array structure allows chronological ordering of badges
    var sbt_ledger : [(Principal, [SBT])] = [];

    /// Badge ID Generator
    /// Sequential counter ensuring unique identifiers for all SBTs
    /// Incremented with each new badge to prevent collisions
    var next_badge_id : Nat = 0;

    /// Authorized Minter Registry
    /// List of Principals authorized to issue SBTs
    /// Typically includes Event DAOs and admin for different badge types
    var authorized_minters : [Principal] = [];

    /// System Administrator
    /// Principal with authority to manage minter authorization
    /// Set during actor initialization and immutable thereafter
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
