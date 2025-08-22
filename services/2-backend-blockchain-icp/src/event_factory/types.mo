// src/types.mo
import Principal "mo:base/Principal";

module Types {
  public type ValidatedEventData = {
    event_type: Text;
    severity: Text;
    details_json: Text;
  };

  public type InitArgs = {
    event_data: ValidatedEventData;
    factory_principal: Principal;
  };
};
