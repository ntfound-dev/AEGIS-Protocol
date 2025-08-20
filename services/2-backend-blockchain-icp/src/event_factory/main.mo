// src/event_factory/main.mo
import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Error "mo:base/Error";
import Debug "mo:base/Debug";
import EventDAO "canister:event_dao";
import InsuranceVault "canister:insurance_vault";
import Types "types";

persistent actor class EventFactory() = this { 
  public type ValidatedEventData = Types.ValidatedEventData;
  public type DeclareEventResult = Result.Result<Principal, Text>;

  public shared(_msg) func declare_event(eventData: ValidatedEventData) : async DeclareEventResult {
    Debug.print("declare_event invoked on EventFactory");

    let factory_principal : Principal = Principal.fromActor(this);
    Debug.print("factory principal = " # Principal.toText(factory_principal));

    let init_args : Types.InitArgs = {
      event_data = eventData;
      factory_principal = factory_principal;
    };

    try {
      // panggil EventDAO initialize
      let _init_status : Text = await EventDAO.initialize(init_args);
      let eventdao_principal : Principal = Principal.fromActor(EventDAO);
      Debug.print("eventdao principal = " # Principal.toText(eventdao_principal));

      // PANGGIL insurance_vault secara langsung via import statis
      //
      // IMPORTANT: cek signature release_initial_funding di insurance_vault.
      // Jika ia menerima (Principal, ValidatedEventData), panggil seperti berikut:
      let vault_res = await InsuranceVault.release_initial_funding(eventdao_principal, eventData);

      // Jika insurance_vault mengembalikan Result, kamu bisa debug hasilnya:
      Debug.print("insurance_vault returned: " # debug_show(vault_res));

      return #ok(eventdao_principal);
    } catch (e) {
      Debug.print("declare_event failed: " # Error.message(e));
      return #err(Error.message(e));
    };
  };
};
