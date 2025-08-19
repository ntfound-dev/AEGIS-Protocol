// src/event_factory/main.mo -- corrected
import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Nat "mo:base/Nat";
import Error "mo:base/Error";
import Cycles "mo:base/ExperimentalCycles";
import EventDAO "canister:event_dao";
import Types "types";

persistent actor class EventFactory (vault_id: Principal) = this {

  public type ValidatedEventData = Types.ValidatedEventData;
  public type DeclareEventResult = Result.Result<Principal, Text>;

  // insurance_vault expects an actor id as Text; convert Principal -> Text here.
  transient let insurance_vault : actor {
    release_initial_funding: (Principal, ValidatedEventData) -> async Result.Result<Text, Text>;
  } = actor(Principal.toText(vault_id));

  public shared(msg) func declare_event(eventData: ValidatedEventData) : async DeclareEventResult {
    // get the principal of this factory canister
    let factory_principal : Principal = Principal.fromActor(this);

    // Build init args using a Principal for factory_principal (not Text).
    let init_args : Types.InitArgs = {
      event_data = eventData;
      factory_principal = factory_principal;
    };

    // Example cycles amount (adjust or remove if your environment handles cycles differently)
    let cycles_for_new_canister : Nat = 2_000_000_000_000;

    try {
      // If you need to add cycles to the calling canister before calling other canisters,
      // use the Cycles API properly for your Motoko version. If this line fails, comment it out.
      // Cycles.add(cycles_for_new_canister);

      // Initialize the DAO. NOTE: this calls the singleton EventDAO canister declared in dfx.json.
      let init_status : Text = await EventDAO.initialize(init_args);

      // Get the Principal for the EventDAO canister
      let eventdao_principal : Principal = Principal.fromActor(EventDAO);

      // Ask the insurance vault (actor reference created above) to release funding
      let _ = await insurance_vault.release_initial_funding(eventdao_principal, eventData);

      return #ok(eventdao_principal);
    } catch (e) {
      return #err(Error.message(e));
    };
  };
};
