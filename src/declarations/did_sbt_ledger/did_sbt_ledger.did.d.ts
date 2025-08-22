import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export interface DIDProfile {
  'registration_date' : Time,
  'owner' : Principal,
  'name' : string,
  'contact_info' : string,
  'entity_type' : string,
}
export interface DID_SBT_Ledger {
  'authorize_minter' : ActorMethod<[Principal], Result>,
  'get_did' : ActorMethod<[Principal], [] | [DIDProfile]>,
  'get_sbts' : ActorMethod<[Principal], Array<SBT>>,
  'mint_sbt' : ActorMethod<[Principal, string, string], Result>,
  'register_did' : ActorMethod<[string, string, string], string>,
}
export type Result = { 'ok' : string } |
  { 'err' : string };
export interface SBT {
  'issued_at' : Time,
  'badge_id' : bigint,
  'issuer' : Principal,
  'event_name' : string,
  'badge_type' : string,
}
export type Time = bigint;
export interface _SERVICE extends DID_SBT_Ledger {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
