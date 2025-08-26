import TrieMap "mo:base/TrieMap";
import Buffer "mo:base/Buffer";
import Types "types";
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Nat32 "mo:base/Nat32";
import Hash "mo:base/Hash";
import Debug "mo:base/Debug";
import EventDefs "event_defs";
import SbtLedger "canister:did_sbt_ledger";

persistent actor EventDAO {

    
    var treasury_balance : Nat = 0;

    func customNatHash(n : Nat) : Hash.Hash { Nat32.fromNat(n % 4294967296); };

    transient var proposals : TrieMap.TrieMap<Nat, EventDefs.Proposal> =
        TrieMap.TrieMap<Nat, EventDefs.Proposal>(Nat.equal, customNatHash);

    transient var donors : TrieMap.TrieMap<Principal, Nat> =
        TrieMap.TrieMap<Principal, Nat>(Principal.equal, Principal.hash);

    var nextProposalId : Nat = 0;
    transient var event_details : ?Types.ValidatedEventData = null;
    transient var factory_principal : ?Principal = null;

    public shared func initialize(args: Types.InitArgs) : async Text {
        if (factory_principal != null) {
            return "Already initialized.";
        };
        factory_principal := ?args.factory_principal;
        event_details := ?args.event_data;
        return "Initialized.";
    };

    public shared query func get_event_details() : async ?Types.ValidatedEventData {
        return event_details;
    };

    public shared query func get_all_proposals() : async [EventDefs.ProposalInfo] {
        let results = Buffer.Buffer<EventDefs.ProposalInfo>(proposals.size());
        for ((_, proposal) in proposals.entries()) {
            results.add({
                id = proposal.id;
                proposer = proposal.proposer;
                title = proposal.title;
                description = proposal.description;
                amount_requested = proposal.amount_requested;
                recipient_wallet = proposal.recipient_wallet;
                votes_for = proposal.votes_for;
                votes_against = proposal.votes_against;
                is_executed = proposal.is_executed;
            });
        };
        return Buffer.toArray(results);
    };

    public shared(msg) func submit_proposal(
        title: Text,
        description: Text,
        amount: Nat,
        recipient: Principal
    ) : async Text {
        let pid = nextProposalId;
        let voters_map = TrieMap.TrieMap<Principal, Bool>(Principal.equal, Principal.hash);
        let proposal : EventDefs.Proposal = {
            id = pid;
            proposer = msg.caller;
            title = title;
            description = description;
            amount_requested = amount;
            recipient_wallet = recipient;
            votes_for = 0;
            votes_against = 0;
            voters = voters_map;
            is_executed = false;
        };
        proposals.put(pid, proposal);
        nextProposalId += 1;
        return "Proposal submitted with ID: " # Nat.toText(pid);
    };

    public shared(msg) func donateAndVote(
        amount: Nat,
        proposalId: EventDefs.ProposalId,
        in_favor: Bool
    ) : async Text {
        _donate(msg.caller, amount);
        let vote_msg = await _vote(msg.caller, proposalId, in_favor);
        if (vote_msg != "Vote cast successfully.") {
            Debug.trap("Voting failed: " # vote_msg);
        };

        let event_name = switch(event_details) {
            case (?details) { details.event_type };
            case (null) { "Unknown Event" };
        };

        let mint_result = await SbtLedger.mint_sbt(
            msg.caller,
            event_name,
            "Donatur & Partisipan"
        );
        
        switch (mint_result) {
          case (#ok(_mint_message)) {
            return "Thank you! Donation and vote have been recorded. Your participation SBT has been minted.";
          };
          case (#err(error_message)) {
            Debug.trap("FATAL: Your donation and vote were recorded, but SBT minting failed: " # error_message);
          };
        };
    };

    private func _donate(caller: Principal, amount: Nat) {
        switch (donors.get(caller)) {
            case (null) { donors.put(caller, amount); };
            case (?old) { donors.put(caller, old + amount); };
        };
        treasury_balance += amount;
    };
   
    public shared(msg) func donate(amount: Nat) : async Text {
        _donate(msg.caller, amount);
        return "Thank you for your donation of " # Nat.toText(amount) # " units.";
    };

    private func _vote(caller: Principal, proposalId: EventDefs.ProposalId, in_favor: Bool) : async Text {
        switch (proposals.get(proposalId)) {
            case (null) { return "Proposal not found."; };
            case (?proposal) {
                if (proposal.voters.get(caller) != null) {
                    return "You have already voted on this proposal.";
                };
                proposal.voters.put(caller, true);
                let updated = if (in_favor) {
                    { proposal with votes_for = proposal.votes_for + 1 }
                } else {
                    { proposal with votes_against = proposal.votes_against + 1 }
                };
                proposals.put(proposalId, updated);
                ignore try_execute_proposal(proposalId);
                return "Vote cast successfully.";
            };
        };
    };

    private func try_execute_proposal(proposalId: EventDefs.ProposalId) : async () {
        switch (proposals.get(proposalId)) {
            case (?proposal) {
                if (proposal.votes_for > 5 and not proposal.is_executed) {
                    if (treasury_balance >= proposal.amount_requested) {
                        treasury_balance -= proposal.amount_requested;
                        let updated = { proposal with is_executed = true };
                        proposals.put(proposalId, updated);
                    };
                };
            };
            case (_) {};
        };
    };
};