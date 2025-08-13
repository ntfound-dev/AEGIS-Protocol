// src/event_dao/main.mo
import Map "mo:base/HashMap";
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";

// Impor tipe data dari factory
import EventFactory "event_factory";

actor EventDAO (init_args : EventFactory.EventDAOInitArgs) {

    // --- State dari DAO ---
    
    // (D1) Treasury
    private var treasury_balance: Nat = 0;
    private var donors = Map.fromArray<Principal, Nat>([]);

    // (D2) Governance
    private type ProposalId = Nat;
    public type Proposal = {
        id: ProposalId;
        proposer: Principal;
        title: Text;
        description: Text;
        amount_requested: Nat;
        recipient_wallet: Principal;
        votes_for: Nat;
        votes_against: Nat;
        voters: Map.HashMap<Principal, Bool>;
        is_executed: Bool;
    };
    private var proposals = Map.fromArray<ProposalId, Proposal>([]);
    private var nextProposalId: ProposalId = 0;

    // --- Fungsi Publik ---

    public shared(msg) query func get_event_details() : async EventFactory.ValidatedEventData {
        return init_args.event_data;
    };

    public shared(msg) func donate(amount: Nat) : async Text {
        // Simulasi penerimaan dana
        treasury_balance += amount;
        let current_donation = donors.get(msg.caller) ?? 0;
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
            voters = Map.fromArray<Principal, Bool>([]);
            is_executed = false;
        };
        proposals.put(nextProposalId, proposal);
        nextProposalId += 1;
        return "Proposal submitted with ID: " # Nat.toText(proposal.id);
    };

    public shared(msg) func vote(proposalId: ProposalId, in_favor: Bool) : async Text {
        // Cek apakah donatur (sederhana, harusnya anggota DAO)
        if (donors.get(msg.caller) == null) { return "Only donors can vote."; };
        
        switch (proposals.get(proposalId)) {
            case (null) { return "Proposal not found."; };
            case (?proposal) {
                if (proposal.voters.get(msg.caller) != null) {
                    return "You have already voted on this proposal.";
                };
                if (in_favor) {
                    proposal.votes_for += 1;
                } else {
                    proposal.votes_against += 1;
                };
                proposal.voters.put(msg.caller, true);
                proposals.put(proposalId, proposal);
                try_execute_proposal(proposalId);
                return "Vote cast successfully.";
            };
        };
    };

    // --- Fungsi Internal ---

    private func try_execute_proposal(proposalId: ProposalId) {
        let proposal = proposals.get(proposalId)!;
        // Aturan sederhana: jika suara 'setuju' > 5 dan belum dieksekusi
        if (proposal.votes_for > 5 and not proposal.is_executed) {
            if (treasury_balance >= proposal.amount_requested) {
                treasury_balance -= proposal.amount_requested;
                // Simulasi transfer dana
                // transfer_funds(proposal.recipient_wallet, proposal.amount_requested);
                proposal.is_executed = true;
                proposals.put(proposalId, proposal);
            }
        }
    };
}
