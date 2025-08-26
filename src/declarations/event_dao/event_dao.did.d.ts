import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export interface InitArgs {
  'factory_principal' : Principal,
  'event_data' : ValidatedEventData,
}
export type ProposalId = bigint;
export interface ProposalInfo {
  'id' : bigint,
  'title' : string,
  'is_executed' : boolean,
  'amount_requested' : bigint,
  'description' : string,
  'recipient_wallet' : Principal,
  'proposer' : Principal,
  'votes_for' : bigint,
  'votes_against' : bigint,
}
export interface ValidatedEventData {
  'details_json' : string,
  'severity' : string,
  'event_type' : string,
}
export interface _SERVICE {
  'donate' : ActorMethod<[bigint], string>,
  'donateAndVote' : ActorMethod<[bigint, ProposalId, boolean], string>,
  'get_all_proposals' : ActorMethod<[], Array<ProposalInfo>>,
  'get_event_details' : ActorMethod<[], [] | [ValidatedEventData]>,
  'initialize' : ActorMethod<[InitArgs], string>,
  'submit_proposal' : ActorMethod<[string, string, bigint, Principal], string>,
}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
