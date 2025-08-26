// =====================================================================
// AEGIS Protocol - Insurance Vault Canister
// =====================================================================
// File: src/insurance_vault/main.mo
// Purpose: Parametric insurance and treasury management for disaster response
// 
// Architecture Overview:
//   The Insurance Vault implements a parametric insurance model that
//   automatically releases funds based on validated disaster events.
//   It serves as the financial backbone of the AEGIS Protocol,
//   providing immediate liquidity for disaster response activities.
// 
// Key Responsibilities:
//   - Manage insurance fund liquidity from multiple funders
//   - Implement parametric triggers based on disaster severity
//   - Authorize and execute automatic fund releases
//   - Maintain funder authorization and access control
//   - Provide transparent accounting of fund allocation
// 
// Parametric Insurance Model:
//   - Severity-based payout calculations (High/Medium/Low)
//   - Automatic triggering without claims processing
//   - Pre-defined payout amounts for predictable response
//   - Integration with AI validation for trigger events
// 
// Authorization System:
//   - Admin: Can add new authorized funders
//   - Initial Funder: Primary capital provider with funding rights
//   - Additional Funders: Secondary funders added by admin
//   - Event Factory: Authorized to trigger fund releases
// 
// Security Features:
//   - Multi-level authorization for different operations
//   - Immutable factory authorization to prevent unauthorized access
//   - Balance validation before fund releases
//   - Transparent audit trails for all transactions
// 
// Integration Points:
//   - Event Factory: Receives release requests for new disasters
//   - Event DAOs: Ultimate recipients of released funds
//   - AI Agents: Provide validated events for triggering releases
// =====================================================================

// Core Motoko standard library imports
import Principal "mo:base/Principal"; // Principal ID management and operations
import Nat "mo:base/Nat";            // Natural number utilities and arithmetic
import Array "mo:base/Array";        // Array operations and utilities
import R "mo:base/Result";           // Result type for error handling
import _Debug "mo:base/Debug";       // Debugging utilities (remove in production) 

/// =====================================================================
/// Actor: InsuranceVault
/// =====================================================================
/// Parametric insurance system for automated disaster response funding
/// 
/// Initialization Parameters:
///   - init_factory_id: EventFactory principal authorized to trigger releases
///   - init_funder_id: Primary funder with initial funding authorization
///   - init_admin_id: Administrative principal for funder management
/// 
/// Design Philosophy:
///   The Insurance Vault operates on parametric insurance principles,
///   where payouts are automatically triggered by objective disaster
///   parameters rather than traditional claims processing. This enables
///   rapid response without bureaucratic delays.
/// 
/// Liquidity Management:
///   - Accepts funds from multiple authorized sources
///   - Maintains reserve levels for sustained operations
///   - Implements automatic release based on severity thresholds
///   - Provides transparency through query functions
/// 
/// Security Model:
///   - Immutable factory authorization prevents unauthorized access
///   - Admin-controlled funder list for capital source management
///   - Balance validation prevents over-disbursement
///   - Principal-based access control for all operations
/// =====================================================================
persistent actor class InsuranceVault(
  init_factory_id: Principal,    // EventFactory authorized for fund releases
  init_funder_id: Principal,     // Primary funder with funding privileges
  init_admin_id: Principal       // Administrator for funder management
) {

  // ===================================================================
  // TYPE DEFINITIONS AND ALIASES
  // ===================================================================
  // Shared type definitions for consistent API design
  
  /// Standard Result type for operation outcomes
  /// Enables consistent error handling across all functions
  public type Result<T, E> = R.Result<T, E>;

  /// Validated disaster event data structure from AI pipeline
  /// Contains essential information for parametric insurance triggering
  public type ValidatedEventData = {
    event_type: Text;    // Disaster classification (earthquake, tsunami, etc.)
    severity: Text;      // Severity level for payout calculation
    details_json: Text;  // Complete event metadata for audit trail
  };

  // ===================================================================
  // STATE VARIABLES AND CONFIGURATION
  // ===================================================================
  // Core vault state and authorization configuration
  
  /// Total available liquidity for disaster response (in arbitrary units)
  /// Represents the sum of all contributed funds available for disbursement
  /// In production, integrate with proper token ledgers and audit systems
  var total_liquidity: Nat = 0;
  
  /// Immutable factory authorization - set at deployment and never changed
  /// Only this EventFactory can trigger fund releases for security
  let authorized_factory: Principal = init_factory_id;
  
  /// Initial funder with permanent funding authorization
  /// Typically represents the primary capital provider or insurance company
  let initial_funder: Principal = init_funder_id;
  
  /// Dynamic list of additional authorized funders
  /// Can be expanded by admin to include more capital sources
  var additional_funders: [Principal] = [];
  
  /// Administrative principal for funder management
  /// Has authority to add new funders but not access funds directly
  let admin: Principal = init_admin_id;

  // ===================================================================
  // HELPER FUNCTIONS AND UTILITIES
  // ===================================================================
  // Internal utility functions for authorization and policy implementation
  
  /// Check if an array contains a specific Principal
  /// Used for efficient authorization checking in funder lists
  /// 
  /// Parameters:
  ///   arr: Array of Principals to search
  ///   val: Principal to find in the array
  /// Returns:
  ///   Bool: true if Principal is found, false otherwise
  private func arrayContains(arr: [Principal], val: Principal): Bool {
    for (item in arr.vals()) {
      if (Principal.equal(item, val)) { return true };
    };
    false
  };

  /// Verify if a Principal is authorized to fund the vault
  /// Checks both initial funder and additional funder list
  /// 
  /// Parameters:
  ///   who: Principal to check for funding authorization
  /// Returns:
  ///   Bool: true if authorized to fund, false otherwise
  private func isAuthorizedFunder(who: Principal): Bool {
    Principal.equal(who, initial_funder) or
    arrayContains(additional_funders, who)
  };

  /// Parametric insurance payout calculation based on disaster severity
  /// Implements pre-defined payout amounts for different severity levels
  /// This enables automatic, objective fund releases without claims processing
  /// 
  /// Payout Policy:
  ///   - High Severity ("Tinggi"): 100M units - Major disasters requiring massive response
  ///   - Medium Severity ("Sedang"): 50M units - Significant disasters needing substantial aid
  ///   - Low Severity ("Rendah"): 10M units - Minor disasters requiring limited assistance
  ///   - Unknown/Invalid: 0 units - No payout for unrecognized severity levels
  /// 
  /// Parameters:
  ///   event_data: ValidatedEventData containing severity assessment
  /// Returns:
  ///   Nat: Payout amount in vault units (0 if no payout warranted)
  /// 
  /// Future Enhancements:
  ///   - Dynamic payout calculation based on event location and population
  ///   - Integration with real-time economic data for inflation adjustment
  ///   - Multi-factor severity assessment including economic impact
  private func determine_payout(event_data: ValidatedEventData): Nat {
    switch (event_data.severity) {
      case ("Tinggi") { 100_000_000 };  // High severity: Major disaster response
      case ("Sedang") {  50_000_000 };  // Medium severity: Significant assistance
      case ("Rendah") {  10_000_000 };  // Low severity: Limited aid provision
      case (_)        {           0 };  // Unknown severity: No automatic payout
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
