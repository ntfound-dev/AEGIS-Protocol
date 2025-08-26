import Principal "mo:base/Principal";

/// ------------------------------------------------------------
/// Type: ValidatedEventData
/// Description:
///   Structured event information that has already been validated.
///   Used by the EventFactory and InsuranceVault when determining payouts.
/// ------------------------------------------------------------
public type ValidatedEventData = {
  /// Category/type of the event (e.g., "Flood", "Earthquake", "Hack").
  event_type: Text;

  /// Severity level of the event (e.g., "Tinggi", "Sedang", "Rendah").
  severity: Text;

  /// Additional event details in JSON format (structured metadata).
  details_json: Text;
};

/// ------------------------------------------------------------
/// Type: InitArgs
/// Description:
///   Arguments required when initializing an EventDAO actor.
///   Provided by EventFactory upon DAO creation.
/// ------------------------------------------------------------
public type InitArgs = {
  /// The validated event data that defines the DAO’s purpose.
  event_data: ValidatedEventData;

  /// The EventFactory principal that created this DAO.
  factory_principal: Principal;
};
