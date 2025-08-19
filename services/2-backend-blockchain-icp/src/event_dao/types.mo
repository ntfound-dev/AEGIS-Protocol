import Principal "mo:base/Principal";

type ValidatedEventData = {
  event_type: Text;
  severity: Text;
  details_json: Text;
};

type InitArgs = {
  event_data: ValidatedEventData;
  factory_principal: Principal;
};