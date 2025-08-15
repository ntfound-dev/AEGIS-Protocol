// File: services/2-backend-blockchain-icp/src/event_factory/main.mo

import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Nat "mo:base/Nat";
// --- PERBAIKAN: Import ExperimentalCycles untuk manajemen cycles ---
import Cycles "mo:base/ExperimentalCycles";
// --- PERBAIKAN: Import actor class EventDAO secara langsung ---
import EventDAO "canister:event_dao";

// --- PERBAIKAN: Ubah menjadi actor class agar bisa diinstansiasi dengan ID vault ---
actor class EventFactory (vault_id: Principal) {

    public type ValidatedEventData = EventDAO.ValidatedEventData;
    public type DeclareEventResult = Result.Result<Principal, Text>;

    // Menyimpan ID insurance_vault yang berwenang
    let insurance_vault : actor {
        release_initial_funding: (Principal, ValidatedEventData) -> async Result.Result<Text, Text>;
    } = actor(vault_id);

    public shared(msg) func declare_event(eventData: ValidatedEventData) : async DeclareEventResult {
        // --- PERBAIKAN: Logika pembuatan canister yang jauh lebih sederhana ---
        
        // 1. Tentukan argumen inisialisasi untuk EventDAO
        let init_args : EventDAO.InitArgs = {
            event_data = eventData;
            factory_principal = Principal.fromActor(self);
        };

        // 2. Tentukan jumlah cycles yang dibutuhkan untuk membuat canister + cadangan
        // (Jumlah ini perlu disesuaikan)
        let cycles_for_new_canister : Nat = 2_000_000_000_000; // Contoh: 2 Triliun cycles
        
        try {
            // 3. Tambahkan cycles ke panggilan pembuatan canister
            Cycles.add(cycles_for_new_canister);

            // 4. Buat instance baru dari EventDAO actor class
            // Cycles yang ditambahkan di atas akan digunakan untuk pembuatan ini
            let new_dao_canister = await EventDAO.EventDAO(init_args);
            let new_canister_principal = Principal.fromActor(new_dao_canister);

            // 5. (Opsional) Panggil insurance_vault untuk melepaskan dana awal
            let release_result = await insurance_vault.release_initial_funding(new_canister_principal, eventData);
            // Anda bisa menangani 'release_result' di sini jika perlu

            return #ok(new_canister_principal);

        } catch (e) {
            // Jika gagal (misalnya cycles tidak cukup), kembalikan error
            return #err(Error.message(e));
        }
    };
}