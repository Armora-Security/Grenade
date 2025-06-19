# app/core/libvirt_manager.py

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
        if self.conn: # Already connected
            return True
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
        """Checks if the libvirt connection is active and responsive."""
        if self.conn:
            try:
                # Attempt to get a property to verify connection is still alive
                self.conn.getLibVersion()
                return True
            except libvirt.libvirtError:
                self.conn = None # Connection lost
                return False
        return False

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
        if not self.is_connected():
            return []
        try:
            domains = self.conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)
            return [d.name() for d in domains]
        except libvirt.libvirtError as e:
            print(f"Error listing active VMs: {e}", file=sys.stderr)
            return []

    def list_inactive_vms(self):
        """Lists the names of all inactive (stopped/defined but not running) virtual machines."""
        if not self.is_connected():
            return []
        try:
            domains = self.conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_INACTIVE)
            return [d.name() for d in domains]
        except libvirt.libvirtError as e:
            print(f"Error listing inactive VMs: {e}", file=sys.stderr)
            return []

    def get_domain_by_name(self, vm_name):
        """Returns a libvirt Domain object by its name."""
        if not self.is_connected():
            return None
        try:
            return self.conn.lookupByName(vm_name)
        except libvirt.libvirtError as e:
            # VIR_ERR_NO_DOMAIN means domain not found, which is expected for non-existent VMs
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
        """
        Gracefully shuts down a virtual machine by its name.
        Equivalent to a soft shutdown from within the OS.
        """
        domain = self.get_domain_by_name(vm_name)
        if domain:
            try:
                domain.shutdown()
                print(f"VM '{vm_name}' shutting down.")
                return True
            except libvirt.libvirtError as e:
                print(f"Error shutting down VM '{vm_name}': {e}", file=sys.stderr)
                return False
        return False

    def destroy_vm(self, vm_name):
        """
        Forcefully stops (powers off) a virtual machine by its name.
        Equivalent to pulling the power plug. Use with caution.
        """
        domain = self.get_domain_by_name(vm_name)
        if domain:
            try:
                domain.destroy()
                print(f"VM '{vm_name}' forcefully destroyed (powered off).")
                return True
            except libvirt.libvirtError as e:
                print(f"Error destroying VM '{vm_name}': {e}", file=sys.stderr)
                return False
        return False

    def suspend_vm(self, vm_name):
        """Suspends (pauses) a virtual machine by its name."""
        domain = self.get_domain_by_name(vm_name)
        if domain:
            try:
                domain.suspend()
                print(f"VM '{vm_name}' suspended.")
                return True
            except libvirt.libvirtError as e:
                print(f"Error suspending VM '{vm_name}': {e}", file=sys.stderr)
                return False
        return False

    def resume_vm(self, vm_name):
        """Resumes a suspended (paused) virtual machine by its name."""
        domain = self.get_domain_by_name(vm_name)
        if domain:
            try:
                domain.resume()
                print(f"VM '{vm_name}' resumed.")
                return True
            except libvirt.libvirtError as e:
                print(f"Error resuming VM '{vm_name}': {e}", file=sys.stderr)
                return False
        return False

    def delete_vm(self, vm_name):
        """
        Undefines (deletes) a virtual machine by its name.
        VM must be stopped/destroyed first.
        """
        domain = self.get_domain_by_name(vm_name)
        if domain:
            try:
                # Ensure VM is not running
                state, reason = domain.state()
                if state == libvirt.VIR_DOMAIN_RUNNING:
                    print(f"Error: VM '{vm_name}' is running. Stop or destroy it first.", file=sys.stderr)
                    return False
                elif state == libvirt.VIR_DOMAIN_PAUSED:
                     print(f"Error: VM '{vm_name}' is paused. Resume or destroy it first.", file=sys.stderr)
                     return False

                domain.undefine()
                print(f"VM '{vm_name}' undefined (deleted).")
                return True
            except libvirt.libvirtError as e:
                print(f"Error undefining VM '{vm_name}': {e}", file=sys.stderr)
                return False
        return False

    def create_vm(self, xml_config):
        """
        Defines a new virtual machine from an XML configuration string.
        Returns the domain object on success, None otherwise.
        """
        if not self.is_connected():
            return None
        try:
            domain = self.conn.defineXML(xml_config)
            print(f"VM '{domain.name()}' defined successfully.")
            return domain
        except libvirt.libvirtError as e:
            print(f"Error defining VM from XML: {e}", file=sys.stderr)
            return None

    # --- Storage Management Functions (Contoh Kerangka) ---
    def list_storage_pools(self):
        """Lists active storage pools."""
        if not self.is_connected():
            return []
        try:
            pools = self.conn.listAllStoragePools(libvirt.VIR_CONNECT_LIST_STORAGE_POOLS_ACTIVE)
            return [p.name() for p in pools]
        except libvirt.libvirtError as e:
            print(f"Error listing storage pools: {e}", file=sys.stderr)
            return []

    def list_volumes_in_pool(self, pool_name):
        """Lists volumes (virtual disks) in a specific storage pool."""
        if not self.is_connected():
            return []
        try:
            pool = self.conn.lookupStoragePoolByName(pool_name)
            if pool:
                volumes = pool.listAllVolumes(0) # 0 for all flags
                return [v.name() for v in volumes]
            return []
        except libvirt.libvirtError as e:
            print(f"Error listing volumes in pool '{pool_name}': {e}", file=sys.stderr)
            return []

    # --- Tambahan untuk mendapatkan detail VM ---
    def get_vm_details(self, vm_name):
        """
        Gets detailed information about a VM.
        Returns a dictionary or None.
        """
        domain = self.get_domain_by_name(vm_name)
        if not domain:
            return None
        
        details = {
            'name': domain.name(),
            'uuid': domain.UUIDString(),
            'id': domain.ID() if domain.ID() != -1 else None, # -1 for inactive
            'memory_kb': domain.info().memory,
            'max_memory_kb': domain.info().maxMem,
            'vcpu': domain.info().nrVirtCpu,
            'os_type': domain.OSType(),
            'state': self._get_vm_state_string(domain.info().state),
            'autostart': domain.autostart(),
            'devices': [] # This would require parsing XML for disks, nics, etc.
        }

        # Parse XML for more details (disks, networks, etc.) - this is more complex
        # xml_desc = domain.XMLDesc(0)
        # You'd use an XML parser (e.g., xml.etree.ElementTree) here
        
        return details

    def _get_vm_state_string(self, state_code):
        """Helper to convert libvirt state code to readable string."""
        states = {
            libvirt.VIR_DOMAIN_NOSTATE: 'No State',
            libvirt.VIR_DOMAIN_RUNNING: 'Running',
            libvirt.VIR_DOMAIN_BLOCKED: 'Blocked',
            libvirt.VIR_DOMAIN_PAUSED: 'Paused',
            libvirt.VIR_DOMAIN_SHUTDOWN: 'Shutdown',
            libvirt.VIR_DOMAIN_SHUTOFF: 'Stopped',
            libvirt.VIR_DOMAIN_CRASHED: 'Crashed',
            libvirt.VIR_DOMAIN_PMSUSPENDED: 'Suspended'
        }
        return states.get(state_code, 'Unknown')
