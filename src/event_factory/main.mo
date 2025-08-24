// src/event_factory/main.mo
import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Error "mo:base/Error";

import EventDAO "canister:event_dao";
import InsuranceVault "canister:insurance_vault"; // import statis, lebih aman
import Types "types";

persistent actor class EventFactory() = this { // hapus vault_id constructor karena import statis
  public type ValidatedEventData = Types.ValidatedEventData;
  public type DeclareEventResult = Result.Result<Principal, Text>;

  public shared(_msg) func declare_event(eventData: ValidatedEventData) : async DeclareEventResult {
    // OPTIMIZATION: Removed excessive debug prints for production

    let factory_principal : Principal = Principal.fromActor(this);

    let init_args : Types.InitArgs = {
      event_data = eventData;
      factory_principal = factory_principal;
    };

    try {
      // panggil EventDAO initialize
      let _init_status : Text = await EventDAO.initialize(init_args);
      let eventdao_principal : Principal = Principal.fromActor(EventDAO);

      // PANGGIL insurance_vault secara langsung via import statis
      let _vault_res = await InsuranceVault.release_initial_funding(eventdao_principal, eventData);

      return #ok(eventdao_principal);
    } catch (e) {
      return #err(Error.message(e));
    };
  };
};
