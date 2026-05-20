#!/usr/bin/env python3
"""
Virtualmin Offline Bundle Generator
"""

import re
import os
import sys
import json
import argparse
import urllib.request
from datetime import datetime
from pathlib import Path

VIRTUALMIN_DOWNLOAD_HOST = "download.virtualmin.com"
VIRTUALMIN_OLD_HOST = "software.virtualmin.com"
WEBMIN_HOST = "download.webmin.com"

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent

CORE_PACKAGES = [
    "webmin", "usermin", "virtualmin-core", "virtualmin-config",
    "webmin-virtual-server", "webmin-virtualmin-nginx", "webmin-virtualmin-nginx-ssl",
    "webmin-virtualmin-support", "webmin-virtualmin-awstats", "webmin-virtualmin-htpasswd",
    "webmin-virtualmin-registrar", "webmin-virtualmin-mailman", "webmin-virtualmin-wp-workbench",
    "virtualmin-lamp-stack", "virtualmin-lemp-stack", "virtualmin-lamp-stack-minimal",
    "virtualmin-lemp-stack-minimal", "procmail-wrapper", "jailkit"
]


def fetch_script(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None


def extract_urls_from_script(script_content):
    urls = set()

    for match in re.findall(r"https?://[^\s\"'<>()|]+", script_content):
        if match.startswith("http"):
            urls.add(match)

    host_vars = {
        "download_virtualmin_host": VIRTUALMIN_DOWNLOAD_HOST,
        "download_virtualmin_host_lib": VIRTUALMIN_DOWNLOAD_HOST,
        "download_virtualmin_host_dev": "download.virtualmin.dev",
        "download_virtualmin_host_rc": "rc.download.virtualmin.dev",
        "download_webmin_host": WEBMIN_HOST,
        "download_webmin_host_dev": "download.webmin.dev",
        "download_webmin_host_rc": "rc.download.webmin.dev",
        "download_old_virtualmin_host": VIRTUALMIN_OLD_HOST,
    }

    for var_name, host in host_vars.items():
        urls.add(f"https://{host}/slib.sh")
        urls.add(f"https://{host}/install")
        urls.add(f"https://{host}/migrate")

    for match in re.findall(r"dl\.fedoraproject\.org[^\s\"'<>]+", script_content):
        urls.add(f"https://{match}")

    return sorted(urls)


def download_file(url, dest_dir):
    filename = os.path.basename(url)
    filepath = os.path.join(dest_dir, filename)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(filepath, "wb") as f:
                f.write(response.read())
        print(f"  Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"  Failed: {filename} - {e}")
        return False


def download_all_packages(core_files, dep_files):
    packages_dir = PROJECT_ROOT / "packages"
    os.makedirs(packages_dir / "core", exist_ok=True)
    os.makedirs(packages_dir / "dependencies", exist_ok=True)

    print("
[DOWNLOAD] Core packages...")
    for f in core_files:
        download_file(f["url"], str(packages_dir / "core"))

    print("
[DOWNLOAD] Dependencies...")
    for f in dep_files:
        download_file(f["url"], str(packages_dir / "dependencies"))


def categorize_urls(urls):
    core_files = []
    dependency_files = []

    for url in urls:
        filename = os.path.basename(url)
        is_core = any(core_pkg in filename.lower() for core_pkg in CORE_PACKAGES)

        if any(host in url for host in [VIRTUALMIN_DOWNLOAD_HOST, WEBMIN_HOST, VIRTUALMIN_OLD_HOST]):
            if is_core or any(ext in filename for ext in [".rpm", ".deb", ".tar.gz", ".sh"]):
                if not any(dep in url for dep in ["slib.sh", "spinner", "log4sh", "oschooser"]):
                    core_files.append({"url": url, "filename": filename, "category": "core"})
                else:
                    dependency_files.append({"url": url, "filename": filename, "category": "dependency"})
            else:
                dependency_files.append({"url": url, "filename": filename, "category": "dependency"})
        else:
            dependency_files.append({"url": url, "filename": filename, "category": "dependency"})

    return core_files, dependency_files


def generate_modified_installer(original_script, local_repo_path="/opt/virtualmin-offline"):
    modified = original_script
    replacements = [
        ('download_virtualmin_host="download.virtualmin.com"', f'download_virtualmin_host="file://{local_repo_path}"'),
        ('download_virtualmin_host_lib="download.virtualmin.com"', f'download_virtualmin_host_lib="file://{local_repo_path}"'),
        ('download_webmin_host="download.webmin.com"', f'download_webmin_host="file://{local_repo_path}"'),
        ('download_old_virtualmin_host="software.virtualmin.com"', f'download_old_virtualmin_host="file://{local_repo_path}"'),
    ]
    for old, new in replacements:
        modified = modified.replace(old, new)

    offline_header = f"""# OFFLINE MODE - Modified for local installation
# Local repository path: {local_repo_path}
# Generated: {datetime.now().isoformat()}
VIRTUALMIN_OFFLINE_MODE=1
VIRTUALMIN_LOCAL_REPO="{local_repo_path}"

"""
    modified = modified.replace("#!/bin/sh", "#!/bin/sh\n" + offline_header)
    return modified


def generate_manifest(core_files, dep_files, script_version):
    return {
        "generated_at": datetime.now().isoformat(),
        "virtualmin_version": script_version,
        "total_files": len(core_files) + len(dep_files),
        "core_files_count": len(core_files),
        "dependency_files_count": len(dep_files),
        "core_files": core_files,
        "dependency_files": dep_files,
    }


def generate_readme(core_files, dep_files, script_version):
    readme = f"# Virtualmin Offline Installation Bundle\n\n"
    readme += f"**Version:** {script_version}\n"
    readme += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    readme += "## Core Packages\n\n"
    for f in core_files:
        readme += f"- {f['filename']}\n"
    readme += "\n## Dependencies\n\n"
    for f in dep_files:
        readme += f"- {f['filename']}\n"
    return readme


def generate_download_script(core_files, dep_files):
    script = "#!/bin/bash\n"
    script += "mkdir -p packages/core packages/dependencies\n\n"
    for f in core_files:
        script += f"wget -P packages/core \"{f['url']}\" 2>/dev/null || curl -L -o \"packages/core/{f['filename']}\" \"{f['url']}\"\n"
    for f in dep_files:
        script += f"wget -P packages/dependencies \"{f['url']}\" 2>/dev/null || curl -L -o \"packages/dependencies/{f['filename']}\" \"{f['url']}\"\n"
    return script


def main():
    parser = argparse.ArgumentParser(description="Virtualmin Offline Bundle Generator")
    parser.add_argument("--extract-only", action="store_true", help="Only extract URLs")
    parser.add_argument("--download-only", action="store_true", help="Only download packages")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "virtualmin-offline-bundle"), help="Output directory")
    args = parser.parse_args()

    print("=" * 60)
    print("Virtualmin Offline Bundle Generator")
    print("=" * 60)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Script Dir: {SCRIPT_DIR}")

    script_url = f"https://{VIRTUALMIN_DOWNLOAD_HOST}/virtualmin-install"
    print(f"\n[1/6] Downloading install script...")
    script_content = fetch_script(script_url)
    if not script_content:
        script_url = f"https://{VIRTUALMIN_OLD_HOST}/gpl/scripts/virtualmin-install.sh"
        script_content = fetch_script(script_url)
        if not script_content:
            print("ERROR: Failed to download install script")
            sys.exit(1)

    version_match = re.search(r"VER=([0-9.]+)", script_content)
    script_version = version_match.group(1) if version_match else "unknown"
    print(f"   Version: {script_version}")

    print("\n[2/6] Extracting URLs...")
    urls = extract_urls_from_script(script_content)
    print(f"   Found {len(urls)} URLs")

    # CRITICAL FIX: Write urls.txt to PROJECT ROOT
    urls_file = PROJECT_ROOT / "urls.txt"
    with open(urls_file, "w") as f:
        for url in urls:
            f.write(url + "\n")
    print(f"   Saved to: {urls_file}")

    if args.extract_only:
        print("\n[EXTRACT-ONLY] Complete!")
        return

    print("\n[3/6] Categorizing...")
    core_files, dep_files = categorize_urls(urls)
    print(f"   Core: {len(core_files)}, Dependencies: {len(dep_files)}")

    if args.download_only:
        print("\n[4/6] Downloading packages...")
        download_all_packages(core_files, dep_files)
        print("   Done!")
        return

    print("\n[4/6] Generating offline installer...")
    modified_installer = generate_modified_installer(script_content)

    print("\n[5/6] Generating documentation...")
    manifest = generate_manifest(core_files, dep_files, script_version)
    readme = generate_readme(core_files, dep_files, script_version)
    download_script = generate_download_script(core_files, dep_files)

    print("\n[6/6] Saving files...")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "virtualmin-install-original.sh", "w") as f:
        f.write(script_content)

    with open(output_dir / "virtualmin-install-offline.sh", "w") as f:
        f.write(modified_installer)
    os.chmod(output_dir / "virtualmin-install-offline.sh", 0o755)

    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    with open(output_dir / "README.md", "w") as f:
        f.write(readme)

    with open(output_dir / "download-all.sh", "w") as f:
        f.write(download_script)
    os.chmod(output_dir / "download-all.sh", 0o755)

    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Output: {output_dir.absolute()}")
    print(f"Files: {len(core_files)} core + {len(dep_files)} dependency")


if __name__ == "__main__":
    main()
