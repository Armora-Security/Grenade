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
    """Returns a list of all virtual machines (active and inactive)."""
    if not libvirt_manager.is_connected():
        return jsonify({"error": "Not connected to libvirt"}), 500

    active_vms = libvirt_manager.list_active_vms()
    inactive_vms = libvirt_manager.list_inactive_vms()

    vms_data = []
    for vm_name in active_vms:
        vms_data.append({"name": vm_name, "status": "Running", "icon": "🟢"})
    for vm_name in inactive_vms:
        vms_data.append({"name": vm_name, "status": "Stopped", "icon": "⚫"})
    
    return jsonify({"vms": vms_data})

@app.route('/api/vm/<name>/<action>', methods=['POST'])
def vm_action(name, action):
    """Performs an action (start/stop) on a specific VM."""
    if not libvirt_manager.is_connected():
        return jsonify({"error": "Not connected to libvirt"}), 500

    success = False
    message = ""

    if action == 'start':
        success = libvirt_manager.start_vm(name)
        message = f"VM '{name}' {'started successfully' if success else 'failed to start'}."
    elif action == 'stop':
        success = libvirt_manager.stop_vm(name)
        message = f"VM '{name}' {'stopped successfully' if success else 'failed to stop'}."
    else:
        return jsonify({"error": "Invalid action"}), 400

    if success:
        return jsonify({"message": message, "success": True})
    else:
        return jsonify({"message": message, "success": False}), 500

if __name__ == '__main__':
    # Ensure libvirt connection is attempted on startup
    if not libvirt_manager.is_connected():
        print("Attempting initial connection to libvirt...")
        libvirt_manager.connect()
    
    app.run(debug=True, host='0.0.0.0', port=5000) # Run in debug mode for development
