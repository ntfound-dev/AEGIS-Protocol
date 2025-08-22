import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export interface InsuranceVault {
  'add_funder' : ActorMethod<[Principal], Result>,
  'fund_vault' : ActorMethod<[bigint], Result>,
  'get_authorized_funders' : ActorMethod<[], Array<Principal>>,
  'get_total_liquidity' : ActorMethod<[], bigint>,
  'release_initial_funding' : ActorMethod<
    [Principal, ValidatedEventData],
    Result
  >,
}
export type Result = { 'ok' : string } |
  { 'err' : string };
export interface ValidatedEventData {
  'details_json' : string,
  'severity' : string,
  'event_type' : string,
}
export interface _SERVICE extends InsuranceVault {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
