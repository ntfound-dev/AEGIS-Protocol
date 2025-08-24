Core Concepts and Terminology of Aegis Protocol
This document serves as a dictionary for understanding key terms and fundamental components that form the Aegis Protocol ecosystem.

Off-Chain Concepts (AI Agents World)
These components run outside the blockchain (on servers/Docker) and are responsible for observing and interacting with the real world.

Oracle Agent
Analogy: A scout in a watchtower.

Task: Its task is very specific: continuously monitor predetermined external data sources (USGS earthquake API, BMKG, etc.). When it sees "something" (new data), it doesn't analyze it, it just shouts out what it sees ("New report from USGS!") to the Validator Agent. It is the eyes and ears of the system.

Validator Agent
Analogy: An intelligence analyst in the command room.

Task: It receives raw reports from scouts (Oracle Agent) and also from human operators (chat input in frontend). Its task is to:

Filter Noise: Ensure the report has the correct format.

Analyze Significance: Apply logic (currently based on magnitude) to decide whether this report is important enough to act upon.

Compose Official Report: Transform messy raw data into a clean and structured standard report (ValidatedEvent).

Give Commands: If a report is deemed valid and significant, it will command the Action Agent to act.

Action Agent (The Bridge)
Analogy: An official messenger with a royal seal.

Task: It is the only off-chain entity trusted to speak directly with the on-chain world (blockchain). It has no intelligence to analyze, it only executes commands. When the Validator Agent gives it an official report (ValidatedEvent), it will go to the Event Factory on the blockchain, show its "seal" (identity.pem), and say, "By command of the command room, declare this emergency event!"

On-Chain Concepts (Blockchain/Canisters World)
These components live on the Internet Computer. They are the transparent and immutable foundation of the system.

Internet Identity
Analogy: Universal digital passport.

Task: This is the decentralized authentication system from Internet Computer. Users don't create username/password in our application. Instead, they login using their Internet Identity, which gives them a unique and secure Principal ID (like a passport number) across the entire IC ecosystem.

Event Factory
Analogy: An automated assembly factory.

Task: This canister has only one job: receive valid commands from the Action Agent. When a command is received, the "assembly line" in this factory will automatically create and deploy a new, fully configured Event DAO.

Insurance Vault
Analogy: An insured bank vault.

Task: This is a canister where funders store initial liquidity funds. When the Event Factory creates a new DAO, it has authorization to withdraw a certain amount of initial funds from this vault (based on disaster severity) to "inject capital" into the newly created DAO's treasury.

Event DAO
Analogy: An emergency meeting room and transparent bank account for one specific disaster.

Task: This is the on-chain command center for one event. Inside it, verified stakeholders can:

Submit Proposals: "We need funds of X amount to buy Y."

Vote: Approve or reject proposals.

Donate: Add funds to the treasury (treasury_balance).
All these activities are recorded publicly and permanently.

DID/SBT Ledger
Analogy: Civil registry office and achievement album on blockchain.

Task:

DIDProfile (Birth Certificate): Records a user's or organization's identity registration, linking their Principal ID with a name.

SBT (Badge/Achievement Certificate): When a user performs important actions (such as donating in an Event DAO), this canister will mint a non-transferable digital "badge" for them. This builds a verified reputation track record.