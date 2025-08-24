// ======================================================
// AEGIS PROTOCOL - main.js (REVISED)
// ======================================================

import { Actor, HttpAgent } from "@dfinity/agent";
import { AuthClient } from "@dfinity/auth-client";
import { Principal } from "@dfinity/principal";

// ===== CHANGES HERE =====
import { idlFactory as did_sbt_ledger_idl, canisterId as did_sbt_ledger_id } from "@declarations/did_sbt_ledger";
import { idlFactory as event_dao_idl } from "@declarations/event_dao";
import { idlFactory as event_factory_idl, canisterId as event_factory_id } from "@declarations/event_factory";


const host = "http://127.0.0.1:4943";

//  retrieving disaster list from Oracle
const ORACLE_API_URL = 'http://localhost:8001/disasters';

//  sending proposal creation request to Validator
const VALIDATOR_API_URL = 'http://localhost:8002/create_proposal';

document.addEventListener('DOMContentLoaded', async () => {
    // 1. DEFINING ALL UI ELEMENTS
    const loginBtn = document.getElementById('loginBtn');
    const loginStatusEl = document.getElementById('loginStatus');
    const getProposalsBtn = document.getElementById('getProposalsBtn');
    const donateVoteBtn = document.getElementById('donateVoteBtn');
    const chatWindow = document.getElementById('chatWindow');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const profileNameInput = document.getElementById('profileName');
    const registerDidBtn = document.getElementById('registerDidBtn');
    const getSbtsBtn = document.getElementById('getSbtsBtn');

    //  APPLICATION STATE 
    let authClient;
    let agent;
    let didLedgerActor;
    let activeDaoPrincipal = null; 
    let activeDaoActor = null;     

    const agentChatUrl = 'http://localhost:8002/chat';
    const agentSignalUrl = 'http://localhost:8002/verify_disaster';

    // === 3. HELPER DISPLAY FUNCTIONS ===
    function displayMessage(content, sender, isJson = false) {
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('message', sender === 'user' ? 'user-message' : 'agent-message');
        let element;
        if (isJson && typeof content !== 'string') {
            element = document.createElement('pre');
            element.textContent = JSON.stringify(content, (key, value) =>
                typeof value === 'bigint' ? value.toString() : value, 2);
        } else {
            element = document.createElement('p');
            element.textContent = content;
        }
        messageContainer.appendChild(element);
        chatWindow.appendChild(messageContainer);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    //  MAIN INTERACTION LOGIC 

    //  Chat Logic 
    async function handleChatMessage() {
        const messageText = chatInput.value.trim();
        if (!messageText) return;

        displayMessage(messageText, 'user');
        chatInput.value = '';
        chatSendBtn.disabled = true;
        displayMessage('Aegis is processing...', 'agent');

        try {
            if (messageText.toLowerCase().startsWith('send signal')) {
                await handleSendSignalCommand(messageText);
            } else {
                await handleNormalChat(messageText);
            }
        } catch (error) {
            chatWindow.removeChild(chatWindow.lastChild);
            displayMessage(`Error: An error occurred. ${error.message}`, 'agent');
        } finally {
            chatSendBtn.disabled = false;
            chatInput.focus();
        }
    }
    
    async function handleNormalChat(messageText) {
        const response = await fetch(agentChatUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText })
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const agentResponse = await response.json();
        chatWindow.removeChild(chatWindow.lastChild);
        displayMessage(agentResponse.reply, 'agent');
    }

    async function handleSendSignalCommand(messageText) {
        let eventData;
        try {
            const parts = messageText.split(" ");
            const location_index = parts.indexOf("earthquake") + 1;
            const magnitude_index = parts.indexOf("magnitude") + 1;
            const location = parts[location_index];
            const magnitude = parseFloat(parts[magnitude_index]);
            
            if (!location || isNaN(magnitude)) throw new Error();

            eventData = {
                source: "Manual Chat Input",
                magnitude: magnitude,
                location: location.charAt(0).toUpperCase() + location.slice(1),
                lat: 0.0, lon: 0.0,
                timestamp: Math.floor(Date.now() / 1000)
            };
        } catch (e) {
            throw new Error("Format of 'send signal' command not recognized. Example: send signal earthquake [location] magnitude [number]");
        }

        const response = await fetch(agentSignalUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eventData)
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const agentResponse = await response.json();
        chatWindow.removeChild(chatWindow.lastChild);
        displayMessage(`Signal Status: ${agentResponse.message}`, 'agent');
        
        const principalRegex = /([a-z0-9]{5}-){4}[a-z0-9]{3}/;
        const match = agentResponse.message.match(principalRegex);
        if (match) {
            const newDaoPrincipalStr = match[0];
            activeDaoPrincipal = Principal.fromText(newDaoPrincipalStr);
            activeDaoActor = null; 
            displayMessage(`Active DAO has been set to: ${newDaoPrincipalStr}. DAO Action buttons now work for this DAO.`, 'agent');
            updateUIState();
        }
    }

    //  Authentication Logic & Update UI State 
    authClient = await AuthClient.create();
    updateUIState();

    async function handleLogin() {
        displayMessage("Processing login request...", "agent");
        if (await authClient.isAuthenticated()) {
            await authClient.logout();
            displayMessage("You have been logged out.", "agent");
        } else {
            await authClient.login({
                identityProvider: "https://identity.ic0.app",
                onSuccess: () => {
                    chatWindow.removeChild(chatWindow.lastChild);
                    displayMessage("Login successful!", "agent");
                    updateUIState();
                },
            });
        }
        updateUIState();
    }

    function updateUIState() {
        const isAuthenticated = authClient.isAuthenticated();
        const identity = authClient.getIdentity();
        agent = new HttpAgent({ host, identity });
        
        didLedgerActor = Actor.createActor(did_sbt_ledger_idl, { agent, canisterId: did_sbt_ledger_id });

        donateVoteBtn.disabled = !isAuthenticated || !activeDaoPrincipal;
        registerDidBtn.disabled = !isAuthenticated;
        getSbtsBtn.disabled = !isAuthenticated;
        getProposalsBtn.disabled = !activeDaoPrincipal;

        if (isAuthenticated) {
            const principal = identity.getPrincipal().toText();
            loginStatusEl.innerHTML = `Logged in as: <b>${principal.substring(0, 5)}...</b>`;
            loginBtn.innerText = "Logout";
        } else {
            loginStatusEl.innerHTML = "<b>Not logged in</b>";
            loginBtn.innerText = "Login with Internet Identity";
        }
    }
    
    //  DID Profile & SBT Logic 
    async function handleRegisterDid() {
        const name = profileNameInput.value.trim();
        if (!name) { alert("Profile name cannot be empty."); return; }
        displayMessage(`Registering profile "${name}"...`, "agent");
        try {
            const response = await didLedgerActor.register_did(name, "Individual", "via-frontend");
            displayMessage(`Success: ${response}`, "agent");
            profileNameInput.value = '';
        } catch(e) {
            displayMessage(`Error registering profile: ${e.message}`, "agent");
        }
    }

    async function handleGetSbts() {
        displayMessage("Searching for your SBTs...", "agent");
        try {
            const principal = authClient.getIdentity().getPrincipal();
            const sbts = await didLedgerActor.get_sbts(principal);
            if (sbts.length === 0) {
                displayMessage("You don't have any SBTs yet.", "agent");
            } else {
                displayMessage("Your SBTs found:", "agent");
                displayMessage(sbts, "agent", true);
            }
        } catch(e) {
            displayMessage(`Error retrieving SBTs: ${e.message}`, "agent");
        }
    }

    //  Dynamic DAO Interaction Logic 
    function getActiveEventDaoActor() {
        if (!activeDaoPrincipal) {
            displayMessage("No active DAO. Create a new event through chat first.", "agent");
            return null;
        }
        // Create new actor every time called to ensure identity (if login/logout) is up to date
        const identity = authClient.getIdentity();
        const dynAgent = new HttpAgent({ host, identity });
        return Actor.createActor(event_dao_idl, { agent: dynAgent, canisterId: activeDaoPrincipal });
    }

    async function handleGetProposals() {
        const daoActor = getActiveEventDaoActor();
        if (!daoActor) return;
        displayMessage(`Retrieving proposals from DAO ${activeDaoPrincipal.toText().substring(0,13)}...`, "agent");
        try {
            const proposals = await daoActor.get_all_proposals();
            if (proposals.length === 0) {
                displayMessage("No proposals have been created in this DAO yet.", "agent");
            } else {
                displayMessage(proposals, "agent", true);
            }
        } catch (error) {
            displayMessage(`Error retrieving proposals: ${error.message}`, "agent");
        }
    }

    async function handleDonateAndVote() {
    if (!authClient.isAuthenticated()) { 
        alert("You must be logged in!"); 
        return; 
    }
    const daoActor = getActiveEventDaoActor();
    if (!daoActor) return;
    
    displayMessage(`Sending donation to DAO ${activeDaoPrincipal.toText().substring(0,13)}...`, "agent");
    
    try {
        
        const amount = 100_000_000n; 
        const proposalId = 0n;
        const inFavor = true;
        const response = await daoActor.donateAndVote(amount, proposalId, inFavor);
        displayMessage(`Success: ${response}`, "agent");
    } catch (error) {
        displayMessage(`Error during donation/vote: ${error.message}`, "agent");
    }
}

    //  CONNECTING ALL FUNCTIONS TO BUTTONS 
    loginBtn.addEventListener("click", handleLogin);
    chatSendBtn.addEventListener("click", handleChatMessage);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleChatMessage(); });
    registerDidBtn.addEventListener("click", handleRegisterDid);
    getSbtsBtn.addEventListener("click", handleGetSbts);
    getProposalsBtn.addEventListener("click", handleGetProposals);
    donateVoteBtn.addEventListener("click", handleDonateAndVote);
});
