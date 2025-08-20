import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export type DeclareEventResult = { 'ok' : Principal } |
  { 'err' : string };
export interface EventFactory {
  'declare_event' : ActorMethod<[ValidatedEventData], DeclareEventResult>,
}
export interface ValidatedEventData {
  'details_json' : string,
  'severity' : string,
  'event_type' : string,
}
export interface _SERVICE extends EventFactory {}
export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
