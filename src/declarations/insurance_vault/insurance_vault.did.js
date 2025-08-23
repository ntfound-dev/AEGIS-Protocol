export const idlFactory = ({ IDL }) => {
  const Result = IDL.Variant({ 'ok' : IDL.Text, 'err' : IDL.Text });
  const ValidatedEventData = IDL.Record({
    'details_json' : IDL.Text,
    'severity' : IDL.Text,
    'event_type' : IDL.Text,
  });
  const InsuranceVault = IDL.Service({
    'add_funder' : IDL.Func([IDL.Principal], [Result], []),
    'fund_vault' : IDL.Func([IDL.Nat], [Result], []),
    'get_authorized_funders' : IDL.Func(
        [],
        [IDL.Vec(IDL.Principal)],
        ['query'],
      ),
    'get_total_liquidity' : IDL.Func([], [IDL.Nat], ['query']),
    'release_initial_funding' : IDL.Func(
        [IDL.Principal, ValidatedEventData],
        [Result],
        [],
      ),
  });
  return InsuranceVault;
};
export const init = ({ IDL }) => {
  return [IDL.Principal, IDL.Principal, IDL.Principal];
};
