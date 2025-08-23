sequenceDiagram
    participant Oracle as <i class='fas fa-satellite-dish'></i> Oracle Agent
    participant Validator as <i class='fas fa-brain'></i> Validator Agent
    participant Action as <i class='fas fa-key'></i> Action Agent
    participant Factory as <i class='fa fa-industry'></i> Event Factory (IC)
    participant Vault as <i class='fa fa-university'></i> Insurance Vault (IC)
    participant DAO as <i class='fa fa-users'></i> Event DAO (IC)

    %% Fase 1: Off-Chain
    note over Oracle, Validator: Fase 1: Deteksi & Validasi Off-Chain
    Oracle->>Oracle: Ambil data dari API USGS/BMKG
    Oracle->>Validator: Kirim RawEarthquakeData
    Validator->>Validator: Terapkan logika validasi (perform_ai_validation)
    Validator->>Action: Kirim ValidatedEvent (jika signifikan)

    %% Fase 2: On-Chain
    note over Action, DAO: Fase 2: Eksekusi & Penciptaan On-Chain
    Action->>Factory: panggil update_raw("declare_event", event_data)
    Factory->>DAO: Buat instance EventDAO baru
    Factory->>Vault: panggil release_initial_funding(dao_principal_id)
    Vault-->>Factory: Konfirmasi dana terkirim
    Factory-->>Action: Kembalikan Principal ID DAO baru

    %% Fase 3: Konfirmasi
    note over Action: Fase 3: Konfirmasi
    Action->>Action: Log hasil sukses & Principal ID DAO baru
