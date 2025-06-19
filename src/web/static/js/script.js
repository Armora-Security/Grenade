// src/web/static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const libvirtStatusSpan = document.getElementById('libvirt-status');
    const vmListContainer = document.getElementById('vm-list');
    const noVmMessage = document.getElementById('no-vm-message');
    const refreshVmsBtn = document.getElementById('refresh-vms-btn');
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    // Create VM Form elements
    const createVmForm = document.getElementById('create-vm-form');
    const createVmMessage = document.getElementById('create-vm-message');
    const vmNameInput = document.getElementById('vm-name');
    const vmMemoryInput = document.getElementById('vm-memory');
    const vmVcpuInput = document.getElementById('vm-vcpu');
    const vmDiskPathInput = document.getElementById('vm-disk-path');
    const vmDiskSizeInput = document.getElementById('vm-disk-size');
    const vmIsoPathInput = document.getElementById('vm-iso-path');
    const vmNetworkBridgeInput = document.getElementById('vm-network-bridge');

    // Storage Tab elements
    const refreshPoolsBtn = document.getElementById('refresh-pools-btn');
    const storagePoolsList = document.getElementById('storage-pools-list');
    const noPoolMessage = document.getElementById('no-pool-message');


    // --- Tab Switching Logic ---
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;

            // Remove 'active' class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add 'active' class to the clicked button and corresponding content
            button.classList.add('active');
            document.getElementById(tabId).classList.add('active');

            // Optionally, trigger a refresh when switching to certain tabs
            if (tabId === 'vms') {
                fetchVmList();
            } else if (tabId === 'storage') {
                fetchStoragePools();
            }
            // Add more conditions for other tabs
        });
    });

    // --- API Calls ---

    async function fetchLibvirtStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            libvirtStatusSpan.textContent = `Connected: ${data.libvirt_status}`;
            libvirtStatusSpan.classList.remove('connected', 'disconnected');
            libvirtStatusSpan.classList.add(data.connected ? 'connected' : 'disconnected');
        } catch (error) {
            console.error('Error fetching libvirt status:', error);
            libvirtStatusSpan.textContent = 'Connection Failed';
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
                vmCard.className = `vm-card ${vm.status.toLowerCase().replace(/\s/g, '-')}`; // e.g., 'running' or 'stopped' or 'no-state'
                vmCard.innerHTML = `
                    <div class="vm-header">
                        <h3>${vm.name} <span class="status-badge ${vm.status.replace(/\s/g, '')}">${vm.status}</span></h3>
                        <div class="vm-actions-card">
                            <button class="btn-icon start-btn" title="Start VM" data-vm-name="${vm.name}" ${vm.status === 'Running' || vm.status === 'Paused' ? 'disabled' : ''}><i class="fas fa-play"></i></button>
                            <button class="btn-icon stop-btn" title="Graceful Shutdown" data-vm-name="${vm.name}" ${vm.status !== 'Running' ? 'disabled' : ''}><i class="fas fa-power-off"></i></button>
                            <button class="btn-icon destroy-btn" title="Force Power Off" data-vm-name="${vm.name}" ${vm.status === 'Stopped' || vm.status === 'Shutdown' || vm.status === 'No State' ? 'disabled' : ''}><i class="fas fa-fire"></i></button>
                            <button class="btn-icon suspend-btn" title="Suspend VM" data-vm-name="${vm.name}" ${vm.status !== 'Running' ? 'disabled' : ''}><i class="fas fa-pause"></i></button>
                            <button class="btn-icon resume-btn" title="Resume VM" data-vm-name="${vm.name}" ${vm.status !== 'Paused' ? 'disabled' : ''}><i class="fas fa-play-circle"></i></button>
                            <button class="btn-icon delete-btn" title="Delete VM (Undefine)" data-vm-name="${vm.name}" ${vm.status === 'Running' || vm.status === 'Paused' ? 'disabled' : ''}><i class="fas fa-trash-alt"></i></button>
                        </div>
                    </div>
                    <div class="vm-details">
                        <p><i class="fas fa-microchip"></i> ${vm.vcpu} vCPU</p>
                        <p><i class="fas fa-memory"></i> ${vm.memory_mb} MB RAM</p>
                        <p><i class="fas fa-fingerprint"></i> ${vm.uuid}</p>
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
        document.querySelectorAll('.destroy-btn').forEach(button => {
            button.onclick = () => performVmAction(button.dataset.vmName, 'destroy', true); // Confirm destroy
        });
        document.querySelectorAll('.suspend-btn').forEach(button => {
            button.onclick = () => performVmAction(button.dataset.vmName, 'suspend');
        });
        document.querySelectorAll('.resume-btn').forEach(button => {
            button.onclick = () => performVmAction(button.dataset.vmName, 'resume');
        });
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.onclick = () => performVmAction(button.dataset.vmName, 'delete', true); // Confirm delete
        });
    }

    async function performVmAction(vmName, action, requiresConfirmation = false) {
        if (requiresConfirmation) {
            let confirmMsg;
            if (action === 'destroy') {
                confirmMsg = `WARNING: Are you sure you want to FORCE POWER OFF '${vmName}'? This is like pulling the power plug and may cause data loss!`;
            } else if (action === 'delete') {
                confirmMsg = `WARNING: Are you sure you want to DELETE (UNDEFINE) '${vmName}'? This will remove its definition from libvirt. Its disk image might remain.`;
            } else {
                confirmMsg = `Are you sure you want to ${action} '${vmName}'?`;
            }
            if (!confirm(confirmMsg)) {
                return;
            }
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

    async function handleCreateVm(event) {
        event.preventDefault(); // Prevent default form submission

        // Clear previous messages
        createVmMessage.style.display = 'none';
        createVmMessage.classList.remove('success-message', 'error-message');

        const vmData = {
            name: vmNameInput.value,
            memory_mb: parseInt(vmMemoryInput.value),
            vcpu: parseInt(vmVcpuInput.value),
            disk_path: vmDiskPathInput.value,
            disk_size_gb: parseInt(vmDiskSizeInput.value),
            os_iso_path: vmIsoPathInput.value || null,
            network_bridge: vmNetworkBridgeInput.value
        };

        // Basic validation
        if (!vmData.name || !vmData.memory_mb || !vmData.vcpu || !vmData.disk_path || !vmData.disk_size_gb || !vmData.network_bridge) {
            createVmMessage.textContent = "Please fill in all required fields.";
            createVmMessage.classList.add('error-message');
            createVmMessage.style.display = 'block';
            return;
        }

        try {
            const response = await fetch('/api/vm/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(vmData)
            });
            const data = await response.json();

            if (data.success) {
                createVmMessage.textContent = data.message;
                createVmMessage.classList.add('success-message');
                // Optionally clear form or switch tab
                createVmForm.reset();
                // Switch to VMs tab to show new VM
                document.querySelector('.tab-button[data-tab="vms"]').click();
            } else {
                createVmMessage.textContent = 'Error: ' + data.error;
                createVmMessage.classList.add('error-message');
            }
            createVmMessage.style.display = 'block';

        } catch (error) {
            console.error('Error creating VM:', error);
            createVmMessage.textContent = 'An unexpected error occurred during VM creation.';
            createVmMessage.classList.add('error-message');
            createVmMessage.style.display = 'block';
        }
    }


    async function fetchStoragePools() {
        storagePoolsList.innerHTML = ''; // Clear existing pools
        noPoolMessage.style.display = 'none'; // Hide no pool message

        try {
            const response = await fetch('/api/storage/pools'); // You need to create this endpoint in Flask
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to fetch storage pools');
            }
            const data = await response.json();

            if (data.pools.length === 0) {
                noPoolMessage.style.display = 'block';
                return;
            }

            data.pools.forEach(pool => {
                const poolCard = document.createElement('div');
                poolCard.className = `vm-card`; // Re-use vm-card style, or create specific storage-card
                poolCard.innerHTML = `
                    <div class="vm-header">
                        <h3><i class="fas fa-box"></i> ${pool.name} <span class="status-badge Running">${pool.status}</span></h3>
                    </div>
                    <div class="vm-details">
                        <p><i class="fas fa-folder"></i> Path: ${pool.path}</p>
                        <p><i class="fas fa-sd-card"></i> Capacity: ${pool.capacity_gb} GB</p>
                        <p><i class="fas fa-chart-pie"></i> Used: ${pool.used_gb} GB</p>
                    </div>
                `;
                storagePoolsList.appendChild(poolCard);
            });

        } catch (error) {
            console.error('Error fetching storage pools:', error);
            storagePoolsList.innerHTML = `<p class="info-message error-message">Error: ${error.message}.</p>`;
        }
    }


    // --- Event Listeners ---
    refreshVmsBtn.addEventListener('click', fetchVmList);
    createVmForm.addEventListener('submit', handleCreateVm);
    refreshPoolsBtn.addEventListener('click', fetchStoragePools);


    // Initial load when page loads
    fetchLibvirtStatus();
    fetchVmList();
    fetchStoragePools(); // Initial load for storage pools as well
    
    // Optional: Refresh status/VMs periodically
    setInterval(fetchLibvirtStatus, 30000); // Every 30 seconds
    setInterval(fetchVmList, 60000); // Every 60 seconds (can be adjusted)
    // setInterval(fetchStoragePools, 120000); // Every 2 minutes
});
