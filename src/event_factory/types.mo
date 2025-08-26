import Principal "mo:base/Principal";

/// ------------------------------------------------------------
/// Module: Types
/// Description:
///   Defines core data structures used across EventDAO.
///   Keeps event-related and initialization data centralized
///   for easier maintenance and reuse.
/// ------------------------------------------------------------
module Types {

  /// ----------------------------------------------------------
  /// Represents validated metadata about an event.
  /// This data is injected by the Factory at initialization
  /// and used to describe the nature of the event.
  /// ----------------------------------------------------------
  public type ValidatedEventData = {
    /// Type of event (e.g., "Hackathon", "Conference", etc.)
    event_type: Text;

    /// Severity classification (e.g., "Low", "Medium", "High")
    severity: Text;

    /// Event details in JSON format (for flexible storage)
    details_json: Text;
  };

  /// ----------------------------------------------------------
  /// Arguments passed during initialization of the EventDAO.
  /// Ensures that the deployed instance has:
  ///   - Its event metadata
  ///   - A link back to the factory canister (for provenance)
  /// ----------------------------------------------------------
  public type InitArgs = {
    /// Metadata describing the event
    event_data: ValidatedEventData;

    /// Principal of the factory canister that created this DAO
    factory_principal: Principal;
  };
};
