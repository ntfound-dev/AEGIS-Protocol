// src/event_dao/event_defs.mo
import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Hash "mo:base/Hash";

module EventDefs {
  // Fallback hash untuk Nat menggunakan Hash.hash pada nilai Nat langsung.
  // Mengembalikan Nat32 seperti yang dibutuhkan TrieMap.
  public func hashNat(key: Nat): Nat32 {
    return Hash.hash(key);
  };

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

  public type ProposalId = Nat;

  public type Proposal = {
    id: ProposalId;
    proposer: Principal;
    title: Text;
    description: Text;
    amount_requested: Nat;
    recipient_wallet: Principal;
    votes_for: Nat;
    votes_against: Nat;
    voters: TrieMap.TrieMap<Principal, Bool>;
    is_executed: Bool;
  };
}
