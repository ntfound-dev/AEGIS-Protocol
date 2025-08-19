// File: src/event_dao/main.mo

import TrieMap "mo:base/TrieMap";
import Buffer "mo:base/Buffer";
import Types "types";
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Hash "mo:base/Hash";

import EventDefs "event_defs"; 

// Beri nama actor; gunakan 'persistent' (butuh motoko >= 0.13.5)
persistent actor EventDAO {

    // contoh: treasury ingin dipertahankan -> jangan transient (sesuaikan kebijakanmu)
    var treasury_balance: Nat = 0;

    // TrieMap bukan stable type -> transient agar di-reset saat upgrade
    transient var proposals : TrieMap.TrieMap<Nat, EventDefs.Proposal> =
        TrieMap.TrieMap<Nat, EventDefs.Proposal>(Nat.equal, EventDefs.hashNat);
    transient var donors : TrieMap.TrieMap<Principal, Nat> =
        TrieMap.TrieMap<Principal, Nat>(Principal.equal, Principal.hash);
    var nextProposalId : Nat = 0;

    transient var event_details : ?Types.ValidatedEventData = null;
    transient var factory_principal : ?Principal = null;

    // initialize tidak perlu msg di sini (kamu tidak pakai msg.caller)
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
        var results = Buffer.Buffer<EventDefs.ProposalInfo>(proposals.size());
        for ((_, proposal) in proposals.entries()) {
            let info : EventDefs.ProposalInfo = {
                id = proposal.id;
                proposer = proposal.proposer;
                title = proposal.title;
                description = proposal.description;
                amount_requested = proposal.amount_requested;
                recipient_wallet = proposal.recipient_wallet;
                votes_for = proposal.votes_for;
                votes_against = proposal.votes_against;
                is_executed = proposal.is_executed;
            };
            results.add(info);
        };
        return Buffer.toArray(results);
    };

    public shared(msg) func submit_proposal(title: Text, description: Text, amount: Nat, recipient: Principal) : async Text {
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

    public shared(msg) func donate(amount: Nat) : async Text {
        let prev = donors.get(msg.caller);
        switch (prev) {
            case (null) {
                donors.put(msg.caller, amount);
            };
            case (?old) {
                donors.put(msg.caller, old + amount);
            };
        };
        treasury_balance := treasury_balance + amount;
        return "Donation received.";
    };

    public shared(msg) func vote(proposalId: EventDefs.ProposalId, in_favor: Bool) : async Text {
        if (donors.get(msg.caller) == null) {
            return "Only donors can vote.";
        };

        let maybe = proposals.get(proposalId);
        switch (maybe) {
            case (null) { return "Proposal not found."; };
            case (?proposal_ref) {
                let proposal = proposal_ref;
                if (proposal.voters.get(msg.caller) != null) {
                    return "You have already voted on this proposal.";
                };

                proposal.voters.put(msg.caller, true);

                let updated = if (in_favor) {
                    {
                        id = proposal.id;
                        proposer = proposal.proposer;
                        title = proposal.title;
                        description = proposal.description;
                        amount_requested = proposal.amount_requested;
                        recipient_wallet = proposal.recipient_wallet;
                        votes_for = proposal.votes_for + 1;
                        votes_against = proposal.votes_against;
                        voters = proposal.voters;
                        is_executed = proposal.is_executed;
                    }
                } else {
                    {
                        id = proposal.id;
                        proposer = proposal.proposer;
                        title = proposal.title;
                        description = proposal.description;
                        amount_requested = proposal.amount_requested;
                        recipient_wallet = proposal.recipient_wallet;
                        votes_for = proposal.votes_for;
                        votes_against = proposal.votes_against + 1;
                        voters = proposal.voters;
                        is_executed = proposal.is_executed;
                    }
                };

                proposals.put(proposalId, updated);

                await try_execute_proposal(proposalId);
                return "Vote cast successfully.";
            };
        };
    };

    private func try_execute_proposal(proposalId: EventDefs.ProposalId) : async () {
        let maybe = proposals.get(proposalId);
        switch (maybe) {
            case (?proposal_ref) {
                let proposal = proposal_ref;
                if (proposal.votes_for > 5 and not proposal.is_executed) {
                    if (treasury_balance >= proposal.amount_requested) {
                        treasury_balance := treasury_balance - proposal.amount_requested;
                        let updated = {
                            id = proposal.id;
                            proposer = proposal.proposer;
                            title = proposal.title;
                            description = proposal.description;
                            amount_requested = proposal.amount_requested;
                            recipient_wallet = proposal.recipient_wallet;
                            votes_for = proposal.votes_for;
                            votes_against = proposal.votes_against;
                            voters = proposal.voters;
                            is_executed = true;
                        };
                        proposals.put(proposalId, updated);
                    };
                };
            };
            case (_) {};
        };
    };
};
