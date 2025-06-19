# src/main.py

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import ArmoraGrenadeMainWindow

def main():
    """Main entry point of the Armora Grenade application."""
    app = QApplication(sys.argv)
    window = ArmoraGrenadeMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
