sequenceDiagram
    participant Oracle as <i class='fas fa-satellite-dish'></i> Oracle Agent
    participant Validator as <i class='fas fa-brain'></i> Validator Agent
    participant Action as <i class='fas fa-key'></i> Action Agent
    participant Factory as <i class='fa fa-industry'></i> Event Factory (IC)
    participant Vault as <i class='fa fa-university'></i> Insurance Vault (IC)
    participant DAO as <i class='fa fa-users'></i> Event DAO (IC)

    %% Phase 1: Off-Chain
    note over Oracle, Validator: Phase 1: Off-Chain Detection & Validation
    Oracle->>Oracle: Fetch data from USGS/BMKG API
    Oracle->>Validator: Send RawEarthquakeData
    Validator->>Validator: Apply validation logic (perform_ai_validation)
    Validator->>Action: Send ValidatedEvent (if significant)

    %% Phase 2: On-Chain
    note over Action, DAO: Phase 2: On-Chain Execution & Creation
    Action->>Factory: call update_raw("declare_event", event_data)
    Factory->>DAO: Create new EventDAO instance
    Factory->>Vault: call release_initial_funding(dao_principal_id)
    Vault-->>Factory: Confirm funds sent
    Factory-->>Action: Return new DAO Principal ID

    %% Phase 3: Confirmation
    note over Action: Phase 3: Confirmation
    Action->>Action: Log success result & new DAO Principal ID
