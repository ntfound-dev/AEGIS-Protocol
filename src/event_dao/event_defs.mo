import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";

/// ======================================================
/// Module: EventDefs
/// Purpose:
///   - Provides utility hashing functions for Nats
///   - Defines data structures for proposals
///   - Used in governance, voting, or funding mechanisms
/// ======================================================
module EventDefs {

  // ======================================================
  // ================ HASH FUNCTIONS ======================
  // ======================================================

  /// ------------------------------------------------------
  /// Function : simpleHashAllBytes
  /// Purpose  : Hashes a Nat by iterating through its bytes
  /// Params   : 
  ///   - n (Nat) -> The input number
  /// Return   : Nat -> Hash value
  /// Notes    :
  ///   - Uses FNV-like hashing algorithm
  ///   - Ensures consistent distribution for TrieMap keys
  /// ------------------------------------------------------
  public func simpleHashAllBytes(n : Nat) : Nat {
    var x = n;
    var h = 1469598103;          // FNV offset basis
    var prime = 1099511627;      // FNV prime

    if (x == 0) {
      h := (h * prime) + 0;
    };

    while (x > 0) {
      let b = x % 256;           // extract lowest byte
      h := (h * prime) + b;
      x := x / 256;              // shift right (divide by 256)
    };

    h;
  };

  /// ------------------------------------------------------
  /// Function : hashNat
  /// Purpose  : Hashes a Nat into a 32-bit space
  /// Params   : 
  ///   - key (Nat) -> The input key
  /// Return   : Nat -> 32-bit hash result
  /// ------------------------------------------------------
  public func hashNat(key : Nat) : Nat {
    let h_big = simpleHashAllBytes(key);
    h_big % 4294967296; // Limit hash to 32 bits
  };

  // ======================================================
  // ================ DATA STRUCTURES =====================
  // ======================================================

  /// ProposalInfo:
  ///   Lightweight proposal representation, without voter details
  public type ProposalInfo = {
    id: Nat;
    proposer: Principal;
    title: Text;
    description: Text;
    amount_requested: Nat;
    recipient_wallet: Principal;
    votes_for: Nat;
    votes_against: Nat;
    is_executed: Bool;
  };

  /// Unique identifier for a proposal
  public type ProposalId = Nat;

  /// Proposal:
  ///   Full proposal data, including voter tracking
  public type Proposal = {
    id: ProposalId;
    proposer: Principal;
    title: Text;
    description: Text;
    amount_requested: Nat;
    recipient_wallet: Principal;
    votes_for: Nat;
    votes_against: Nat;
    voters: TrieMap.TrieMap<Principal, Bool>; // principal -> hasVoted
    is_executed: Bool;
  };
};
