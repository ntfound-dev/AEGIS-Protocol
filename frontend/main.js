// ======================================================
// AEGIS PROTOCOL - main.js
// Simulasi Lengkap Semua Peran
// ======================================================

document.addEventListener('DOMContentLoaded', () => {

    // 1. UI ELEMENTS
    const loginBtn = document.getElementById('loginBtn');
    const loginStatusEl = document.getElementById('loginStatus');
    const chatWindow = document.getElementById('chatWindow');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');

    // 2. SIMULASI APLIKASI STATE
    let currentRole = null;
    let funderBalance = 0;
    let funderToken = 0;
    let activeDaoId = null;
    let proposalList = [];
    let isProfileRegistered = false;
    let proposalApproved = false;

    const ROLES = {
        ADMIN: 'Admin',
        FUNDER: 'Funder',
        ORGANIZER: 'Organizer',
        KOMUNITAS_PEDULI: 'Komunitas Peduli',
        KOMUNITAS_KORBAN: 'Komunitas Korban'
    };

    // 3. MESSAGE DISPLAY FUNCTION
    function displayMessage(content, sender, isImage = false) {
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('message', sender.includes('Anda') ? 'user-message' : 'agent-message');
        
        const messageIcon = document.createElement('div');
        messageIcon.classList.add('message-icon');
        
        if (sender === 'Aegis AI Assistant') {
            messageIcon.innerHTML = '<i class="fas fa-robot"></i>';
        } else {
            messageIcon.innerHTML = '<i class="fas fa-user-circle"></i>';
        }

        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        const messageHeader = document.createElement('div');
        messageHeader.classList.add('message-header');
        messageHeader.innerHTML = `
            <span class="sender">${sender}</span>
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
        `;
        messageContent.appendChild(messageHeader);

        let element = document.createElement('p');
        element.innerHTML = content;
        
        messageContent.appendChild(element);
        messageContainer.appendChild(messageIcon);
        messageContainer.appendChild(messageContent);
        chatWindow.appendChild(messageContainer);
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
