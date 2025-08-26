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

/// ------------------------------------------------------------------
/// Helpers and utilities
/// ------------------------------------------------------------------

/// ------------------------------------------------------------------
/// Persistent actor
/// ------------------------------------------------------------------

persistent actor EventDAO {

    // customNatHash
    // - Adapter hash function for TrieMap keys of type Nat
    // - Converts to Nat32 to ensure a 32-bit hash value
    // === CHANGED === helper moved here (was top-level) ===
    private func customNatHash(n : Nat) : Hash.Hash { Nat32.fromNat(n % 4294967296); };



    // treasury_balance
    // - Total recorded donations held by the DAO (units = arbitrary Nat)
    // NOTE: If real funds are involved, integrate proper bookkeeping and audits.
    var treasury_balance : Nat = 0;

    // proposals
    // - TrieMap storing proposals by id (Nat)
    // - Transient: data marked transient will not survive upgrades; if you need
    //   persistence across upgrades, remove 'transient' or use stable storage patterns.
    // TODO: consider adding secondary indexes (by proposer, executed flag, etc.)
    transient var proposals : TrieMap.TrieMap<Nat, EventDefs.Proposal> =
        TrieMap.TrieMap<Nat, EventDefs.Proposal>(Nat.equal, customNatHash);

    // donors
    // - Map donor Principal -> total donated amount
    transient var donors : TrieMap.TrieMap<Principal, Nat> =
        TrieMap.TrieMap<Principal, Nat>(Principal.equal, Principal.hash);

    // nextProposalId: incrementing counter for proposal IDs
    var nextProposalId : Nat = 0;

    // event_details
    // - Optional event metadata (e.g. event name, type)
    // - Stored transiently; if persistence across upgrades is required, adapt strategy.
    transient var event_details : ?Types.ValidatedEventData = null;

    // factory_principal
    // - Optional principal that represents the factory or deployer
    // FIXME: currently no access control — consider restricting initialize() to a specific principal.
    transient var factory_principal : ?Principal = null;

    /// ------------------------------------------------------------------
    /// Initialization
    /// ------------------------------------------------------------------

    /* initialize
     * - Sets up the canister with initial values provided by deployer/factory
     * @param args: Types.InitArgs containing optional factory_principal and event_data
     * @return Text: status message. Repeated initialization is guarded.
     * NOTE: This function is idempotent: calling it again returns a message without changing state.
     */
    public shared func initialize(args: Types.InitArgs) : async Text {
        if (factory_principal != null) {
            return "Already initialized.";
        };
        factory_principal := ?args.factory_principal;
        event_details := ?args.event_data;
        return "Initialized.";
    };

    /// ------------------------------------------------------------------
    /// Queries (read-only)
    /// ------------------------------------------------------------------

    // get_event_details
    // - Returns optional event metadata
    public shared query func get_event_details() : async ?Types.ValidatedEventData {
        return event_details;
    };

    // get_all_proposals
    // - Returns an array of ProposalInfo suitable for UI consumption
    // NOTE: For large numbers of proposals consider pagination or range queries.
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

    /// ------------------------------------------------------------------
    /// Mutations / public entrypoints
    /// ------------------------------------------------------------------

    /* submit_proposal
     * - Create a new proposal.
     * @param title, description, amount, recipient
     * @return Text status message
     * NOTE: No validation is performed on title or amount here — add checks if needed.
     */
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

    /* donateAndVote
     * - Combined flow: donate and cast a vote on a proposal
     * Flow:
     *   1) _donate -> update donor map & treasury
     *   2) _vote -> cast vote (async)
     *   3) mint SBT to caller via SbtLedger canister
     * Error handling: currently traps if voting fails — consider returning an error instead.
     */
    public shared(msg) func donateAndVote(
        amount: Nat,
        proposalId: EventDefs.ProposalId,
        in_favor: Bool
    ) : async Text {
        _donate(msg.caller, amount);
        let vote_msg = await _vote(msg.caller, proposalId, in_favor);
        if (vote_msg != "Vote cast successfully.") {
            // FIXME: Debug.trap will abort the call and revert state from the caller's perspective.
            // It may be preferable to return an error message so the donor's donation is not lost silently.
            Debug.trap("Voting failed: " # vote_msg);
        };

        let event_name = switch(event_details) {
            case (?details) { details.event_type };
            case (null) { "Unknown Event" };
        };

        // Call SBT canister to mint a participation token
        let mint_result = await SbtLedger.mint_sbt(
            msg.caller,
            event_name,
            "Donor & Participant"
        );
        
        switch (mint_result) {
          case (#ok(_mint_message)) {
            return "Thank you! Donation and vote have been recorded. Your participation SBT has been minted.";
          };
          case (#err(error_message)) {
            // Return success for donation/vote but report minting failure
            return "Vote and donation succeeded, but SBT minting failed: " # error_message;
          };
        };
    };

    /// ------------------------------------------------------------------
    /// Internal helpers
    /// ------------------------------------------------------------------

    // _donate
    // - Update donor map & treasury
    // NOTE: No validation performed (e.g. amount > 0)
    private func _donate(caller: Principal, amount: Nat) {
        switch (donors.get(caller)) {
            case (null) { donors.put(caller, amount); };
            case (?old) { donors.put(caller, old + amount); };
        };
        treasury_balance += amount;
    };
   
    // donate
    // - Public wrapper for donations
    public shared(msg) func donate(amount: Nat) : async Text {
        _donate(msg.caller, amount);
        return "Thank you for your donation of " # Nat.toText(amount) # " units.";
    };

    /* _vote
     * - Private async function to record a vote
     * - Checks for proposal existence and whether caller has already voted
     * - After recording the vote, attempts to execute the proposal (fire-and-forget)
     * - Returns Text message for caller feedback
     */
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
                // Fire-and-forget execution attempt. If execution fails, caller won't be notified.
                ignore try_execute_proposal(proposalId);
                return "Vote cast successfully.";
            };
        };
    };

    /* try_execute_proposal
     * - Executes a proposal when votes_for passes the threshold
     * - Threshold and transfer mechanics are currently hardcoded (votes_for > 5)
     * TODO: make threshold a configurable constant and emit events/logs on execution
     */
    private func try_execute_proposal(proposalId: EventDefs.ProposalId) : async () {
        switch (proposals.get(proposalId)) {
            case (?proposal) {
                if (proposal.votes_for > 5 and not proposal.is_executed) {
                    if (treasury_balance >= proposal.amount_requested) {
                        treasury_balance -= proposal.amount_requested;
                        let updated = { proposal with is_executed = true };
                        proposals.put(proposalId, updated);
                        // NOTE: At this point, a real transfer to the recipient_wallet should occur
                        // (e.g. via a ledger canister), along with a receipt/event log.
                    };
                };
            };
            case (_) {};
        };
    };
};

// End of file
// Quick improvement checklist (non-exhaustive):
// - Add input validation (e.g. amount > 0, non-empty title)
// - Replace Debug.trap with proper error returns and caller-friendly messaging
// - Add event logs for important state transitions (proposal created, executed)
// - Add access control for initialize / admin-only operations
// - Introduce configuration constants (vote threshold, minimum donation, etc.)
