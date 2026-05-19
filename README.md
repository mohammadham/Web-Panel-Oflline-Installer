# 🔒 Offline Server Management Bundle Builder

<p align="center">
  <img src="https://img.shields.io/badge/Ubuntu-22.04%2F24.04-orange?logo=ubuntu" alt="Ubuntu">
  <img src="https://img.shields.io/badge/Virtualmin-GPL-blue?logo=linux" alt="Virtualmin">
  <img src="https://img.shields.io/badge/Webmin-2.x-green?logo=webmin" alt="Webmin">
  <img src="https://img.shields.io/badge/GitHub%20Actions-Enabled-brightgreen?logo=github" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/Offline-Ready-red" alt="Offline">
</p>

<p align="center">
  <b>Build complete offline installation packages for Virtualmin, Webmin, and Cockpit</b><br>
  <i>No internet required on target server — perfect for air-gapped environments</i>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Supported Bundles](#-supported-bundles)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Bundle Types Explained](#-bundle-types-explained)
- [Installation on Offline Server](#-installation-on-offline-server)
- [Repository Structure](#-repository-structure)
- [GitHub Actions Workflow](#-github-actions-workflow)
- [Troubleshooting](#-troubleshooting)
- [Security Notes](#-security-notes)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

This project provides an automated **GitHub Actions workflow** that downloads all necessary packages for installing server management panels (Virtualmin, Webmin, Cockpit) along with their complete dependencies, and packages them into a single archive suitable for offline/air-gapped server installations.

### Why This Project?

| Challenge | Solution |
|-----------|----------|
| 🔒 Air-gapped servers with no internet | ✅ Complete offline package bundles |
| 📦 Missing dependencies during install | ✅ All dependencies pre-downloaded |
| ⏱️ Manual package collection is tedious | ✅ Fully automated via GitHub Actions |
| 🔄 Version consistency across servers | ✅ Tagged releases with version control |
| 📝 Complex installation procedures | ✅ One-command automated installer |

---

## ✨ Features

### Core Features
- 🚀 **Fully Automated** — One click to build complete offline bundles
- 📦 **Complete Dependencies** — All packages and sub-dependencies included
- 🔄 **GPG Fallback System** — 3-level fallback for repository key issues
- 🏗️ **Multiple Stack Support** — LAMP (Apache) and LEMP (Nginx) variants
- 📋 **Smart Installer Script** — Color-coded, phased installation with error handling
- 🔐 **Auto-Generated Credentials** — Secure passwords saved automatically
- 📖 **Comprehensive Documentation** — README, INSTALL guide, package manifest
- 🏷️ **Automatic GitHub Releases** — Tagged releases with SHA256 checksums
- 🎨 **Colored Terminal Output** — Easy-to-read installation progress
- 🛡️ **Security Hardening** — MariaDB secured, services enabled automatically

### Supported Platforms
| OS | Version | Architecture | Status |
|----|---------|-------------|--------|
| Ubuntu | 22.04 LTS (Jammy) | amd64 | ✅ Fully Supported |
| Ubuntu | 24.04 LTS (Noble) | amd64 | ✅ Fully Supported |

---

## 📦 Supported Bundles

| Bundle Type | Web Server | Database | Mail | DNS | FTP | Security | Size |
|-------------|-----------|----------|------|-----|-----|----------|------|
| `webmin-only` | — | — | — | — | — | Basic | ~50-100MB |
| `virtualmin-mini-lamp` | Apache2 | MariaDB | — | — | — | Basic | ~200-300MB |
| `virtualmin-mini-lemp` | Nginx | MariaDB | — | — | — | Basic | ~200-300MB |
| `virtualmin-full-lamp` | Apache2 | MariaDB | ✅ | ✅ | ✅ | ✅ | ~800MB-1.2GB |
| `virtualmin-full-lemp` | Nginx | MariaDB | ✅ | ✅ | ✅ | ✅ | ~700MB-1GB |
| `cockpit-web` | Apache2+Nginx | MariaDB | — | — | — | Basic | ~300-500MB |

### Bundle Comparison

```
webmin-only          → Just the Webmin control panel
virtualmin-mini-*    → Panel + Web Server + Database (development/small sites)
virtualmin-full-*    → Complete hosting platform (production servers)
cockpit-web          → Modern server management + web stack
```

---

## 🚀 Quick Start

### Step 1: Fork or Use This Repository

```bash
# Clone this repository
git clone https://github.com/YOUR_USERNAME/offline-server-bundle.git
cd offline-server-bundle
```

### Step 2: Run GitHub Actions Workflow

1. Go to **Actions** tab in your GitHub repository
2. Select **"Build Offline Virtualmin Bundle"** workflow
3. Click **"Run workflow"** button
4. Configure parameters:
   - **Ubuntu Version**: `jammy` (22.04) or `noble` (24.04)
   - **Bundle Type**: Choose from supported bundles
   - **Release Version** (optional): e.g., `v1.0.0` or leave empty for auto-tag
5. Click **"Run workflow"**

### Step 3: Download the Bundle

After workflow completes:

**Option A — From GitHub Release (Recommended)**
- Navigate to **Releases** tab
- Download the `.tar.gz` archive
- Also download `.sha256` file for verification

**Option B — From Workflow Artifacts**
- Go to the completed workflow run
- Download artifacts from the bottom of the page

### Step 4: Install on Offline Server

```bash
# On your offline server:
# 1. Transfer the archive (USB, SCP, etc.)
tar -xzf offline-virtualmin-full-lamp-jammy-*.tar.gz
cd offline-bundle/scripts
sudo ./install.sh
```

---

## 📖 Usage Guide

### Building a Bundle

#### Via GitHub Web Interface

1. Navigate to **Actions** → **Build Offline Virtualmin Bundle**
2. Click **"Run workflow"** (dropdown on right side)
3. Fill parameters:

| Parameter | Options | Description |
|-----------|---------|-------------|
| `ubuntu_version` | `jammy`, `noble` | Target Ubuntu LTS version |
| `bundle_type` | See [Supported Bundles](#-supported-bundles) | Type of package bundle |
| `release_version` | Any string (e.g., `v1.0.0`) | Optional manual version tag |

4. Workflow runs automatically (5-15 minutes)
5. Find output in **Releases** section

#### Via GitHub CLI

```bash
# Trigger workflow with parameters
gh workflow run "Build Offline Virtualmin Bundle" \
  -f ubuntu_version=jammy \
  -f bundle_type=virtualmin-full-lamp \
  -f release_version=v1.0.0

# Watch progress
gh run watch

# Download latest artifact
gh run download $(gh run list --workflow="Build Offline Virtualmin Bundle" -L1 --json databaseId -q '.[0].databaseId')
```

### Verifying Download Integrity

```bash
# Verify SHA256 checksum
sha256sum -c offline-virtualmin-full-lamp-jammy-*.tar.gz.sha256

# Expected output:
# offline-virtualmin-full-lamp-jammy-20240519.tar.gz: OK
```

---

## 🔧 Bundle Types Explained

### `webmin-only`
**Use case**: Simple server management without hosting features

**Includes**:
- Webmin control panel (port 10000)
- All Webmin dependencies
- Basic system management tools

**Best for**: Single server management, no hosting needed

---

### `virtualmin-mini-lamp`
**Use case**: Lightweight web development environment

**Includes**:
- Webmin + Usermin panels
- Apache2 web server
- MariaDB database
- PHP (with common extensions)
- Certbot for SSL

**Best for**: Development servers, small websites, learning environments

---

### `virtualmin-mini-lemp`
**Use case**: Lightweight web development with Nginx

**Includes**:
- Webmin + Usermin panels
- Nginx web server + PHP-FPM
- MariaDB database
- Certbot for SSL

**Best for**: High-performance small sites, Nginx enthusiasts

---

### `virtualmin-full-lamp`
**Use case**: Complete web hosting platform (Apache-based)

**Includes**:
- Webmin + Usermin panels
- Apache2 + mod_php + mod_fcgid
- MariaDB with full configuration
- Postfix + Dovecot mail server
- BIND9 DNS server
- ProFTPd FTP server
- ClamAV antivirus
- SpamAssassin spam filter
- Fail2Ban intrusion prevention
- Certbot (Apache plugin)

**Best for**: Production hosting servers, shared hosting, cPanel alternative

---

### `virtualmin-full-lemp`
**Use case**: Complete web hosting platform (Nginx-based)

**Includes**:
- Webmin + Usermin panels
- Nginx + PHP-FPM
- MariaDB with full configuration
- Postfix + Dovecot mail server
- BIND9 DNS server
- ProFTPd FTP server
- ClamAV antivirus
- SpamAssassin spam filter
- Fail2Ban intrusion prevention
- Certbot (Nginx plugin)
- Optimized Nginx PHP-FPM configuration

**Best for**: High-traffic production sites, WordPress hosting, modern web apps

---

### `cockpit-web`
**Use case**: Modern server management with flexible web stack

**Includes**:
- Cockpit server management (port 9090)
- Both Apache2 and Nginx
- MariaDB database
- PHP support
- Podman container management

**Best for**: Modern Linux administration, container workloads, mixed environments

---

## 🔌 Installation on Offline Server

### Prerequisites

- Ubuntu 22.04 LTS or 24.04 LTS (clean install recommended)
- Root access (sudo)
- Minimum requirements:
  | Bundle Type | RAM | Disk Space |
  |-------------|-----|-----------|
  | webmin-only | 1GB | 5GB |
  | virtualmin-mini-* | 2GB | 10GB |
  | virtualmin-full-* | 4GB | 20GB |
  | cockpit-web | 2GB | 10GB |

### Method 1: Automated Script (Recommended)

```bash
# Extract the bundle
tar -xzf offline-virtualmin-full-lamp-jammy-*.tar.gz

# Navigate to scripts
cd offline-bundle/scripts

# Run installer
sudo ./install.sh
```

**What the script does**:
1. ✅ Validates root privileges
2. ✅ Checks package integrity
3. ✅ Installs packages in correct order (5 phases)
4. ✅ Fixes broken dependencies automatically
5. ✅ Configures services (MariaDB, Postfix, etc.)
6. ✅ Generates secure passwords
7. ✅ Enables and starts all services
8. ✅ Displays access URLs and credentials

### Method 2: Local APT Repository

```bash
# Add the local repository
cd offline-bundle/scripts
sudo ./add-repo.sh

# Now you can use apt normally (offline)
sudo apt-get update
sudo apt-get install webmin
```

### Method 3: Manual Installation

```bash
cd offline-bundle/packages

# Install all packages
sudo dpkg -i *.deb

# Fix any dependency issues
sudo apt-get install -f -y

# Reconfigure if needed
sudo dpkg --configure -a
```

### Post-Installation

After installation completes:

```bash
# Check credentials
cat /root/.virtualmin-credentials

# Check services status
sudo systemctl status apache2 mariadb webmin

# Access Webmin
# https://YOUR-SERVER-IP:10000

# Access Usermin (if installed)
# https://YOUR-SERVER-IP:20000
```

---

## 📁 Repository Structure

```
offline-server-bundle/
├── .github/
│   └── workflows/
│       └── build-offline-bundle.yml    # Main GitHub Actions workflow
├── docs/
│   ├── ARCHITECTURE.md                 # Technical architecture details
│   ├── BUNDLE_TYPES.md                 # Detailed bundle comparison
│   └── CONTRIBUTING.md                 # Contribution guidelines
├── scripts/
│   ├── local-build.sh                  # Local build script (optional)
│   └── verify-offline.sh              # Verify offline server readiness
├── .gitignore
├── LICENSE
└── README.md                           # This file
```

### Workflow File Location

```
.github/workflows/build-offline-bundle.yml
```

---

## ⚙️ GitHub Actions Workflow

### Workflow Triggers

| Trigger | Description |
|---------|-------------|
| `workflow_dispatch` | Manual trigger with parameters |
| Auto-release | Creates GitHub Release with tag |

### Workflow Steps

```
1. Setup Environment
   └── Install build tools (wget, curl, gnupg, dpkg-dev)

2. Setup Repositories (3-Fallback)
   ├── Method 1: Virtualmin 7 GPG key
   ├── Method 2: Virtualmin 6 GPG key
   ├── Method 3: Webmin developers key
   └── Fallback: No GPG verification

3. Download Packages
   ├── Core panel packages
   ├── Web server (Apache/Nginx)
   ├── Database (MariaDB)
   ├── PHP and extensions
   ├── Mail services (Postfix, Dovecot)
   ├── DNS (BIND9)
   ├── FTP (ProFTPd)
   └── Security tools

4. Create Installer Script
   └── Smart phased installation with error handling

5. Generate Documentation
   ├── README.md (bundle-specific)
   ├── docs/INSTALL.md
   └── docs/PACKAGE_MANIFEST.txt

6. Create Local APT Repository
   └── dpkg-scanpackages + Release file

7. Verify Bundle
   └── Package count, size, integrity check

8. Create Archive
   └── tar.gz + SHA256 checksum + info file

9. Upload Artifact
   └── GitHub Actions artifact (30-day retention)

10. Create GitHub Release
    └── Tagged release with all files attached
```

### GPG Fallback System

```
Attempt 1: Download Virtualmin 7 key → signed-by repository
    ↓ (if fails)
Attempt 2: Download Virtualmin 6 key → signed-by repository
    ↓ (if fails)
Attempt 3: Download Webmin key → Webmin signed + Virtualmin trusted
    ↓ (if fails)
Fallback: No GPG verification → trusted=yes repository
```

---

## 🛠️ Troubleshooting

### Build Failures

#### Issue: "gpg: no valid OpenPGP data found"
**Solution**: The workflow automatically falls back to trusted repository. Check build logs to see which method succeeded.

#### Issue: "Package not found" during download
**Solution**: Some packages may not exist in the repository. The workflow uses `|| true` to continue. Check the final package count in the verification step.

#### Issue: Workflow timeout
**Solution**: Full bundles take 10-15 minutes. If timeout occurs, use `virtualmin-mini-*` bundles instead.

### Installation Failures

#### Issue: "dpkg: dependency problems"
**Solution**: Run the fix command:
```bash
sudo apt-get install -f -y
sudo dpkg --configure -a
```

#### Issue: Services fail to start
**Solution**: Check service status and logs:
```bash
sudo systemctl status apache2
sudo journalctl -xe
```

#### Issue: Cannot access Webmin
**Solution**: Check firewall and service:
```bash
sudo systemctl status webmin
sudo ufw allow 10000/tcp
sudo netstat -tlnp | grep 10000
```

### Common Fixes

```bash
# Re-run configuration
sudo dpkg --configure -a

# Fix all broken packages
sudo apt-get install -f -y

# Restart all services
sudo systemctl restart apache2 nginx mariadb webmin

# Check installation log
cat /var/log/offline-install.log
```

---

## 🔒 Security Notes

### Auto-Generated Credentials

The installer automatically:
- Generates strong random passwords for MariaDB
- Saves credentials to `/root/.virtualmin-credentials`
- Sets file permissions to `600` (owner read-only)

**Important**: Change default passwords after first login!

```bash
# Change MySQL root password
sudo mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY 'your-new-password';
FLUSH PRIVILEGES;
EXIT;
```

### SSL Certificates

- Self-signed certificates are generated automatically
- For production, replace with proper certificates:
  ```bash
  # If you have internet access later
  sudo certbot --apache  # or --nginx
  ```

### Firewall Configuration

```bash
# Allow necessary ports
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw allow 10000/tcp  # Webmin
sudo ufw allow 20000/tcp  # Usermin
sudo ufw allow 9090/tcp   # Cockpit (if installed)
sudo ufw enable
```

### Fail2Ban

Installed and enabled by default on full bundles:
```bash
# Check status
sudo fail2ban-client status

# View banned IPs
sudo fail2ban-client status sshd
```

---

## 🤝 Contributing

We welcome contributions! Please see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- 🐛 Report bugs via GitHub Issues
- 💡 Suggest new features or bundle types
- 📝 Improve documentation
- 🔧 Submit pull requests

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/offline-server-bundle.git
cd offline-server-bundle

# Create branch
git checkout -b feature/your-feature

# Make changes and test
# ...

# Commit and push
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

### Third-Party Components

- **Virtualmin**: GPL License — [virtualmin.com](https://www.virtualmin.com)
- **Webmin**: BSD License — [webmin.com](https://www.webmin.com)
- **Cockpit**: LGPL License — [cockpit-project.org](https://cockpit-project.org)

---

## 🙏 Acknowledgments

- [Virtualmin](https://www.virtualmin.com) team for the excellent hosting control panel
- [Webmin](https://www.webmin.com) developers for the system management tools
- [GitHub Actions](https://github.com/features/actions) for the automation platform
- Ubuntu community for the LTS releases

---

## 📞 Support

| Resource | Link |
|----------|------|
| 📖 Documentation | This README + docs/ folder |
| 🐛 Issues | [GitHub Issues](../../issues) |
| 💬 Discussions | [GitHub Discussions](../../discussions) |
| 📧 Virtualmin | [forums.virtualmin.com](https://forums.virtualmin.com) |
| 📧 Webmin | [github.com/webmin/webmin](https://github.com/webmin/webmin) |

---

<p align="center">
  <b>Built with ❤️ for the offline server community</b><br>
  <i>Star ⭐ this repository if you find it useful!</i>
</p>
