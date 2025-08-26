import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Error "mo:base/Error";
import EventDAO "canister:event_dao";
import InsuranceVault "canister:insurance_vault"; 
import Types "types";

/// ------------------------------------------------------------
/// Actor: EventFactory
/// Description:
///   - Factory actor responsible for declaring new events.
///   - Each event corresponds to an EventDAO instance,
///     initialized with validated event metadata.
///   - Also coordinates with InsuranceVault to release initial funding.
/// ------------------------------------------------------------
persistent actor class EventFactory() = this { 

  // -----------------------------
  // Type Aliases for convenience
  // -----------------------------
  public type ValidatedEventData = Types.ValidatedEventData;
  public type DeclareEventResult = Result.Result<Principal, Text>;

  /// ----------------------------------------------------------
  /// Function: declare_event
  /// Description:
  ///   Declares a new event and deploys an EventDAO instance.
  ///   Steps:
  ///     1. Capture the factory's principal.
  ///     2. Build initialization arguments for EventDAO.
  ///     3. Initialize EventDAO with event metadata.
  ///     4. Notify InsuranceVault to release initial funding.
  ///     5. Return the EventDAO's principal if successful.
  /// Error Handling:
  ///   Returns a `#err` with the failure reason if any step fails.
  /// ----------------------------------------------------------
  public shared(_msg) func declare_event(
    eventData: ValidatedEventData
  ) : async DeclareEventResult {

    // Step 1: Identify this factory's principal
    let factory_principal : Principal = Principal.fromActor(this);

    // Step 2: Build init args for EventDAO
    let init_args : Types.InitArgs = {
      event_data = eventData;
      factory_principal = factory_principal;
    };

    try {
      // Step 3: Initialize EventDAO with event metadata
      let _init_status : Text = await EventDAO.initialize(init_args);

      // Step 4: Retrieve deployed EventDAO principal
      let eventdao_principal : Principal = Principal.fromActor(EventDAO);

      // Step 5: Trigger InsuranceVault initial funding
      let _vault_res = await InsuranceVault.release_initial_funding(
        eventdao_principal,
        eventData
      );

      // Success: return new EventDAO principal
      return #ok(eventdao_principal);

    } catch (e) {
      // Failure: return captured error message
      return #err(Error.message(e));
    };
  };
};

