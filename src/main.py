# src/main.py

from flask import Flask, render_template, jsonify, request
import os
from core.libvirt_manager import LibvirtManager

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'web/templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'web/static'))

libvirt_manager = LibvirtManager()

@app.route('/')
def index():
    """Renders the main dashboard page."""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Returns the current connection status to libvirt."""
    connected = libvirt_manager.connect() # Attempt to connect if not already
    status = "Connected" if connected else "Disconnected"
    return jsonify({"libvirt_status": status, "connected": connected})

@app.route('/api/vms')
def get_vms():
    """Returns a list of all virtual machines (active and inactive) with basic details."""
    if not libvirt_manager.is_connected():
        return jsonify({"error": "Not connected to libvirt"}), 500

    all_vms = []
    try:
        # Get all domains (active and inactive)
        domains = libvirt_manager.conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE | libvirt.VIR_CONNECT_LIST_DOMAINS_INACTIVE)
        
        for dom in domains:
            state_code, _ = dom.state()
            state_string = libvirt_manager._get_vm_state_string(state_code)
            all_vms.append({
                "name": dom.name(),
                "status": state_string,
                "icon": "🟢" if state_string == "Running" else ("⏸️" if state_string == "Paused" else "⚫"),
                # You can add more simple details here without parsing XML heavily
                "vcpu": dom.info().nrVirtCpu,
                "memory_mb": int(dom.info().memory / 1024), # Convert KB to MB
                "uuid": dom.UUIDString()
            })
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve VMs: {e}"}), 500
    
    return jsonify({"vms": all_vms})

@app.route('/api/vm/<name>/<action>', methods=['POST'])
def vm_action(name, action):
    """Performs an action (start/stop/destroy/suspend/resume) on a specific VM."""
    if not libvirt_manager.is_connected():
        return jsonify({"error": "Not connected to libvirt"}), 500

    success = False
    message = ""

    if action == 'start':
        success = libvirt_manager.start_vm(name)
        message = f"VM '{name}' {'started successfully' if success else 'failed to start'}."
    elif action == 'stop':
        success = libvirt_manager.stop_vm(name)
        message = f"VM '{name}' {'shutting down gracefully' if success else 'failed to shut down gracefully'}."
    elif action == 'destroy':
        success = libvirt_manager.destroy_vm(name)
        message = f"VM '{name}' {'forcefully powered off' if success else 'failed to power off'}."
    elif action == 'suspend':
        success = libvirt_manager.suspend_vm(name)
        message = f"VM '{name}' {'suspended' if success else 'failed to suspend'}."
    elif action == 'resume':
        success = libvirt_manager.resume_vm(name)
        message = f"VM '{name}' {'resumed' if success else 'failed to resume'}."
    elif action == 'delete':
        success = libvirt_manager.delete_vm(name)
        message = f"VM '{name}' {'deleted' if success else 'failed to delete'}."
    else:
        return jsonify({"error": "Invalid action"}), 400

    if success:
        return jsonify({"message": message, "success": True})
    else:
        return jsonify({"message": message, "success": False}), 500

@app.route('/api/vm/create', methods=['POST'])
def create_new_vm():
    """Endpoint to create a new VM."""
    if not libvirt_manager.is_connected():
        return jsonify({"error": "Not connected to libvirt"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for VM creation"}), 400

    vm_name = data.get('name')
    memory_mb = data.get('memory_mb', 512)
    vcpu = data.get('vcpu', 1)
    disk_path = data.get('disk_path', '/var/lib/libvirt/images/new_vm.qcow2')
    disk_size_gb = data.get('disk_size_gb', 10)
    os_iso_path = data.get('os_iso_path') # Optional: path to an ISO for installation
    network_bridge = data.get('network_bridge', 'virbr0') # Default libvirt bridge

    if not vm_name:
        return jsonify({"error": "VM name is required"}), 400

    # Basic XML template for a new VM (QEMU/KVM)
    # This is a very basic template and should be expanded for more options
    xml_config = f"""
    <domain type='kvm'>
      <name>{vm_name}</name>
      <uuid>{libvirt.virDomainGenerateUUID()}</uuid>
      <memory unit='MiB'>{memory_mb}</memory>
      <currentMemory unit='MiB'>{memory_mb}</currentMemory>
      <vcpu placement='static'>{vcpu}</vcpu>
      <os>
        <type arch='x86_64' machine='pc'>hvm</type>
      </os>
      <features>
        <acpi/>
        <apic/>
      </features>
      <cpu mode='host-passthrough' check='partial'/>
      <clock offset='utc'/>
      <on_poweroff>destroy</on_poweroff>
      <on_reboot>restart</on_reboot>
      <on_crash>destroy</on_crash>
      <devices>
        <emulator>/usr/local/bin/qemu-system-x86_64</emulator> <disk type='file' device='disk'>
          <driver name='qemu' type='qcow2'/>
          <source file='{disk_path}'/>
          <target dev='vda' bus='virtio'/>
          <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
        </disk>
        <interface type='bridge'>
          <source bridge='{network_bridge}'/>
          <model type='virtio'/>
          <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
        </interface>
        <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
          <listen type='address' address='0.0.0.0'/>
        </graphics>
        <console type='pty'>
          <target type='serial' port='0'/>
        </console>
        <channel type='spicevmc'>
          <target type='virtio' name='com.redhat.spice.0'/>
        </channel>
      </devices>
    </domain>
    """
    # Note: Disk creation (qcow2 file) itself is not handled by libvirt.
    # You'd typically create the disk image first using qemu-img.
    # E.g., qemu-img create -f qcow2 /var/lib/libvirt/images/new_vm.qcow2 10G

    domain = libvirt_manager.create_vm(xml_config)
    if domain:
        return jsonify({"message": f"VM '{vm_name}' created successfully!", "success": True})
    else:
        return jsonify({"error": f"Failed to create VM '{vm_name}'. Check logs for details."}), 500

if __name__ == '__main__':
    # Ensure libvirt connection is attempted on startup
    if not libvirt_manager.is_connected():
        print("Attempting initial connection to libvirt...")
        libvirt_manager.connect()
    
    app.run(debug=True, host='0.0.0.0', port=5000) # Run in debug mode for development
