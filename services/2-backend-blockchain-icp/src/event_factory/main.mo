// File: services/2-backend-blockchain-icp/src/event_factory/main.mo

// Mengimpor library standar yang dibutuhkan dari Motoko
import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Error "mo:base/Error";
import Nat "mo:base/Nat";
import Blob "mo:base/Blob";

// Impor canister EventDAO agar kita tahu "cetakan" DAO yang akan kita buat
// DFX akan secara otomatis menautkan ini saat build
import EventDAO "mo:../event_dao/main";

actor EventFactory {

    // Mendefinisikan tipe data untuk informasi bencana yang divalidasi.
    // Ini adalah struktur data yang akan dikirim oleh Action Agent dari Fetch.ai.
    public type ValidatedEventData = {
        event_type: Text;
        severity: Text;
        details_json: Text; // Detail dalam format JSON yang diubah menjadi teks
    };

    // Mendefinisikan tipe data untuk hasil dari pemanggilan fungsi `declare_event`.
    // Hasilnya bisa berupa #ok dengan ID Canister baru, atau #err dengan pesan kesalahan.
    public type DeclareEventResult = Result.Result<Principal, Text>;

    // --- FUNGSI UTAMA ---
    // Fungsi ini bersifat 'shared', artinya bisa dipanggil dari luar (oleh Action Agent).
    // Ia menerima data bencana yang sudah divalidasi.
    public shared(msg) func declare_event(eventData: ValidatedEventData) : async DeclareEventResult {

        // Di versi produksi, Anda harus menambahkan pengecekan keamanan di sini
        // untuk memastikan bahwa `msg.caller` (pemanggil fungsi ini)
        // adalah Principal (ID) dari Action Agent yang sah.

        try {
            // Kita butuh Wasm (kode yang sudah dikompilasi) dari EventDAO untuk menginstalnya.
            // DFX akan menangani ini secara otomatis saat kita men-deploy.
            let dao_wasm : Blob = EventDAO.idl_to_wasm((EventDAO,));

            // Argumen yang akan diteruskan saat EventDAO baru pertama kali dibuat (inisialisasi).
            let init_args : EventDAO.InitArgs = {
                event_data = eventData;
                // `Principal.fromActor(self)` adalah ID dari canister EventFactory ini sendiri.
                factory_principal = Principal.fromActor(self);
            };

            // Membuat canister baru di jaringan Internet Computer.
            // Kita memberinya 1 Triliun cycles sebagai "bahan bakar" awal.
            let new_canister_principal = await create_canister(1_000_000_000_000);

            // Setelah canister kosong dibuat, kita menginstal kode EventDAO ke dalamnya.
            await install_code(new_canister_principal, dao_wasm, init_args);

            // Jika semua berhasil, kembalikan ID dari canister DAO yang baru dibuat.
            return #ok(new_canister_principal);

        } catch (e) {
            // Jika terjadi error, kembalikan pesan kesalahan.
            return #err(Error.message(e));
        }
    };

    // --- FUNGSI HELPER (PEMBANTU) ---
    // Fungsi-fungsi ini adalah versi yang disederhanakan. DFX akan menyediakan implementasi
    // yang sebenarnya saat proses build dengan menghubungkannya ke IC Management Canister.

    private func create_canister(cycles: Nat) : async Principal {
        // Ini adalah placeholder.
        return Principal.fromText("aaaaa-aa"); // Dummy Principal
    };

    private func install_code(id: Principal, wasm: Blob, init_args: EventDAO.InitArgs) : async () {
        // Ini adalah placeholder.
    };
}