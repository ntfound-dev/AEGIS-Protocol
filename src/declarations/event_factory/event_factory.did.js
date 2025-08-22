export const idlFactory = ({ IDL }) => {
  const ValidatedEventData = IDL.Record({
    'details_json' : IDL.Text,
    'severity' : IDL.Text,
    'event_type' : IDL.Text,
  });
  const DeclareEventResult = IDL.Variant({
    'ok' : IDL.Principal,
    'err' : IDL.Text,
  });
  const EventFactory = IDL.Service({
    'declare_event' : IDL.Func([ValidatedEventData], [DeclareEventResult], []),
  });
  return EventFactory;
};
export const init = ({ IDL }) => { return []; };
