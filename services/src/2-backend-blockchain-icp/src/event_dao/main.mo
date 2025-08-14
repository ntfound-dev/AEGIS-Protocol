// File: services/2-backend-blockchain-icp/src/event_dao/main.mo

import Map "mo:base/HashMap";
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Array "mo:base/Array";

// Impor tipe data dari factory agar konsisten.
import EventFactory "mo:../event_factory/main";

// Ini adalah canister DAO yang sebenarnya.
// Ia diinisialisasi dengan argumen yang dikirim oleh EventFactory.
actor EventDAO (init_args : EventDAO.InitArgs) {

    // --- STATE DARI DAO ---
    // Variabel-variabel ini akan menyimpan semua data DAO di dalam memori canister.

    // (D1) Treasury / Perbendaharaan
    private var treasury_balance: Nat = 0; // Saldo dana
    private var donors = Map.fromArray<Principal, Nat>([]); // Peta untuk melacak donatur dan jumlah donasinya

    // (D2) Governance / Tata Kelola
    public type ProposalId = Nat; // Tipe data untuk ID proposal
    public type Proposal = {
        id: ProposalId;
        proposer: Principal;        // ID dari NGO yang mengajukan
        title: Text;
        description: Text;
        amount_requested: Nat;      // Jumlah dana yang diminta
        recipient_wallet: Principal;// Dompet tujuan dana
        votes_for: Nat;             // Jumlah suara setuju
        votes_against: Nat;         // Jumlah suara tidak setuju
        voters: Map.HashMap<Principal, Bool>; // Melacak siapa saja yang sudah voting
        is_executed: Bool;          // Status apakah proposal sudah dieksekusi
    };
    private var proposals = Map.fromArray<ProposalId, Proposal>([]); // Peta untuk menyimpan semua proposal
    private var nextProposalId: ProposalId = 0;

    // Tipe data untuk argumen inisialisasi, agar bisa diakses oleh EventFactory
    public type InitArgs = {
        event_data: EventFactory.ValidatedEventData;
        factory_principal: Principal;
    };

    // --- FUNGSI PUBLIK (Bisa dipanggil dari luar) ---

    // Fungsi 'query' hanya untuk membaca data, sangat cepat dan gratis.
    public shared(msg) query func get_event_details() : async EventFactory.ValidatedEventData {
        return init_args.event_data;
    };
    
    public shared(msg) query func get_all_proposals() : async [Proposal] {
        return Array.fromVar(proposals.vals());
    };

    // Fungsi untuk menerima donasi.
    public shared(msg) func donate(amount: Nat) : async Text {
        // Simulasi penerimaan dana.
        treasury_balance += amount;

        // Mencatat donasi dari pemanggil (`msg.caller`).
        let current_donation = donors.get(msg.caller) ?? 0;
        donors.put(msg.caller, current_donation + amount);

        return "Thank you for your donation!";
    };

    // Fungsi untuk NGO mengajukan proposal kebutuhan.
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

    // Fungsi untuk anggota (donatur) melakukan voting.
    public shared(msg) func vote(proposalId: ProposalId, in_favor: Bool) : async Text {
        if (donors.get(msg.caller) == null) { return "Only donors can vote."; };

        switch (proposals.get(proposalId)) {
            case (null) { return "Proposal not found."; };
            case (?proposal) {
                if (proposal.voters.get(msg.caller) != null) {
                    return "You have already voted on this proposal.";
                };

                var mutable_proposal = proposal;
                if (in_favor) {
                    mutable_proposal.votes_for += 1;
                } else {
                    mutable_proposal.votes_against += 1;
                };
                mutable_proposal.voters.put(msg.caller, true);
                proposals.put(proposalId, mutable_proposal);

                try_execute_proposal(proposalId);
                return "Vote cast successfully.";
            };
        };
    };

    // --- FUNGSI INTERNAL (Hanya bisa dipanggil dari dalam canister ini) ---

    private func try_execute_proposal(proposalId: ProposalId) {
        let proposal_opt = proposals.get(proposalId);
        if (proposal_opt != null) {
            var proposal = proposal_opt!;
            if (proposal.votes_for > 5 and not proposal.is_executed) {
                if (treasury_balance >= proposal.amount_requested) {
                    treasury_balance -= proposal.amount_requested;
                    proposal.is_executed = true;
                    proposals.put(proposalId, proposal);
                }
            }
        };
    };
}