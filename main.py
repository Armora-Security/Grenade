# main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt
import libvirt
import os
import platform

class ArmoraGrenadeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Armora Grenade - Virtualization Management")
        self.setGeometry(100, 100, 800, 600)

        self.connection = None
        self.connect_to_libvirt()

        self.init_ui()

    def connect_to_libvirt(self):
        """Attempts to connect to the libvirt daemon."""
        try:
            # Try to connect as read-write, then read-only if that fails
            # For local connection, typically 'qemu:///system' or 'qemu+unix:///system'
            # Adjust based on your libvirt setup
            self.connection = libvirt.open('qemu:///system')
            if self.connection is None:
                raise libvirt.libvirtError('Failed to open connection to qemu:///system')
            print("Successfully connected to libvirt!")
            QMessageBox.information(self, "Connection Success", "Successfully connected to libvirt daemon.")

        except libvirt.libvirtError as e:
            msg = f"Failed to connect to libvirt daemon: {e}\n\nPlease ensure libvirt is installed, configured, and the 'libvirtd' service is running. Also, make sure your user is part of the 'libvirt' group."
            QMessageBox.critical(self, "Connection Error", msg)
            self.connection = None
            # Optionally, disable UI elements if connection fails
            # self.close() # Or disable all functionality
            print(f"Error connecting to libvirt: {e}")

    def init_ui(self):
        """Initializes the main user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Title
        title_label = QLabel("Welcome to Armora Grenade!")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # Connection Status
        self.status_label = QLabel("Libvirt Status: Disconnected")
        if self.connection:
            self.status_label.setText("Libvirt Status: Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Example buttons (you'll expand these)
        btn_list_vms = QPushButton("List Virtual Machines")
        btn_list_vms.clicked.connect(self.list_vms)
        layout.addWidget(btn_list_vms)

        btn_create_vm = QPushButton("Create New VM (Not Implemented)")
        btn_create_vm.setEnabled(False) # Disable for now
        layout.addWidget(btn_create_vm)

        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.close)
        layout.addWidget(btn_exit)

        layout.addStretch(1) # Pushes content to the top

    def list_vms(self):
        """Lists active virtual machines."""
        if not self.connection:
            QMessageBox.warning(self, "Not Connected", "Cannot list VMs. Not connected to libvirt.")
            return

        try:
            dom_ids = self.connection.listDomainsID()
            if not dom_ids:
                QMessageBox.information(self, "No VMs", "No active virtual machines found.")
                return

            vm_list = []
            for dom_id in dom_ids:
                dom = self.connection.lookupByID(dom_id)
                vm_list.append(f"- {dom.name()} (ID: {dom_id}, State: {dom.state()[0]})")
            
            QMessageBox.information(self, "Active Virtual Machines", "\n".join(vm_list))

        except libvirt.libvirtError as e:
            QMessageBox.critical(self, "Error Listing VMs", f"Failed to list VMs: {e}")

    def closeEvent(self, event):
        """Handles application close event, ensuring libvirt connection is closed."""
        if self.connection:
            print("Closing libvirt connection...")
            self.connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArmoraGrenadeApp()
    window.show()
    sys.exit(app.exec_())
