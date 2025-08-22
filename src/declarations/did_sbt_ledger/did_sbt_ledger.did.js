export const idlFactory = ({ IDL }) => {
  const Result = IDL.Variant({ 'ok' : IDL.Text, 'err' : IDL.Text });
  const Time = IDL.Int;
  const DIDProfile = IDL.Record({
    'registration_date' : Time,
    'owner' : IDL.Principal,
    'name' : IDL.Text,
    'contact_info' : IDL.Text,
    'entity_type' : IDL.Text,
  });
  const SBT = IDL.Record({
    'issued_at' : Time,
    'badge_id' : IDL.Nat,
    'issuer' : IDL.Principal,
    'event_name' : IDL.Text,
    'badge_type' : IDL.Text,
  });
  const DID_SBT_Ledger = IDL.Service({
    'authorize_minter' : IDL.Func([IDL.Principal], [Result], []),
    'get_did' : IDL.Func([IDL.Principal], [IDL.Opt(DIDProfile)], ['query']),
    'get_sbts' : IDL.Func([IDL.Principal], [IDL.Vec(SBT)], ['query']),
    'mint_sbt' : IDL.Func([IDL.Principal, IDL.Text, IDL.Text], [Result], []),
    'register_did' : IDL.Func([IDL.Text, IDL.Text, IDL.Text], [IDL.Text], []),
  });
  return DID_SBT_Ledger;
};
export const init = ({ IDL }) => { return [IDL.Principal]; };
