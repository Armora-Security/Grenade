# Armora Grenade: The Ultimate BSD Virtualization Management Solution

## Unleash the Power of Virtualization with Unparalleled Elegance

Armora Grenade redefines virtualization management. Built on the rock-solid foundation of BSD, it offers an exceptionally stable and secure platform for all your virtualized environments. What truly sets Armora Grenade apart is its breathtakingly intuitive and visually stunning graphical user interface (GUI). Forget clunky, command-line heavy tools; Armora Grenade makes managing your virtual machines a delightful experience.

Whether you're a seasoned sysadmin or new to virtualization, Armora Grenade's elegant design and powerful features empower you to deploy, monitor, and control your VMs with unprecedented ease and efficiency.

-----

## Key Features

  * **BSD-Powered Stability:** Leveraging the legendary reliability and security of BSD for a robust virtualization backbone.
  * **Stunning & Intuitive GUI:** A modern, responsive, and aesthetically pleasing interface that simplifies complex tasks.
  * **Effortless VM Management:** Create, start, stop, pause, snapshot, and clone VMs with just a few clicks.
  * **Resource Monitoring:** Real-time insights into CPU, memory, network, and disk usage for all your virtual machines.
  * **Network Configuration:** Easily set up and manage virtual networks, bridges, and NAT.
  * **Storage Management:** Seamlessly handle virtual disks, images, and storage pools.
  * **Snapshot & Rollback:** Quickly create and restore snapshots for flexible testing and disaster recovery.
  * **Live Migration (Planned):** Future-proof with upcoming support for live migration of VMs.
  * **Open Source:** Built with the community in mind, contributing to a transparent and collaborative ecosystem.

-----

## Installation Guide

Follow these steps to get Armora Grenade up and running on your BSD system.

### Prerequisites

  * A running **BSD operating system** (FreeBSD, OpenBSD, or NetBSD recommended).
  * Minimum **4GB RAM** (8GB+ recommended).
  * Sufficient **disk space** for your virtual machines.
  * `git` installed.
  * Basic understanding of BSD command line.

### Step 1: Clone the Repository

First, clone the Armora Grenade repository from GitHub:

```bash
git clone https://github.com/Armora-Security/Grenade.git
cd Grenade
```

### Step 2: Install Dependencies

Armora Grenade relies on several packages for its functionality and GUI. The following commands will install them. *Please note: Specific package names might vary slightly between BSD distributions.*

#### For FreeBSD:

```bash
sudo pkg install libvirt-python py39-qt5 py39-psutil py39-websockets py39-flask
# Install libvirt if not already installed, ensuring it's recent enough
sudo pkg install libvirt
```

#### For OpenBSD:

```bash
doas pkg_add libvirt python%3.9-qt5 python%3.9-psutil python%3.9-websockets python%3.9-flask
```

#### For NetBSD:

```bash
sudo pkgin install libvirt py39-qt5 py39-psutil py39-websockets py39-flask
```

### Step 3: Configure Libvirt

Armora Grenade uses `libvirt` for managing virtual machines. Ensure `libvirt` is properly configured and running.

1.  **Enable and Start Libvirt Service:**

    #### For FreeBSD:

    ```bash
    echo 'libvirt_enable="YES"' | sudo tee -a /etc/rc.conf
    sudo service libvirtd start
    ```

    #### For OpenBSD:

    ```bash
    # Libvirt might be enabled by default. Check /etc/rc.conf.local or similar for details.
    # If not, you might need to add a line to enable it or start it manually:
    # doas rcctl enable libvirtd
    # doas rcctl start libvirtd
    ```

    #### For NetBSD:

    ```bash
    echo 'libvirtd=YES' | sudo tee -a /etc/rc.conf
    sudo /etc/rc.d/libvirtd start
    ```

2.  **Add Your User to the `libvirt` Group:**

    This allows your user to interact with `libvirt` without needing `sudo` for every operation within Armora Grenade.

    ```bash
    sudo pw groupadd libvirt # (If group doesn't exist)
    sudo pw groupmod libvirt -m your_username
    ```

    *Replace `your_username` with your actual username.*
    You might need to log out and log back in for the group changes to take effect.

### Step 4: Run Armora Grenade

Now you can launch Armora Grenade:

```bash
python3 main.py
```

This command will open the beautiful Armora Grenade GUI, ready for you to start managing your virtual machines\!

-----

## Contributing

We welcome contributions from the community\! If you'd like to contribute, please refer to our `CONTRIBUTING.md` file (to be created) for guidelines on how to submit bug reports, feature requests, and pull requests.

-----

## License

Armora Grenade is released under the license specified in the `LICENSE.txt` file.

