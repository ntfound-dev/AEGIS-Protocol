// File: src/event_dao/main.mo

import TrieMap "mo:base/TrieMap";
import Buffer "mo:base/Buffer";
import Types "types";
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Nat32 "mo:base/Nat32";
import Hash "mo:base/Hash";

import EventDefs "event_defs"; 

persistent actor EventDAO {

    // --- State Variables ---
    var treasury_balance : Nat = 0;

    // Custom hash for Nat (avoid deprecated Nat.hash)
    func customNatHash(n : Nat) : Hash.Hash {
        Nat32.fromNat(n % 4294967296);
    };

    // TrieMap (transient: auto-reset on upgrade)
    transient var proposals : TrieMap.TrieMap<Nat, EventDefs.Proposal> =
        TrieMap.TrieMap<Nat, EventDefs.Proposal>(Nat.equal, customNatHash);

    transient var donors : TrieMap.TrieMap<Principal, Nat> =
        TrieMap.TrieMap<Principal, Nat>(Principal.equal, Principal.hash);

    var nextProposalId : Nat = 0;

    transient var event_details : ?Types.ValidatedEventData = null;
    transient var factory_principal : ?Principal = null;

    // --- Initialization ---
    public shared func initialize(args: Types.InitArgs) : async Text {
        if (factory_principal != null) {
            return "Already initialized.";
        };
        factory_principal := ?args.factory_principal;
        event_details := ?args.event_data;
        return "Initialized.";
    };

    // --- Queries ---
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

    // --- Proposals ---
    public shared(msg) func submit_proposal(
        title: Text,
        description: Text,
        amount: Nat,
        recipient: Principal
    ) : async Text {
        let pid = nextProposalId;

        let voters_map = TrieMap.TrieMap<Principal, Bool>(
            Principal.equal,
            Principal.hash
        );

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

    // --- Donations ---
    public shared(msg) func donate(amount: Nat) : async Text {
        switch (donors.get(msg.caller)) {
            case (null) { donors.put(msg.caller, amount); };
            case (?old) { donors.put(msg.caller, old + amount); };
        };
        treasury_balance += amount;
        return "Donation received.";
    };

    // --- Voting ---
    public shared(msg) func vote(
        proposalId: EventDefs.ProposalId,
        in_favor: Bool
    ) : async Text {
        if (donors.get(msg.caller) == null) {
            return "Only donors can vote.";
        };

        switch (proposals.get(proposalId)) {
            case (null) { return "Proposal not found."; };
            case (?proposal) {
                if (proposal.voters.get(msg.caller) != null) {
                    return "You have already voted on this proposal.";
                };

                proposal.voters.put(msg.caller, true);

                let updated = if (in_favor) {
                    { proposal with votes_for = proposal.votes_for + 1 }
                } else {
                    { proposal with votes_against = proposal.votes_against + 1 }
                };

                proposals.put(proposalId, updated);

                await try_execute_proposal(proposalId);
                return "Vote cast successfully.";
            };
        };
    };

    // --- Execution ---
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
