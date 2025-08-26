// =====================================================================
// AEGIS Protocol - Frontend User Interface
// =====================================================================
// File: frontend/main.js
// Purpose: Interactive web interface for disaster response simulation
// 
// Architecture Overview:
//   The AEGIS Protocol frontend provides a comprehensive user interface
//   for interacting with the decentralized disaster response system.
//   It simulates multiple user roles and demonstrates the complete
//   disaster response workflow from event detection to fund disbursement.
// 
// Key Features:
//   - Multi-role simulation (Admin, Funder, Organizer, Communities)
//   - Real-time chat interface with AI assistant
//   - Interactive demonstration of all system components
//   - Visual feedback for blockchain operations
//   - Complete disaster response lifecycle simulation
// 
// User Roles:
//   - Admin: System management and proposal approval
//   - Funder: Capital provision and insurance vault management
//   - Organizer: Disaster event declaration and coordination
//   - Community (Affected): Proposal submission and aid requests
//   - Community (Supporting): Donations and voting participation
// 
// Simulation Features:
//   - Realistic disaster response scenarios
//   - Step-by-step workflow demonstration
//   - Interactive command processing (natural language + DFX)
//   - Real-time state updates and progress tracking
//   - Educational feedback for each operation
// 
// Technical Implementation:
//   - Vanilla JavaScript for broad compatibility
//   - Event-driven architecture for responsive UI
//   - Local state management for simulation data
//   - Integration with IC agent libraries for blockchain connectivity
// 
// Integration Points:
//   - IC Canisters: Direct communication with deployed contracts
//   - AI Agents: Monitoring and event processing
//   - Identity System: User authentication and role management
// =====================================================================

// Wait for DOM to be fully loaded before initializing application
// This ensures all HTML elements are available for manipulation
document.addEventListener('DOMContentLoaded', () => {

    // ===================================================================
    // DOM ELEMENT REFERENCES
    // ===================================================================
    // Cache DOM elements for efficient access throughout the application
    
    // Authentication and user interface elements
    const loginBtn = document.getElementById('loginBtn');           // Role selection button
    const loginStatusEl = document.getElementById('loginStatus');   // Current user role display
    
    // Chat interface elements for AI assistant interaction
    const chatWindow = document.getElementById('chatWindow');       // Message display area
    const chatInput = document.getElementById('chatInput');         // User input field
    const chatSendBtn = document.getElementById('chatSendBtn');     // Message send button

    // ===================================================================
    // APPLICATION STATE MANAGEMENT
    // ===================================================================
    // Global state variables for simulation and role-playing
    
    // Current user role for role-based command processing
    let currentRole = null;
    
    // Financial state tracking for funder simulation
    let funderBalance = 0;      // Available capital for insurance vault
    let funderToken = 0;        // AEGIS tokens earned as funder rewards
    
    // Active DAO tracking for disaster event management
    let activeDaoId = null;     // Current disaster DAO identifier
    
    // Proposal system state for governance simulation
    let proposalList = [];      // Array of disaster relief proposals
    
    // User registration and participation tracking
    let isProfileRegistered = false;  // Community member registration status
    let proposalApproved = false;     // Admin approval state for proposals

    // ===================================================================
    // ROLE DEFINITIONS AND PERMISSIONS
    // ===================================================================
    // Define available user roles and their capabilities in the system
    
    const ROLES = {
        ADMIN: 'Admin',                    // System administrator with full access
        FUNDER: 'Funder',                  // Capital provider for insurance vault
        ORGANIZER: 'Organizer',            // Disaster event coordinator
        KOMUNITAS_PEDULI: 'Komunitas Peduli',   // Supporting community (donors/voters)
        KOMUNITAS_KORBAN: 'Komunitas Korban'    // Affected community (aid recipients)
    };
    
    // Role Capabilities:
    // - ADMIN: Deploy canisters, approve proposals, system management
    // - FUNDER: Provide capital, manage insurance vault, earn rewards
    // - ORGANIZER: Declare disaster events, coordinate response efforts
    // - KOMUNITAS_PEDULI: Register identity, donate funds, vote on proposals
    // - KOMUNITAS_KORBAN: Submit aid proposals, request fund disbursement

    // ===================================================================
    // MESSAGE DISPLAY SYSTEM
    // ===================================================================
    // Comprehensive chat interface for user interaction and feedback
    
    /**
     * Display message in chat interface with rich formatting and context
     * 
     * Features:
     *   - Role-based message styling (user vs AI assistant)
     *   - Timestamp tracking for conversation history
     *   - Icon differentiation for message sources
     *   - Automatic scrolling for latest messages
     *   - HTML content support for rich formatting
     * 
     * @param {string} content - Message content (supports HTML)
     * @param {string} sender - Message sender identifier
     * @param {boolean} isImage - Flag for image content (optional)
     */
    function displayMessage(content, sender, isImage = false) {
        // Create message container with appropriate styling
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('message', sender.includes('Anda') ? 'user-message' : 'agent-message');
        
        // Create and configure message icon
        const messageIcon = document.createElement('div');
        messageIcon.classList.add('message-icon');
        
        // Set icon based on sender type
        if (sender === 'Aegis AI Assistant') {
            messageIcon.innerHTML = '<i class="fas fa-robot"></i>';  // AI assistant icon
        } else {
            messageIcon.innerHTML = '<i class="fas fa-user-circle"></i>';  // User icon
        }

        // Create message content container
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        // Create message header with sender and timestamp
        const messageHeader = document.createElement('div');
        messageHeader.classList.add('message-header');
        messageHeader.innerHTML = `
            <span class="sender">${sender}</span>
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
        `;
        messageContent.appendChild(messageHeader);

        // Create and append message body
        let element = document.createElement('p');
        element.innerHTML = content;  // Support HTML formatting in messages
        
        messageContent.appendChild(element);
        messageContainer.appendChild(messageIcon);
        messageContainer.appendChild(messageContent);
        chatWindow.appendChild(messageContainer);
        
        // Auto-scroll to show latest message
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // 4. SIMULASI CHAT ENGINE
    async function handleCommand(command, role) {
        const lowerCommand = command.toLowerCase().trim();
        let response = '';

        // Deteksi perintah DFX
        if (lowerCommand.startsWith('dfx')) {
            response = handleDfxCommand(lowerCommand, role);
        } else {
            // Perintah natural
            response = handleNaturalCommand(lowerCommand, role);
        }

        await new Promise(resolve => setTimeout(resolve, 1000));
        displayMessage(response, 'Aegis AI Assistant');
    }

    // Fungsi untuk memproses perintah natural
    function handleNaturalCommand(lowerCommand, role) {
        let response = '';
        switch (role) {
            case ROLES.ADMIN:
                if (lowerCommand.includes('bersihkan') && lowerCommand.includes('deploy')) {
                    response = `✅ Semua canister berhasil dideploy ulang. Sistem siap digunakan.`;
                } else if (lowerCommand.includes('cek proposal') || lowerCommand.includes('setujui proposal')) {
                    if (proposalList.length === 0) {
                        proposalList.push({ id: 0, title: "Pengadaan 100 Tenda Darurat", votes_for: 1, votes_against: 0, amount: "1 juta" });
                    }
                    proposalApproved = true;
                    const proposal = proposalList[0];
                    let responsePart1 = `📊 Proposal #0 → votes_for = ${proposal.votes_for}, votes_against = ${proposal.votes_against}<br>Status: Disetujui ✅`;
                    let responsePart2 = `✅ Proposal #0 dieksekusi.<br>💰 Dana ${proposal.amount} icp dicairkan dari vault ke Komunitas korban.<br>Status proposal: Selesai`;
                    response = responsePart1 + '<br><br>' + responsePart2;
                } else {
                    response = `Mohon maaf, berikan saya perintah yang benar untuk penanggulangan bencana darurat.`;
                }
                break;
            case ROLES.FUNDER:
                if (lowerCommand.includes('invest dana vault')) {
                    funderBalance = 100000000000000;
                    funderToken = 10000;
                    response = `✅ Vault terisi: 100T icp token<br>🎁 Sebagai funder Anda menerima 10.000 Token AEGIS.<br>Saldo token Funder = 10.000 AEGIS`;
                } else {
                    response = `Mohon maaf, berikan saya perintah yang benar untuk penanggulangan bencana darurat.`;
                }
                break;
            case ROLES.ORGANIZER:
                if (lowerCommand.includes('deklarasikan event bencana')) {
                    activeDaoId = 'lz3um-vp777-77777-aaaba-cai';
                    response = `✅ Event Gempa Haiti 7.2 dibuat.<br>DAO aktif dengan ID: ${activeDaoId}.`;
                } else {
                    response = `Mohon maaf, berikan saya perintah yang benar untuk penanggulangan bencana darurat.`;
                }
                break;
            case ROLES.KOMUNITAS_KORBAN:
                if (lowerCommand.includes('ajukan proposal bantuan')) {
                    if (!activeDaoId) {
                         activeDaoId = 'lz3um-vp777-77777-aaaba-cai';
                    }
                    if (proposalList.length === 0) {
                        proposalList.push({ id: 0, title: "Pengadaan 100 Tenda Darurat", votes_for: 0, votes_against: 0, amount: "1 juta" });
                    }
                    response = `✅ Proposal #0 terdaftar Pengadaan 100 Tenda Darurat dan 1 juta token icp.`;
                } else if (lowerCommand.includes('minta pencairan dana')) {
                    if (proposalList.length === 0) {
                        proposalList.push({ id: 0, title: "Pengadaan 100 Tenda Darurat", votes_for: 0, votes_against: 0, amount: "1 juta" });
                    }
                    
                    if (proposalApproved) {
                        response = `✅ Proposal #0 dieksekusi.<br>💰 Dana ${proposalList[0].amount} icp dicairkan dari vault ke Komunitas korban.<br>Status proposal: Selesai`;
                    } else {
                        response = `✅ Proposal #0<br>💰 menunggu persetujuan admin untuk pencairan`;
                    }
                } else {
                    response = `Mohon maaf, berikan saya perintah yang benar untuk penanggulangan bencana darurat.`;
                }
                break;
            case ROLES.KOMUNITAS_PEDULI:
                if (lowerCommand.includes('daftar indentitas') || lowerCommand.includes('daftar profil')) {
                    isProfileRegistered = true;
                    response = `✅ Profil Komunitas Peduli berhasil terdaftar.`;
                } else if (lowerCommand.includes('kirim donasi') || lowerCommand.includes('donateandvote')) {
                    if (!activeDaoId) {
                        activeDaoId = 'lz3um-vp777-77777-aaaba-cai';
                    }
                    if (proposalList.length === 0) {
                        proposalList.push({ id: 0, title: "Pengadaan 100 Tenda Darurat", votes_for: 0, votes_against: 0, amount: "50 miliar" });
                    }
                    
                    if (isProfileRegistered && proposalList.length > 0) {
                        proposalList[0].votes_for += 1;
                        response = `✅ Donasi terkirim 1 miliar<br>✅ Vote terekam<br>🎖️ SBT Donatur & Partisipasi untuk anda dan anda mendapatkan 1000 token aegis`;
                    } else {
                         response = `Gagal: Pastikan Anda sudah mendaftar profil dan ada proposal aktif.`;
                    }
                } else {
                    response = `Mohon maaf, berikan saya perintah yang benar untuk penanggulangan bencana darurat.`;
                }
                break;
            default:
                response = `Silakan pilih peran Anda terlebih dahulu.`;
        }
        return response;
    }
    
    // Fungsi untuk memproses perintah DFX
    function handleDfxCommand(lowerCommand, role) {
        let response = '';
        if (lowerCommand.includes('dfx stop') || lowerCommand.includes('dfx deploy')) {
            if (role === ROLES.ADMIN) {
                response = `✅ Semua canister berhasil dideploy ulang. Sistem siap digunakan.`;
            } else {
                response = `Mohon maaf, hanya Admin yang dapat menjalankan perintah ini.`;
            }
        } else if (lowerCommand.includes('fund_vault')) {
            if (role === ROLES.FUNDER) {
                funderBalance = 100000000000000;
                funderToken = 10000;
                response = `✅ Vault terisi: 100T icp token<br>🎁 Sebagai funder Anda menerima 10.000 Token AEGIS.<br>Saldo token Funder = 10.000 AEGIS`;
            } else {
                response = `Mohon maaf, hanya Funder yang dapat menjalankan perintah ini.`;
            }
        } else if (lowerCommand.includes('declare_event')) {
            if (role === ROLES.ORGANIZER) {
                activeDaoId = 'lz3um-vp777-77777-aaaba-cai';
                response = `✅ Event Gempa Haiti 7.2 dibuat.<br>DAO aktif dengan ID: ${activeDaoId}.`;
            } else {
                response = `Mohon maaf, hanya Organizer yang dapat menjalankan perintah ini.`;
            }
        } else if (lowerCommand.includes('submit_proposal')) {
            if (role === ROLES.KOMUNITAS_KORBAN) {
                if (!activeDaoId) {
                     activeDaoId = 'lz3um-vp777-77777-aaaba-cai';
                }
                if (proposalList.length === 0) {
                    proposalList.push({ id: 0, title: "Pengadaan 100 Tenda Darurat", votes_for: 0, votes_against: 0, amount: "1 juta" });
                }
                response = `✅ Proposal **#0** terdaftar Pengadaan 100 Tenda Darurat dan 1 juta token icp.`;
            } else {
                response = `Mohon maaf, Anda tidak memiliki izin atau tidak ada DAO aktif.`;
            }
        } else if (lowerCommand.includes('register_did')) {
            if (role === ROLES.KOMUNITAS_PEDULI) {
                isProfileRegistered = true;
                response = `✅ Profil Komunitas Peduli berhasil terdaftar.`;
            } else {
                response = `Mohon maaf, hanya Komunitas Peduli yang dapat menjalankan perintah ini.`;
            }
        } else if (lowerCommand.includes('donateandvote')) {
             if (role === ROLES.KOMUNITAS_PEDULI && isProfileRegistered && proposalList.length > 0) {
                 proposalList[0].votes_for += 1;
                 response = `✅ Donasi terkirim 1 miliar<br>✅ Vote terekam<br>🎖️ SBT Donatur & Partisipasi untuk anda dan anda mendapatkan 1000 token aegis`;
             } else {
                 response = `Mohon maaf, pastikan Anda sudah mendaftar profil dan ada proposal aktif.`;
             }
        } else if (lowerCommand.includes('get_all_proposals')) {
             if (role === ROLES.ADMIN) {
                 const proposal = proposalList[0];
                 if (proposal && proposal.votes_for > 0) {
                    proposalApproved = true;
                    response = `📊 Proposal #0 → votes_for = ${proposal.votes_for}, votes_against = ${proposal.votes_against}<br>Status: Disetujui ✅`;
                 } else if (proposal) {
                     response = `📊 Proposal #0 → votes_for = 0, votes_against = 0<br>Status: Menunggu Vote...`;
                 } else {
                     response = `Tidak ada proposal aktif.`;
                 }
             } else {
                 response = `Mohon maaf, hanya Admin yang dapat menjalankan perintah ini.`;
             }
        } else if (lowerCommand.includes('execute_proposal')) {
            if (role === ROLES.KOMUNITAS_KORBAN) {
                if (proposalList.length === 0) {
                    proposalList.push({ id: 0, title: "Pengadaan 100 Tenda Darurat", votes_for: 0, votes_against: 0, amount: "1 juta" });
                }
                
                if (proposalApproved) {
                    response = `✅ Proposal #0 dieksekusi.<br>💰 Dana ${proposalList[0].amount} icp dicairkan dari vault ke Komunitas korban.<br>Status proposal: Selesai`;
                } else {
                     response = `✅ Proposal #0<br>💰 menunggu persetujuan admin untuk pencairan`;
                }
            } else {
                response = `Mohon maaf, Anda tidak memiliki izin atau tidak ada proposal aktif.`;
            }
        } else {
            response = `Perintah DFX tidak dikenali: "${command}".`;
        }
        return response;
    }

    // 5. EVENT HANDLERS
    loginBtn.addEventListener('click', () => {
        const role = prompt("Pilih peran Anda (Admin, Funder, Organizer, Komunitas Peduli, Komunitas Korban):");
        if (Object.values(ROLES).includes(role)) {
            currentRole = role;
            loginStatusEl.innerHTML = `Login sebagai: <b>${currentRole}</b>`;
            loginBtn.innerText = "Logout";
            
            if (currentRole === ROLES.ORGANIZER) {
                displayMessage("Terdapat laporan bencana dari oracle gempa lokasi haiti gempa manigtudo 7.2", "Aegis AI Assistant");
            } else {
                displayMessage(`Selamat datang, ${currentRole}. Sistem siap melayani Anda.`, "Aegis AI Assistant");
            }
        } else {
            alert('Peran tidak valid.');
        }
    });

    chatSendBtn.addEventListener('click', () => {
        const command = chatInput.value.trim();
        if (command && currentRole) {
            displayMessage(command, `Anda (${currentRole})`);
            chatInput.value = '';
            handleCommand(command, currentRole);
        } else if (!currentRole) {
            alert('Silakan login terlebih dahulu.');
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            chatSendBtn.click();
        }
    });
});
