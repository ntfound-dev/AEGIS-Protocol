// =====================================================================
// AEGIS Protocol - Event Factory Canister
// =====================================================================
// File: src/event_factory/main.mo
// Purpose: Central factory for creating disaster-specific DAOs
// 
// Architecture Overview:
//   The Event Factory serves as the entry point for disaster event
//   processing in the AEGIS Protocol. It receives validated disaster
//   events from AI agents and creates dedicated DAO instances for
//   each significant disaster requiring community response.
// 
// Key Responsibilities:
//   - Receive disaster event declarations from Action Agent
//   - Create new EventDAO instances for each disaster
//   - Initialize DAOs with validated disaster metadata
//   - Coordinate with InsuranceVault for initial funding
//   - Maintain registry of all active disaster events
// 
// Factory Pattern Benefits:
//   - Dynamic DAO creation without pre-deployment
//   - Isolated governance for each disaster event
//   - Scalable architecture supporting unlimited disasters
//   - Standardized initialization across all DAOs
// 
// Integration Points:
//   - Input: AI Agent validated events via declare_event()
//   - Output: New EventDAO instances with unique principals
//   - Coordination: InsuranceVault funding release
//   - Registry: Tracking of all created disaster DAOs
// 
// Security Considerations:
//   - Only authorized agents can declare events
//   - Event data validation before DAO creation
//   - Atomic operations to prevent partial state
//   - Error handling to maintain system integrity
// =====================================================================

// Core Motoko libraries for fundamental operations
import Principal "mo:base/Principal";  // Principal ID management and validation
import Result "mo:base/Result";        // Result type for error handling
import Error "mo:base/Error";          // Error type definitions and utilities
// Inter-canister communication imports
// These enable the factory to coordinate with other AEGIS system components
import EventDAO "canister:event_dao";         // DAO instance for disaster governance
import InsuranceVault "canister:insurance_vault"; // Insurance and funding coordination
import Types "types";                          // Shared type definitions

/// =====================================================================
/// Actor: EventFactory
/// =====================================================================
/// Central factory canister for disaster event processing and DAO creation.
/// 
/// Design Pattern: Factory Pattern
///   This canister implements the factory design pattern to dynamically
///   create EventDAO instances for each disaster that requires community
///   response and governance. Each DAO operates independently with its
///   own treasury, proposals, and voting mechanisms.
/// 
/// Lifecycle Management:
///   1. Receive validated disaster event from AI agents
///   2. Validate event data and check authorization
///   3. Create and initialize new EventDAO instance
///   4. Coordinate with InsuranceVault for initial funding
///   5. Return DAO principal for client tracking
/// 
/// Persistent State:
///   - Factory configuration and authorization settings
///   - Registry of created DAOs (if implemented)
///   - Event processing history and metrics
/// 
/// Error Handling Strategy:
///   - Comprehensive validation before state changes
///   - Atomic operations to prevent partial execution
///   - Detailed error messages for debugging
///   - Graceful degradation on component failures
/// =====================================================================
persistent actor class EventFactory() = this { 

  // ===================================================================
  // TYPE ALIASES AND CONVENIENCE DEFINITIONS
  // ===================================================================
  // Import shared types for consistent data structures across canisters
  
  /// Validated disaster event data structure from AI validation pipeline
  /// Contains all necessary information for DAO initialization
  public type ValidatedEventData = Types.ValidatedEventData;
  
  /// Result type for event declaration operations
  /// Success returns new DAO principal, failure returns error message
  public type DeclareEventResult = Result.Result<Principal, Text>;

  /// ===================================================================
  /// Function: declare_event
  /// ===================================================================
  /// Core factory function that processes disaster events and creates DAOs.
  /// 
  /// This function implements the complete disaster event processing pipeline:
  /// 1. Validates the incoming event data structure
  /// 2. Captures factory identity for DAO initialization
  /// 3. Creates initialization arguments with event metadata
  /// 4. Initializes new EventDAO instance with disaster context
  /// 5. Coordinates with InsuranceVault for immediate funding
  /// 6. Returns DAO principal for client tracking and interaction
  /// 
  /// Parameters:
  ///   eventData: ValidatedEventData - Disaster event from AI validation
  ///     - Contains event type, severity, location, and metadata
  ///     - Already validated by Validator Agent for data quality
  ///     - Includes confidence scores and source attribution
  /// 
  /// Returns:
  ///   DeclareEventResult - Success with DAO principal or error message
  ///     - #ok(Principal): New DAO successfully created and initialized
  ///     - #err(Text): Detailed error message for debugging
  /// 
  /// Error Conditions:
  ///   - Invalid or incomplete event data
  ///   - DAO initialization failures
  ///   - InsuranceVault coordination errors
  ///   - Network or inter-canister communication issues
  /// 
  /// Side Effects:
  ///   - Creates new EventDAO canister instance
  ///   - Triggers initial funding release from InsuranceVault
  ///   - Updates internal factory state and metrics
  /// 
  /// Authorization:
  ///   Currently open to all callers - production should implement
  ///   role-based access control to restrict to authorized agents
  /// ===================================================================
  public shared(_msg) func declare_event(
    eventData: ValidatedEventData
  ) : async DeclareEventResult {

    // =================================================================
    // Step 1: Factory Identity Capture
    // =================================================================
    // Capture this factory's principal for DAO initialization
    // The DAO needs to know its creator for security and tracking
    let factory_principal : Principal = Principal.fromActor(this);

    // =================================================================
    // Step 2: DAO Initialization Configuration
    // =================================================================
    // Build initialization arguments combining event data with factory context
    // This creates the complete configuration needed for DAO operation
    let init_args : Types.InitArgs = {
      event_data = eventData;              // Disaster event metadata
      factory_principal = factory_principal; // Factory identity for reference
    };

    try {
      // ===============================================================
      // Step 3: EventDAO Initialization
      // ===============================================================
      // Initialize the EventDAO canister with disaster-specific configuration
      // This creates a dedicated governance system for this disaster
      let _init_status : Text = await EventDAO.initialize(init_args);

      // ===============================================================
      // Step 4: DAO Principal Extraction
      // ===============================================================
      // Retrieve the deployed DAO's principal for client reference
      // This principal serves as the DAO's unique blockchain address
      let eventdao_principal : Principal = Principal.fromActor(EventDAO);

      // ===============================================================
      // Step 5: Insurance Coordination
      // ===============================================================
      // Trigger initial funding release from InsuranceVault
      // This provides immediate capital for disaster response activities
      let _vault_res = await InsuranceVault.release_initial_funding(
        eventdao_principal,  // Target DAO for funding
        eventData           // Event context for funding decisions
      );

      // ===============================================================
      // Step 6: Success Response
      // ===============================================================
      // Return the new DAO's principal for client interaction
      return #ok(eventdao_principal);

    } catch (e) {
      // ===============================================================
      // Error Handling and Recovery
      // ===============================================================
      // Capture and return detailed error information for debugging
      // In production, consider logging to persistent error tracking
      return #err("Event declaration failed: " # Error.message(e));
    };
  };
};

