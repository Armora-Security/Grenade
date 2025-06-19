# app/ui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox, QTabWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from core.libvirt_manager import LibvirtManager # Import LibvirtManager
import os
import platform

class ArmoraGrenadeMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Armora Grenade - Virtualization Management")
        self.setGeometry(100, 100, 1024, 768) # Ukuran jendela yang lebih besar

        self.libvirt_manager = LibvirtManager() # Inisialisasi LibvirtManager
        self.connect_to_libvirt()

        self.init_ui()
        self.load_vm_list() # Muat daftar VM saat aplikasi dimulai

    def connect_to_libvirt(self):
        """Attempts to connect to the libvirt daemon."""
        if not self.libvirt_manager.connect():
            msg = "Failed to connect to libvirt daemon.\n\nPlease ensure libvirt is installed, configured, and the 'libvirtd' service is running. Also, make sure your user is part of the 'libvirt' group."
            QMessageBox.critical(self, "Connection Error", msg)
            # Opsional: Tutup aplikasi jika koneksi gagal total
            # sys.exit(1)

    def init_ui(self):
        """Initializes the main user interface layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header Section
        header_layout = QVBoxLayout()
        title_label = QLabel("Armora Grenade: Ultimate BSD Virtualization")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; padding: 10px; color: #333;")
        
        self.status_label = QLabel("Libvirt Status: Disconnected")
        if self.libvirt_manager.is_connected():
            self.status_label.setText("Libvirt Status: Connected")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;") # Green
        else:
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;") # Red
        self.status_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(self.status_label)
        main_layout.addLayout(header_layout)

        # Tab Widget for different management sections
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # --- VMs Tab ---
        self.vms_tab = QWidget()
        vms_layout = QVBoxLayout()
        self.vms_tab.setLayout(vms_layout)
        self.tab_widget.addTab(self.vms_tab, "Virtual Machines")

        # VM List
        self.vm_list_widget = QListWidget()
        vms_layout.addWidget(self.vm_list_widget)

        # VM Actions Buttons
        vm_buttons_layout = QVBoxLayout() # Menggunakan QVBoxLayout agar tombol ke bawah
        self.btn_refresh_vms = QPushButton("Refresh VM List")
        self.btn_refresh_vms.clicked.connect(self.load_vm_list)
        
        self.btn_start_vm = QPushButton("Start VM")
        self.btn_start_vm.clicked.connect(self.start_selected_vm)
        self.btn_start_vm.setEnabled(False) # Awalnya nonaktif
        
        self.btn_stop_vm = QPushButton("Stop VM")
        self.btn_stop_vm.clicked.connect(self.stop_selected_vm)
        self.btn_stop_vm.setEnabled(False) # Awalnya nonaktif

        self.btn_create_vm = QPushButton("Create New VM (Not Implemented)")
        self.btn_create_vm.setEnabled(False) # Nonaktifkan sementara
        
        vm_buttons_layout.addWidget(self.btn_refresh_vms)
        vm_buttons_layout.addWidget(self.btn_start_vm)
        vm_buttons_layout.addWidget(self.btn_stop_vm)
        vm_buttons_layout.addWidget(self.btn_create_vm)
        
        vms_layout.addLayout(vm_buttons_layout)

        # Connect list selection to button state
        self.vm_list_widget.itemSelectionChanged.connect(self.update_vm_button_state)

        # --- Other Tabs (Placeholders) ---
        storage_tab = QWidget()
        storage_layout = QVBoxLayout()
        storage_tab.setLayout(storage_layout)
        storage_layout.addWidget(QLabel("Storage Management Coming Soon!"))
        self.tab_widget.addTab(storage_tab, "Storage")

        network_tab = QWidget()
        network_layout = QVBoxLayout()
        network_tab.setLayout(network_layout)
        network_layout.addWidget(QLabel("Network Configuration Coming Soon!"))
        self.tab_widget.addTab(network_tab, "Network")

        # Footer
        footer_label = QLabel("Armora Grenade © 2025 Armora Security. All rights reserved.")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("font-size: 12px; color: #777; margin-top: 20px;")
        main_layout.addWidget(footer_label)

        # Apply basic stylesheet (from assets/styles/style.qss)
        self.apply_stylesheet()

    def apply_stylesheet(self):
        """Loads and applies the QSS stylesheet."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        qss_path = os.path.join(current_dir, '../assets/styles/style.qss')
        if os.path.exists(qss_path):
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: Stylesheet not found at {qss_path}")

    def load_vm_list(self):
        """Loads and displays the list of virtual machines."""
        self.vm_list_widget.clear()
        if not self.libvirt_manager.is_connected():
            self.vm_list_widget.addItem("Not connected to libvirt. Please check connection.")
            return

        try:
            active_domains = self.libvirt_manager.list_active_vms()
            inactive_domains = self.libvirt_manager.list_inactive_vms()

            if not active_domains and not inactive_domains:
                self.vm_list_widget.addItem("No virtual machines found.")
                return

            if active_domains:
                self.vm_list_widget.addItem("--- Active VMs ---")
                for vm_name in active_domains:
                    self.vm_list_widget.addItem(f"🟢 {vm_name} (Running)")
            
            if inactive_domains:
                if active_domains: # Add separator if both exist
                    self.vm_list_widget.addItem("-----------------")
                self.vm_list_widget.addItem("--- Inactive VMs ---")
                for vm_name in inactive_domains:
                    self.vm_list_widget.addItem(f"⚫ {vm_name} (Stopped)")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load VM list: {e}")

    def get_selected_vm_name(self):
        """Returns the name of the currently selected VM."""
        selected_items = self.vm_list_widget.selectedItems()
        if not selected_items:
            return None
        
        # Extract VM name from the list item text (e.g., "🟢 MyVM (Running)")
        item_text = selected_items[0].text()
        if "---" in item_text: # Avoid selecting header items
            return None
        
        # Simple regex or string splitting might be needed for robust parsing
        # For now, let's assume format "🟢 Name (State)" or "⚫ Name (State)"
        vm_name = item_text.split('(')[0].strip()
        if vm_name.startswith('🟢') or vm_name.startswith('⚫'):
             vm_name = vm_name[1:].strip()
        return vm_name

    def update_vm_button_state(self):
        """Enables/disables VM action buttons based on selection."""
        selected_vm_name = self.get_selected_vm_name()
        
        self.btn_start_vm.setEnabled(False)
        self.btn_stop_vm.setEnabled(False)

        if selected_vm_name and self.libvirt_manager.is_connected():
            try:
                domain = self.libvirt_manager.get_domain_by_name(selected_vm_name)
                if domain:
                    state, reason = domain.state()
                    if state == libvirt.VIR_DOMAIN_RUNNING:
                        self.btn_stop_vm.setEnabled(True)
                    elif state == libvirt.VIR_DOMAIN_SHUTOFF or state == libvirt.VIR_DOMAIN_PAUSED:
                        self.btn_start_vm.setEnabled(True)
            except Exception as e:
                print(f"Error checking VM state for button update: {e}")
                # Fallback to disabled state if error occurs
                self.btn_start_vm.setEnabled(False)
                self.btn_stop_vm.setEnabled(False)

    def start_selected_vm(self):
        """Starts the selected virtual machine."""
        vm_name = self.get_selected_vm_name()
        if not vm_name:
            QMessageBox.warning(self, "No VM Selected", "Please select a virtual machine to start.")
            return

        if self.libvirt_manager.start_vm(vm_name):
            QMessageBox.information(self, "VM Started", f"Virtual machine '{vm_name}' started successfully.")
            self.load_vm_list() # Refresh list
        else:
            QMessageBox.critical(self, "Error", f"Failed to start virtual machine '{vm_name}'.")

    def stop_selected_vm(self):
        """Stops (shuts down) the selected virtual machine."""
        vm_name = self.get_selected_vm_name()
        if not vm_name:
            QMessageBox.warning(self, "No VM Selected", "Please select a virtual machine to stop.")
            return

        reply = QMessageBox.question(self, 'Confirm Stop', f"Are you sure you want to stop '{vm_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        if self.libvirt_manager.stop_vm(vm_name):
            QMessageBox.information(self, "VM Stopped", f"Virtual machine '{vm_name}' stopped successfully.")
            self.load_vm_list() # Refresh list
        else:
            QMessageBox.critical(self, "Error", f"Failed to stop virtual machine '{vm_name}'.")

    def closeEvent(self, event):
        """Handles application close event, ensuring libvirt connection is closed."""
        if self.libvirt_manager:
            self.libvirt_manager.disconnect()
        event.accept()
