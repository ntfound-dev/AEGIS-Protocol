import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Array "mo:base/Array";
import R "mo:base/Result";
import _Debug "mo:base/Debug"; 

/// ------------------------------------------------------------
/// Actor: InsuranceVault
/// Description:
///   - Manages liquidity to back DAOs created by EventFactory.
///   - Handles authorized funders, vault funding, and event-based payouts.
///   - Liquidity is released to EventDAO based on event severity.
/// ------------------------------------------------------------
persistent actor class InsuranceVault(
  init_factory_id: Principal,
  init_funder_id: Principal,
  init_admin_id: Principal
) {

  // -----------------------------
  // Type Aliases
  // -----------------------------
  public type Result<T, E> = R.Result<T, E>;

  public type ValidatedEventData = {
    event_type: Text;
    severity: Text;
    details_json: Text;
  };

  // -----------------------------
  // State Variables
  // -----------------------------
  var total_liquidity: Nat = 0;
  let authorized_factory: Principal = init_factory_id;
  let initial_funder: Principal = init_funder_id;
  var additional_funders: [Principal] = [];
  let admin: Principal = init_admin_id;

  // -----------------------------
  // Helpers
  // -----------------------------
  private func arrayContains(arr: [Principal], val: Principal): Bool {
    for (item in arr.vals()) {
      if (Principal.equal(item, val)) { return true };
    };
    false
  };

  private func isAuthorizedFunder(who: Principal): Bool {
    Principal.equal(who, initial_funder) or
    arrayContains(additional_funders, who)
  };

  /// Determine payout based on severity policy.
  private func determine_payout(event_data: ValidatedEventData): Nat {
    switch (event_data.severity) {
      case ("Tinggi") { 100_000_000 }; 
      case ("Sedang") {  50_000_000 };
      case ("Rendah") {  10_000_000 };
      case (_)        {           0 };
    }
  };

  // -----------------------------
  // Public Functions
  // -----------------------------

  /// Add a new funder (only callable by admin).
  public shared(msg) func add_funder(
    funder_to_add: Principal
  ): async Result<Text, Text> {
    if (msg.caller != admin) {
      return #err("Unauthorized: only the admin can add new funders.");
    };

    if (isAuthorizedFunder(funder_to_add)) {
      return #ok("Funder already authorized.");
    };

    additional_funders := Array.append<Principal>(
      additional_funders,
      [funder_to_add]
    );
    return #ok("Funder added successfully.");
  };

  /// Fund the vault with liquidity (only by authorized funders).
  public shared(msg) func fund_vault(
    amount: Nat
  ): async Result<Text, Text> {
    if (amount == 0) {
      return #err("Amount must be greater than 0.");
    };
    if (not isAuthorizedFunder(msg.caller)) {
      return #err("Unauthorized: caller is not an authorized funder.");
    };

    total_liquidity += amount;
    return #ok(
      "Vault funded successfully. New balance: " #
      Nat.toText(total_liquidity)
    );
  };

  /// Release initial funding to a DAO (only callable by EventFactory).
  public shared(msg) func release_initial_funding(
    dao_canister_id: Principal,
    event_data: ValidatedEventData
  ): async Result<Text, Text> {
    if (msg.caller != authorized_factory) {
      return #err("Unauthorized: only the authorized EventFactory can call this function.");
    };

    let payout_amount = determine_payout(event_data);

    if (payout_amount == 0) {
      return #ok("Event severity does not meet policy for a payout.");
    };
    if (total_liquidity < payout_amount) {
      return #err("Insufficient liquidity in the vault.");
    };

    total_liquidity -= payout_amount;

    return #ok(
      "Successfully released " # Nat.toText(payout_amount) #
      " to DAO " # Principal.toText(dao_canister_id)
    );
  };

  // -----------------------------
  // Queries
  // -----------------------------
  public query func get_total_liquidity(): async Nat {
    total_liquidity
  };

  public query func get_authorized_funders(): async [Principal] {
    Array.append<Principal>([initial_funder], additional_funders)
  };
};
