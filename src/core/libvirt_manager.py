# src/core/libvirt_manager.py

import libvirt
import sys

class LibvirtManager:
    def __init__(self, uri='qemu:///system'):
        self.uri = uri
        self.conn = None

    def connect(self):
        """
        Attempts to establish a connection to the libvirt daemon.
        Returns True on success, False otherwise.
        """
        try:
            self.conn = libvirt.open(self.uri)
            if self.conn is None:
                print(f"Error: Failed to open connection to '{self.uri}'", file=sys.stderr)
                return False
            print(f"Successfully connected to libvirt at '{self.uri}'")
            return True
        except libvirt.libvirtError as e:
            print(f"Libvirt connection error: {e}", file=sys.stderr)
            self.conn = None
            return False

    def is_connected(self):
        """Checks if the libvirt connection is active."""
        return self.conn is not None

    def disconnect(self):
        """Closes the libvirt connection."""
        if self.conn:
            try:
                self.conn.close()
                print("Disconnected from libvirt.")
            except libvirt.libvirtError as e:
                print(f"Error closing libvirt connection: {e}", file=sys.stderr)
            finally:
                self.conn = None

    def list_active_vms(self):
        """Lists the names of all active (running) virtual machines."""
        if not self.conn:
            return []
        try:
            domains = self.conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)
            return [d.name() for d in domains]
        except libvirt.libvirtError as e:
            print(f"Error listing active VMs: {e}", file=sys.stderr)
            return []

    def list_inactive_vms(self):
        """Lists the names of all inactive (stopped/defined but not running) virtual machines."""
        if not self.conn:
            return []
        try:
            domains = self.conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_INACTIVE)
            return [d.name() for d in domains]
        except libvirt.libvirtError as e:
            print(f"Error listing inactive VMs: {e}", file=sys.stderr)
            return []

    def get_domain_by_name(self, vm_name):
        """Returns a libvirt Domain object by its name."""
        if not self.conn:
            return None
        try:
            return self.conn.lookupByName(vm_name)
        except libvirt.libvirtError as e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                print(f"VM '{vm_name}' not found.", file=sys.stderr)
            else:
                print(f"Error looking up domain '{vm_name}': {e}", file=sys.stderr)
            return None

    def start_vm(self, vm_name):
        """Starts a virtual machine by its name."""
        domain = self.get_domain_by_name(vm_name)
        if domain:
            try:
                domain.create() # 'create' starts the domain
                print(f"VM '{vm_name}' started.")
                return True
            except libvirt.libvirtError as e:
                print(f"Error starting VM '{vm_name}': {e}", file=sys.stderr)
                return False
        return False

    def stop_vm(self, vm_name):
        """Shuts down a virtual machine by its name."""
        domain = self.get_domain_by_name(vm_name)
        if domain:
            try:
                # Use shutdown for a graceful shutdown, or destroy for immediate power-off
                domain.shutdown() 
                print(f"VM '{vm_name}' shutting down.")
                # You might want a loop here to wait for the VM to actually shut off
                return True
            except libvirt.libvirtError as e:
                print(f"Error stopping VM '{vm_name}': {e}", file=sys.stderr)
                return False
        return False

   
    # def create_vm(self, xml_config): ...
    # def delete_vm(self, vm_name): ...
    # def take_snapshot(self, vm_name, snapshot_name): ...
