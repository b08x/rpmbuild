import json
import os
import re
import subprocess
from pathlib import Path

import requests
import yaml

COPR_API = "https://copr.fedorainfracloud.org/api_3"
COPR_OWNER = "b08x"
COPR_PROJECT = "syncopated"

SPEC_DIR = Path("roles/packages/files")
MANIFEST_PATH = Path("vars/package_manifest.yml")

def get_copr_packages():
    """Fetches the list of packages from COPR."""
    url = f"{COPR_API}/package/list?ownername={COPR_OWNER}&projectname={COPR_PROJECT}"
    print(f"Fetching packages from {url}")
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return {pkg['name']: pkg for pkg in data.get('items', [])}

def parse_spec_file(spec_path):
    """Parses a .spec file to extract Name, Version, Release, URL."""
    try:
        content = spec_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Failed to read {spec_path}: {e}")
        return None

    # Handle global variables often used in Version
    globals_dict = {}
    for match in re.finditer(r'^%global\s+(\w+)\s+(.+)$', content, re.MULTILINE):
        globals_dict[match.group(1)] = match.group(2).strip()

    # Try to find Version directly or evaluate macro
    version_match = re.search(r'^Version:\s+(\S+)', content, re.MULTILINE)
    version = version_match.group(1) if version_match else None

    if version and version.startswith('%{') and version.endswith('}'):
        macro = version[2:-1]
        version = globals_dict.get(macro, version)

    name_match = re.search(r'^Name:\s+(\S+)', content, re.MULTILINE)
    name = name_match.group(1) if name_match else None

    if name and name.startswith('%{'):
        macro = name[2:-1]
        name = globals_dict.get(macro, name)

    if name and name.startswith('python-%{pypi_name}'):
        if 'pypi_name' in globals_dict:
            name = f"python-{globals_dict['pypi_name']}"

    url_match = re.search(r'^URL:\s+(\S+)', content, re.MULTILINE)
    url = url_match.group(1) if url_match else None

    # Resolve %{name} macro in URL if present
    if url and '%{name}' in url and name:
        url = url.replace('%{name}', name)

    return {
        'name': name,
        'version': version,
        'url': url,
        'path': spec_path
    }

def fetch_github_latest_release(url):
    """Fetches the latest release version from a GitHub repo URL."""
    match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
    if not match:
        return None
    owner, repo = match.groups()
    # Handle possible trailing slashes or subpaths
    repo = repo.split('/')[0]

    # Use API, fallback to tags if no releases
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    tags_url = f"https://api.github.com/repos/{owner}/{repo}/tags"

    try:
        resp = requests.get(api_url, headers={"Accept": "application/vnd.github.v3+json"})
        if resp.status_code == 200:
            data = resp.json()
            version = data.get('tag_name', '').lstrip('v')
            return version
        elif resp.status_code == 404:
            # Fallback to checking tags if no formal GitHub "Release"
            resp = requests.get(tags_url, headers={"Accept": "application/vnd.github.v3+json"})
            if resp.status_code == 200:
                data = resp.json()
                # filter out non semantic versions if possible, or just skip weird ones
                for tag in data:
                    name = tag.get('name', '').lstrip('v')
                    if re.match(r'^\d', name): # Simple check for numeric start
                        return name
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching GitHub release for {owner}/{repo}: {e}")
    return None

def fetch_pypi_latest_release(name):
    """Fetches the latest release version from PyPI."""
    # PyPI names might not exactly match the spec name, strip 'python-' if present
    pypi_name = name.replace('python-', '')
    api_url = f"https://pypi.org/pypi/{pypi_name}/json"
    try:
        resp = requests.get(api_url)
        resp.raise_for_status()
        data = resp.json()
        return data.get('info', {}).get('version')
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching PyPI release for {pypi_name}: {e}")
        return None

def bump_spec(spec_path, new_version):
    """Bumps the spec file version using rpmdev-bumpspec."""
    cmd = [
        "rpmdev-bumpspec",
        "-n", new_version,
        "-c", f"Update to {new_version}",
        str(spec_path)
    ]
    print(f"  Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error bumping spec: {e.stderr}")
        return False

def main():
    if not MANIFEST_PATH.parent.exists():
        MANIFEST_PATH.parent.mkdir(parents=True)

    print("Fetching packages from COPR...")
    copr_packages = get_copr_packages()

    manifest_data = []

    print(f"Scanning for .spec files in {SPEC_DIR}...")
    for spec_path in SPEC_DIR.rglob('*.spec'):
        print(f"\nProcessing {spec_path.name}...")
        spec_info = parse_spec_file(spec_path)

        if not spec_info or not spec_info['name'] or not spec_info['version']:
            print(f"  Warning: Could not fully parse Name/Version from {spec_path.name}")
            continue

        pkg_name = spec_info['name']
        local_version = spec_info['version']
        url = spec_info['url']

        print(f"  Parsed Name: {pkg_name}, Version: {local_version}, URL: {url}")

        # Determine upstream version
        upstream_version = None

        if url and 'github.com' in url:
            print("  Fetching upstream version from GitHub...")
            upstream_version = fetch_github_latest_release(url)
        elif url and 'readthedocs.io' in url:
             # Assuming PyPI for readthedocs links that are python modules
             print("  Fetching upstream version from PyPI...")
             upstream_version = fetch_pypi_latest_release(pkg_name)
        elif pkg_name.startswith('python-'):
            print("  Fetching upstream version from PyPI (fallback based on name)...")
            upstream_version = fetch_pypi_latest_release(pkg_name)
        else:
            print("  Warning: No supported upstream source detection for this URL/package type.")

        needs_update = False
        new_version = local_version

        if upstream_version:
            print(f"  Upstream Version: {upstream_version}")
            if upstream_version != local_version:
                print(f"  New version available! ({local_version} -> {upstream_version})")
                if bump_spec(spec_info['path'], upstream_version):
                    needs_update = True
                    new_version = upstream_version
            else:
                print("  Up to date.")
        else:
            print("  Could not determine upstream version.")

        manifest_data.append({
            'name': pkg_name,
            'version': new_version,
            'needs_update': needs_update,
            'spec_path': str(spec_info['path'])
        })

    print(f"\nWriting manifest to {MANIFEST_PATH}")
    with open(MANIFEST_PATH, 'w') as f:
        yaml.dump({'packages': manifest_data}, f, default_flow_style=False)

if __name__ == "__main__":
    main()
