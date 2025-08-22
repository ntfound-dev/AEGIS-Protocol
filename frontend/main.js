// ======================================================
// AEGIS PROTOCOL - main.js 
// ======================================================

import { Actor, HttpAgent } from "@dfinity/agent";
import { AuthClient } from "@dfinity/auth-client";
import { Principal } from "@dfinity/principal";

import { idlFactory as did_sbt_ledger_idl, canisterId as did_sbt_ledger_id } from "dfx:canisters/did_sbt_ledger";
import { idlFactory as event_dao_idl } from "dfx:canisters/event_dao";
import { idlFactory as event_factory_idl, canisterId as event_factory_id } from "dfx:canisters/event_factory";

const host = "http://127.0.0.1:4943";

document.addEventListener('DOMContentLoaded', async () => {
    // === 1. MENDEFINISIKAN SEMUA ELEMEN UI ===
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

    // === 2. STATE APLIKASI ===
    let authClient;
    let agent;
    let didLedgerActor;
    let activeDaoPrincipal = null; // Akan diisi dengan Principal ID dari DAO yang aktif
    let activeDaoActor = null;     // Aktor untuk DAO yang aktif, dibuat secara dinamis

    const agentChatUrl = 'http://localhost:8002/chat';
    const agentSignalUrl = 'http://localhost:8002/verify_disaster';

    // === 3. FUNGSI HELPER TAMPILAN ===
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

    // === 4. LOGIKA UTAMA INTERAKSI ===

    // -- Logika Chat (Otak dari Interaksi) --
    async function handleChatMessage() {
        const messageText = chatInput.value.trim();
        if (!messageText) return;

        displayMessage(messageText, 'user');
        chatInput.value = '';
        chatSendBtn.disabled = true;
        displayMessage('Aegis sedang memproses...', 'agent');

        try {
            if (messageText.toLowerCase().startsWith('kirim sinyal')) {
                await handleSendSignalCommand(messageText);
            } else {
                await handleNormalChat(messageText);
            }
        } catch (error) {
            chatWindow.removeChild(chatWindow.lastChild);
            displayMessage(`Error: Terjadi kesalahan. ${error.message}`, 'agent');
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
            const location_index = parts.indexOf("gempa") + 1;
            const magnitude_index = parts.indexOf("magnitudo") + 1;
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
            throw new Error("Format perintah 'kirim sinyal' tidak dikenali. Contoh: kirim sinyal gempa [lokasi] magnitudo [angka]");
        }

        const response = await fetch(agentSignalUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eventData)
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const agentResponse = await response.json();
        chatWindow.removeChild(chatWindow.lastChild);
        displayMessage(`Status Sinyal: ${agentResponse.message}`, 'agent');
        
        const principalRegex = /([a-z0-9]{5}-){4}[a-z0-9]{3}/;
        const match = agentResponse.message.match(principalRegex);
        if (match) {
            const newDaoPrincipalStr = match[0];
            activeDaoPrincipal = Principal.fromText(newDaoPrincipalStr);
            activeDaoActor = null; 
            displayMessage(`DAO Aktif telah diatur ke: ${newDaoPrincipalStr}. Tombol Aksi DAO sekarang berfungsi untuk DAO ini.`, 'agent');
            updateUIState();
        }
    }

    // -- Logika Otentikasi & Update UI State --
    authClient = await AuthClient.create();
    updateUIState();

    async function handleLogin() {
        displayMessage("Memproses permintaan login...", "agent");
        if (await authClient.isAuthenticated()) {
            await authClient.logout();
            displayMessage("Anda telah logout.", "agent");
        } else {
            await authClient.login({
                identityProvider: "https://identity.ic0.app",
                onSuccess: () => {
                    chatWindow.removeChild(chatWindow.lastChild);
                    displayMessage("Login berhasil!", "agent");
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
            loginStatusEl.innerHTML = `Login sebagai: <b>${principal.substring(0, 5)}...</b>`;
            loginBtn.innerText = "Logout";
        } else {
            loginStatusEl.innerHTML = "<b>Not logged in</b>";
            loginBtn.innerText = "Login dengan Internet Identity";
        }
    }
    
    // -- Logika Profil DID & SBT --
    async function handleRegisterDid() {
        const name = profileNameInput.value.trim();
        if (!name) { alert("Nama profil tidak boleh kosong."); return; }
        displayMessage(`Mendaftarkan profil "${name}"...`, "agent");
        try {
            const response = await didLedgerActor.register_did(name, "Individu", "via-frontend");
            displayMessage(`Sukses: ${response}`, "agent");
            profileNameInput.value = '';
        } catch(e) {
            displayMessage(`Error mendaftarkan profil: ${e.message}`, "agent");
        }
    }

    async function handleGetSbts() {
        displayMessage("Mencari SBT milik Anda...", "agent");
        try {
            const principal = authClient.getIdentity().getPrincipal();
            const sbts = await didLedgerActor.get_sbts(principal);
            if (sbts.length === 0) {
                displayMessage("Anda belum memiliki SBT.", "agent");
            } else {
                displayMessage("SBT Anda ditemukan:", "agent");
                displayMessage(sbts, "agent", true);
            }
        } catch(e) {
            displayMessage(`Error mengambil SBT: ${e.message}`, "agent");
        }
    }

    // -- Logika Interaksi DAO Dinamis --
    function getActiveEventDaoActor() {
        if (!activeDaoPrincipal) {
            displayMessage("Tidak ada DAO yang aktif. Buat event baru melalui chat terlebih dahulu.", "agent");
            return null;
        }
        // Buat aktor baru setiap kali dipanggil untuk memastikan identitas (jika login/logout) sudah yang terbaru
        const identity = authClient.getIdentity();
        const dynAgent = new HttpAgent({ host, identity });
        return Actor.createActor(event_dao_idl, { agent: dynAgent, canisterId: activeDaoPrincipal });
    }

    async function handleGetProposals() {
        const daoActor = getActiveEventDaoActor();
        if (!daoActor) return;
        displayMessage(`Mengambil proposal dari DAO ${activeDaoPrincipal.toText().substring(0,13)}...`, "agent");
        try {
            const proposals = await daoActor.get_all_proposals();
            if (proposals.length === 0) {
                displayMessage("Belum ada proposal yang dibuat di DAO ini.", "agent");
            } else {
                displayMessage(proposals, "agent", true);
            }
        } catch (error) {
            displayMessage(`Error mengambil proposal: ${error.message}`, "agent");
        }
    }

    async function handleDonateAndVote() {
        if (!authClient.isAuthenticated()) { alert("Anda harus login!"); return; }
        const daoActor = getActiveEventDaoActor();
        if (!daoActor) return;
        displayMessage(`Mengirim donasi ke DAO ${activeDaoPrincipal.toText().substring(0,13)}...`, "agent");
        try {
            const amount = 100_000_000n; // 1 ICP in e8s (8 desimal)
            const proposalId = 0n;
            const inFavor = true;
            const response = await daoActor.donateAndVote(amount, proposalId, inFavor);
            displayMessage(`Sukses: ${response}`, "agent");
        } catch (error) {
            displayMessage(`Error saat donasi/vote: ${error.message}`, "agent");
        }
    }

    // === 5. MENGHUBUNGKAN SEMUA FUNGSI KE TOMBOL ===
    loginBtn.addEventListener("click", handleLogin);
    chatSendBtn.addEventListener("click", handleChatMessage);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleChatMessage(); });
    registerDidBtn.addEventListener("click", handleRegisterDid);
    getSbtsBtn.addEventListener("click", handleGetSbts);
    getProposalsBtn.addEventListener("click", handleGetProposals);
    donateVoteBtn.addEventListener("click", handleDonateAndVote);
});