import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";

module EventDefs {

  // Simple non-crypto mixing that consumes every 8-bit chunk of the Nat.
  // Uses small constant values to avoid potential parser/LSP issues.

  public func simpleHashAllBytes(n : Nat) : Nat {
    var x = n;
    var h = 1469598103;     // smaller offset basis
    var prime = 1099511627; // smaller prime

    if (x == 0) {
      h := (h * prime) + 0;
    };

    while (x > 0) {
      let b = x % 256;        // low 8 bits
      h := (h * prime) + b;
      x := x / 256;
    };

    h;
  };

  // Return a Nat truncated to 32 bits (mod 2^32)
  public func hashNat(key : Nat) : Nat {
    let h_big = simpleHashAllBytes(key);
    h_big % 4294967296;
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
};
