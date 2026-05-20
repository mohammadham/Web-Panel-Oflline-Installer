#!/usr/bin/env python3
"""
Virtualmin Offline Bundle Generator
Extracts the install script, finds all download URLs, categorizes packages,
and creates an offline-ready modified installer.

Usage:
    python3 virtualmin_offline_generator.py              # Full generation
    python3 virtualmin_offline_generator.py --extract-only  # Only extract URLs
    python3 virtualmin_offline_generator.py --download-only # Only download packages
"""

import re
import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# Configuration
VIRTUALMIN_DOWNLOAD_HOST = "download.virtualmin.com"
VIRTUALMIN_OLD_HOST = "software.virtualmin.com"
WEBMIN_HOST = "download.webmin.com"

# Known package categories
CORE_PACKAGES = [
    "webmin", "usermin", "virtualmin-core", "virtualmin-config",
    "webmin-virtual-server", "webmin-virtualmin-nginx", "webmin-virtualmin-nginx-ssl",
    "webmin-virtualmin-support", "webmin-virtualmin-awstats", "webmin-virtualmin-htpasswd",
    "webmin-virtualmin-registrar", "webmin-virtualmin-mailman", "webmin-virtualmin-wp-workbench",
    "virtualmin-lamp-stack", "virtualmin-lemp-stack", "virtualmin-lamp-stack-minimal",
    "virtualmin-lemp-stack-minimal", "procmail-wrapper", "jailkit"
]

DEPENDENCY_URLS = [
    "dl.fedoraproject.org",  # EPEL
    "software.virtualmin.com/lib",  # slib.sh, spinner, log4sh, etc.
    "download.virtualmin.com/slib.sh",
    "download.webmin.com",
]


def fetch_script(url):
    """Download the install script."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None


def extract_urls_from_script(script_content):
    """Extract all URLs from the install script."""
    urls = set()

    # Pattern 1: Direct URL strings in the script
    url_patterns = [
        r'https?://[^\s\'"<>]+',
        r'\$download\s+"([^"]+)"',
        r'\$download\s+\'([^\']+)\'',
        r'curl\s+-[^\s]*\s+"([^"]+)"',
        r'wget\s+[^\s]*\s+"([^"]+)"',
        r'wget\s+[^\s]*\s+\'([^\']+)\'',
    ]

    for pattern in url_patterns:
        matches = re.findall(pattern, script_content)
        for match in matches:
            if match.startswith('http'):
                urls.add(match)

    # Pattern 2: Variable-based URLs
    host_vars = {
        'download_virtualmin_host': VIRTUALMIN_DOWNLOAD_HOST,
        'download_virtualmin_host_lib': VIRTUALMIN_DOWNLOAD_HOST,
        'download_virtualmin_host_dev': 'download.virtualmin.dev',
        'download_virtualmin_host_rc': 'rc.download.virtualmin.dev',
        'download_webmin_host': WEBMIN_HOST,
        'download_webmin_host_dev': 'download.webmin.dev',
        'download_webmin_host_rc': 'rc.download.webmin.dev',
        'download_old_virtualmin_host': VIRTUALMIN_OLD_HOST,
    }

    # Find URL constructions like https://$download_virtualmin_host/slib.sh
    for var_name, host in host_vars.items():
        # slib.sh
        urls.add(f"https://{host}/slib.sh")
        # install script for repo setup
        urls.add(f"https://{host}/install")
        # migrate script
        urls.add(f"https://{host}/migrate")

    # EPEL downloads
    epel_pattern = r'dl\.fedoraproject\.org[^\s\'"<>]+'
    epel_matches = re.findall(epel_pattern, script_content)
    for match in epel_matches:
        urls.add(f"https://{match}")

    return sorted(urls)


def categorize_urls(urls):
    """Categorize URLs into core and dependencies."""
    core_files = []
    dependency_files = []

    for url in urls:
        filename = os.path.basename(url)

        # Check if it's a core Virtualmin/Webmin package
        is_core = False
        for core_pkg in CORE_PACKAGES:
            if core_pkg in filename.lower():
                is_core = True
                break

        # Check if it's from Virtualmin/Webmin download hosts
        if any(host in url for host in [VIRTUALMIN_DOWNLOAD_HOST, WEBMIN_HOST, VIRTUALMIN_OLD_HOST]):
            if is_core or any(ext in filename for ext in ['.rpm', '.deb', '.tar.gz', '.sh']):
                if not any(dep in url for dep in ['slib.sh', 'spinner', 'log4sh', 'oschooser']):
                    core_files.append({
                        'url': url,
                        'filename': filename,
                        'category': 'core'
                    })
                else:
                    dependency_files.append({
                        'url': url,
                        'filename': filename,
                        'category': 'dependency'
                    })
            else:
                dependency_files.append({
                    'url': url,
                    'filename': filename,
                    'category': 'dependency'
                })
        else:
            dependency_files.append({
                'url': url,
                'filename': filename,
                'category': 'dependency'
            })

    return core_files, dependency_files


def download_file(url, dest_dir):
    """Download a single file."""
    filename = os.path.basename(url)
    filepath = os.path.join(dest_dir, filename)

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
        print(f"  ✓ Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {filename} - {e}")
        return False


def download_all_packages(core_files, dep_files):
    """Download all packages to local directories."""
    os.makedirs('packages/core', exist_ok=True)
    os.makedirs('packages/dependencies', exist_ok=True)

    print("\n[DOWNLOAD] Core packages...")
    for f in core_files:
        download_file(f['url'], 'packages/core')

    print("\n[DOWNLOAD] Dependencies...")
    for f in dep_files:
        download_file(f['url'], 'packages/dependencies')

    # Also download from directory listings
    print("\n[DOWNLOAD] Scanning download.virtualmin.com directory...")
    try:
        req = urllib.request.Request(f"https://{VIRTUALMIN_DOWNLOAD_HOST}/", 
                                       headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            # Find all package files
            files = re.findall(r'href="([^"]+\.(?:rpm|deb|tar\.gz|sh))"', html)
            for file in files:
                url = f"https://{VIRTUALMIN_DOWNLOAD_HOST}/{file}"
                download_file(url, 'packages/core')
    except Exception as e:
        print(f"  Warning: Could not scan directory: {e}")

    print("\n[DOWNLOAD] Scanning download.webmin.com directory...")
    try:
        req = urllib.request.Request(f"https://{WEBMIN_HOST}/", 
                                       headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            files = re.findall(r'href="([^"]+\.(?:rpm|deb|tar\.gz))"', html)
            for file in files:
                url = f"https://{WEBMIN_HOST}/{file}"
                download_file(url, 'packages/core')
    except Exception as e:
        print(f"  Warning: Could not scan directory: {e}")


def generate_modified_installer(original_script, local_repo_path="/opt/virtualmin-offline"):
    """Generate a modified install script that uses local files."""
    modified = original_script

    # Replace download hosts with local paths
    replacements = [
        ('download_virtualmin_host="download.virtualmin.com"', 
         f'download_virtualmin_host="file://{local_repo_path}"'),
        ('download_virtualmin_host_lib="download.virtualmin.com"',
         f'download_virtualmin_host_lib="file://{local_repo_path}"'),
        ('download_webmin_host="download.webmin.com"',
         f'download_webmin_host="file://{local_repo_path}"'),
        ('download_old_virtualmin_host="software.virtualmin.com"',
         f'download_old_virtualmin_host="file://{local_repo_path}"'),
    ]

    for old, new in replacements:
        modified = modified.replace(old, new)

    # Add offline mode flag at the top
    offline_header = f
