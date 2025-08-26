export const idlFactory = ({ IDL }) => {
  const ProposalId = IDL.Nat;
  const ProposalInfo = IDL.Record({
    'id' : IDL.Nat,
    'title' : IDL.Text,
    'is_executed' : IDL.Bool,
    'amount_requested' : IDL.Nat,
    'description' : IDL.Text,
    'recipient_wallet' : IDL.Principal,
    'proposer' : IDL.Principal,
    'votes_for' : IDL.Nat,
    'votes_against' : IDL.Nat,
  });
  const ValidatedEventData = IDL.Record({
    'details_json' : IDL.Text,
    'severity' : IDL.Text,
    'event_type' : IDL.Text,
  });
  const InitArgs = IDL.Record({
    'factory_principal' : IDL.Principal,
    'event_data' : ValidatedEventData,
  });
  return IDL.Service({
    'donate' : IDL.Func([IDL.Nat], [IDL.Text], []),
    'donateAndVote' : IDL.Func([IDL.Nat, ProposalId, IDL.Bool], [IDL.Text], []),
    'get_all_proposals' : IDL.Func([], [IDL.Vec(ProposalInfo)], ['query']),
    'get_event_details' : IDL.Func(
        [],
        [IDL.Opt(ValidatedEventData)],
        ['query'],
      ),
    'initialize' : IDL.Func([InitArgs], [IDL.Text], []),
    'submit_proposal' : IDL.Func(
        [IDL.Text, IDL.Text, IDL.Nat, IDL.Principal],
        [IDL.Text],
        [],
      ),
  });
};
export const init = ({ IDL }) => { return []; };
