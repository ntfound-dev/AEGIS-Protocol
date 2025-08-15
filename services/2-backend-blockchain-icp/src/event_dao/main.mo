// File: services/2-backend-blockchain-icp/src/event_dao/main.mo

import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Trie "mo:base/Trie";
import Result "mo:base/Result";
import Array "mo:base/Array";
import Option "mo:base/Option";

actor class EventDAO (init_args : EventDAO.InitArgs) {

    // --- STATE DARI DAO ---
    stable var treasury_balance: Nat = 0;
    // --- PERBAIKAN: Menggunakan Trie.empty() untuk inisialisasi ---
    stable var donors = Trie.empty<Principal, Nat>();

    public type ProposalId = Nat;
    public stable type Proposal = {
        id: ProposalId;
        proposer: Principal;
        title: Text;
        description: Text;
        amount_requested: Nat;
        recipient_wallet: Principal;
        var votes_for: Nat;         // Dijadikan 'var' agar bisa diubah
        var votes_against: Nat;     // Dijadikan 'var' agar bisa diubah
        var voters: Trie<Principal, Bool>; // Dijadikan 'var' agar bisa diubah
        var is_executed: Bool;      // Dijadikan 'var' agar bisa diubah
    };
    // --- PERBAIKAN: Menggunakan Trie.empty() untuk inisialisasi ---
    stable var proposals = Trie.empty<ProposalId, Proposal>();
    stable var nextProposalId: ProposalId = 0;

    // Tipe ini harus cocok dengan yang ada di EventFactory
    public type ValidatedEventData = {
        event_type: Text;
        severity: Text;
        details_json: Text;
    };
    
    public type InitArgs = {
        event_data: ValidatedEventData;
        factory_principal: Principal;
    };
    
    // Menyimpan argumen inisialisasi
    stable let event_details : ValidatedEventData = init_args.event_data;
    stable let factory_principal: Principal = init_args.factory_principal;

    // --- FUNGSI PUBLIK ---
    public shared(msg) query func get_event_details() : async ValidatedEventData {
        return event_details;
    };
    
    public shared(msg) query func get_all_proposals() : async [Proposal] {
        return proposals.values(); // Cara lebih singkat untuk mendapatkan semua value
    };

    public shared(msg) func donate(amount: Nat) : async Text {
        treasury_balance += amount;
        let current_donation = Option.get(donors.get(msg.caller), 0);
        donors.put(msg.caller, current_donation + amount);
        return "Thank you for your donation!";
    };

    public shared(msg) func submit_proposal(title: Text, description: Text, amount: Nat, recipient: Principal) : async Text {
        let proposal : Proposal = {
            id = nextProposalId;
            proposer = msg.caller;
            title = title;
            description = description;
            amount_requested = amount;
            recipient_wallet = recipient;
            votes_for = 0;
            votes_against = 0;
            // --- PERBAIKAN: Menggunakan Trie.empty() untuk inisialisasi ---
            voters = Trie.empty<Principal, Bool>();
            is_executed = false;
        };
        proposals.put(nextProposalId, proposal);
        nextProposalId += 1;
        return "Proposal submitted with ID: " # Nat.toText(proposal.id);
    };

    public shared(msg) func vote(proposalId: ProposalId, in_favor: Bool) : async Text {
        if (donors.get(msg.caller) == null) { return "Only donors can vote."; };

        switch (proposals.get(proposalId)) {
            case (null) { return "Proposal not found."; };
            case (?proposal) {
                if (proposal.voters.get(msg.caller) != null) {
                    return "You have already voted on this proposal.";
                };
                
                // Karena field di tipe Proposal adalah 'var', kita bisa langsung mengubahnya
                if (in_favor) {
                    proposal.votes_for += 1;
                } else {
                    proposal.votes_against += 1;
                };
                proposal.voters.put(msg.caller, true);
                
                // Tidak perlu put() lagi karena kita memodifikasi record secara langsung
                
                try_execute_proposal(proposalId);
                return "Vote cast successfully.";
            };
        };
    };
    
    private func try_execute_proposal(proposalId: ProposalId) {
        switch (proposals.get(proposalId)) {
            case (?proposal) {
                // Gunakan 'and not' untuk kondisi boolean
                if (proposal.votes_for > 5 and not proposal.is_executed) {
                    if (treasury_balance >= proposal.amount_requested) {
                        treasury_balance -= proposal.amount_requested;
                        // --- PERBAIKAN: Gunakan '=' untuk mengubah field record ---
                        proposal.is_executed = true;
                        // Tidak perlu put() lagi
                    }
                }
            };
            case (_) {};
        };
    };
}