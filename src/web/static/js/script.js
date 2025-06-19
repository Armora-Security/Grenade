// src/web/static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const libvirtStatusSpan = document.getElementById('libvirt-status');
    const vmListContainer = document.getElementById('vm-list');
    const noVmMessage = document.getElementById('no-vm-message');
    const refreshVmsBtn = document.getElementById('refresh-vms-btn');
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    // --- Tab Switching Logic ---
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;

            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // --- API Calls ---

    async function fetchLibvirtStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            libvirtStatusSpan.textContent = data.libvirt_status;
            libvirtStatusSpan.classList.remove('connected', 'disconnected');
            libvirtStatusSpan.classList.add(data.connected ? 'connected' : 'disconnected');
        } catch (error) {
            console.error('Error fetching libvirt status:', error);
            libvirtStatusSpan.textContent = 'Failed to connect';
            libvirtStatusSpan.classList.remove('connected');
            libvirtStatusSpan.classList.add('disconnected');
        }
    }

    async function fetchVmList() {
        vmListContainer.innerHTML = ''; // Clear existing VMs
        noVmMessage.style.display = 'none'; // Hide no VM message
        
        try {
            const response = await fetch('/api/vms');
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to fetch VM list');
            }
            const data = await response.json();

            if (data.vms.length === 0) {
                noVmMessage.style.display = 'block';
                return;
            }

            data.vms.forEach(vm => {
                const vmCard = document.createElement('div');
                vmCard.className = `vm-card ${vm.status.toLowerCase()}`;
                vmCard.innerHTML = `
                    <div class="vm-header">
                        <h3>${vm.name} <span class="status-badge ${vm.status.toLowerCase()}">${vm.status}</span></h3>
                        <div class="vm-actions-card">
                            <button class="btn-icon start-btn" title="Start" data-vm-name="${vm.name}" ${vm.status === 'Running' ? 'disabled' : ''}><i class="fas fa-play"></i></button>
                            <button class="btn-icon stop-btn" title="Stop" data-vm-name="${vm.name}" ${vm.status !== 'Running' ? 'disabled' : ''}><i class="fas fa-stop"></i></button>
                            <button class="btn-icon settings-btn" title="Settings" data-vm-name="${vm.name}"><i class="fas fa-cog"></i></button>
                        </div>
                    </div>
                    <div class="vm-details">
                        <p><i class="fas fa-memory"></i> N/A RAM</p>
                        <p><i class="fas fa-hdd"></i> N/A Disk</p>
                    </div>
                `;
                vmListContainer.appendChild(vmCard);
            });

            // Attach event listeners to newly created buttons
            attachVmButtonListeners();

        } catch (error) {
            console.error('Error fetching VM list:', error);
            vmListContainer.innerHTML = `<p class="info-message error-message">Error: ${error.message}. Please check libvirt connection.</p>`;
        }
    }

    function attachVmButtonListeners() {
        document.querySelectorAll('.start-btn').forEach(button => {
            button.onclick = () => performVmAction(button.dataset.vmName, 'start');
        });
        document.querySelectorAll('.stop-btn').forEach(button => {
            button.onclick = () => performVmAction(button.dataset.vmName, 'stop');
        });
        // Add listeners for settings, etc. as you implement them
    }

    async function performVmAction(vmName, action) {
        if (!confirm(`Are you sure you want to ${action} '${vmName}'?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/vm/${vmName}/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            if (data.success) {
                alert(data.message);
                fetchVmList(); // Refresh VM list after action
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error(`Error performing ${action} on ${vmName}:`, error);
            alert(`An error occurred while trying to ${action} VM.`);
        }
    }

    // --- Event Listeners ---
    refreshVmsBtn.addEventListener('click', fetchVmList);

    // Initial load
    fetchLibvirtStatus();
    fetchVmList();
    
    // Optional: Refresh status/VMs periodically
    setInterval(fetchLibvirtStatus, 30000); // Every 30 seconds
    setInterval(fetchVmList, 60000); // Every 60 seconds (can be adjusted)
});
