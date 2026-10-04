# RPMBuild & Packaging Automation

Dedicated standalone repository for provisioning RPM development workstations, configuring multi-distribution Mock build chroots, and driving reproducible RPM package builds across **Fedora**, **AlmaLinux**, and **Rocky Linux**.

---

## Repository Structure

```text
├── rpmbuild.yml                  # Root entrypoint playbook for builder provisioning
├── ansible.cfg                   # Ansible configuration (roles, inventory, callbacks)
├── inventory/                    # Self-contained host inventory & group variables
│   ├── hosts.yml                 # Target builders: gir (local), tinybot (remote), localhost
│   └── group_vars/
│       └── all.yml               # User identity SSOT and mock cache configurations
├── playbooks/
│   └── rpm_dev.yml               # RPM development & mock environment setup playbook
├── roles/
│   └── rpm_dev/                  # Standalone RPM development and mock role
│       ├── defaults/main.yml     # Role defaults with robust user & home fallbacks
│       ├── handlers/main.yml     # Handlers (e.g., mock cache scrubbing)
│       ├── meta/main.yml         # Role metadata and platform support
│       ├── tasks/                # Modular tasks (install, user, build_env, mock)
│       ├── templates/            # Custom mock configs and user .rpmmacros
│       ├── files/                # Distribution mock templates (.tpl)
│       └── vars/                 # Distribution-specific package definitions
├── scripts/
│   ├── mock-build.sh             # Workflow automation script for isolated builds
│   └── clean-cache.sh            # Mock cache & chroot cleanup utility
├── docs/
│   └── rpm_dev.json              # Architecture and execution graph artifact
├── requirements.txt              # Python & tooling requirements
├── .pre-commit-config.yaml       # Pre-commit quality hooks (prettier, ansible-lint)
└── README.md
```

---

## Features

- **Automated Toolchain Setup**: Installs complete RPM packaging tools (`rpm-build`, `rpmdevtools`, `rpmlint`, `mock`, `koji`, `createrepo_c`, `spectool`).
- **Multi-Distribution Mock Support**:
  - **Fedora**: Dynamic chroot configurations targeting active Fedora releases (Fedora 43+).
  - **Rocky Linux**: Custom configurations for Rocky Linux 10 (`rocky-10-x86_64`) and Rocky with EPEL (`rocky+epel-10-x86_64`).
  - **AlmaLinux**: Native and stock mock target integration for AlmaLinux 8, 9, and 10 with EPEL templates.
- **Robust User Environment**: Automatic creation of `~/rpmbuild` hierarchy (`BUILD`, `RPMS`, `SOURCES`, `SPECS`, `SRPMS`), `.rpmmacros` generation, and non-root mock group permissions.
- **Workflow Automation Scripts**: Pre-configured shell utilities (`scripts/mock-build.sh`, `scripts/clean-cache.sh`) to eliminate manual chroot boilerplate.

---

## Quickstart

### 1. Provision Build Environment

To provision the local workstation or remote build nodes:

```bash
# Provision local machine (default target: gir / localhost)
ansible-playbook rpmbuild.yml --limit gir --ask-become-pass

# Provision remote builder (e.g., tinybot)
ansible-playbook rpmbuild.yml --limit tinybot --ask-become-pass

# Standalone execution on localhost
ansible-playbook rpmbuild.yml --limit localhost --ask-become-pass
```

### 2. Verify Mock Permissions

Ensure your user is in the `mock` group (log out and back in, or run):

```bash
newgrp mock
```

---

## Build Automation Scripts

### Building Packages with `scripts/mock-build.sh`

The `mock-build.sh` script automates building binary and source RPMs inside clean chroots. It auto-detects the host distribution if no target is specified:

```bash
# Build from a spec file (automatically finds SOURCES and builds SRPM + RPM)
./scripts/mock-build.sh /path/to/package.spec

# Rebuild an existing SRPM
./scripts/mock-build.sh mypackage-1.0-1.el10.src.rpm

# Target a specific distribution chroot
./scripts/mock-build.sh -r rocky-10-x86_64 mypackage.spec
./scripts/mock-build.sh -r almalinux-10-x86_64 mypackage.spec
./scripts/mock-build.sh -r fedora-43-x86_64 mypackage.spec

# Initialize a chroot without building
./scripts/mock-build.sh -r rocky+epel-10-x86_64 --init

# Drop into an interactive shell inside the chroot
./scripts/mock-build.sh -r rocky-10-x86_64 --shell

# Specify custom sources directory and output destination
./scripts/mock-build.sh -s ./SOURCES -o ./output mypackage.spec
```

### Cache & Chroot Cleanup with `scripts/clean-cache.sh`

Reclaim disk space or purge contaminated caches using `clean-cache.sh`:

```bash
# Scrub all mock caches and chroots across all targets
./scripts/clean-cache.sh --all

# Clean specific target chroot
./scripts/clean-cache.sh -r fedora-43-x86_64

# Clean package manager cache only (dnf/yum)
./scripts/clean-cache.sh --dnf-cache

# Scrub mock caches and also wipe local ~/rpmbuild/BUILD workspace
./scripts/clean-cache.sh --all --rpmbuild
```

---

## Mock Configuration Targets

| Distribution | Target Root | Configuration Source |
|---|---|---|
| **Fedora** | `fedora-43-x86_64`, `fedora-43-aarch64` | `custom-fedora-branched.tpl`, `custom-fedora-43.cfg` |
| **Rocky Linux** | `rocky-10-x86_64` | `custom-rocky-10.tpl`, `rocky-10-x86_64.cfg` |
| **Rocky + EPEL** | `rocky+epel-10-x86_64` | `custom-epel-z-10.tpl`, `rocky+epel-10-x86_64.cfg` |
| **AlmaLinux** | `almalinux-10-x86_64` | Native `/etc/mock/almalinux-10-x86_64.cfg` |
| **AlmaLinux + EPEL** | `almalinux+epel-10-x86_64` | `almalinux+epel.cfg.j2` |

---

## Quality & Tooling

To run syntax and quality checks:

```bash
# Syntax check
ansible-playbook rpmbuild.yml --syntax-check

# Run ansible-lint
ansible-lint

# Run pre-commit hooks
pre-commit run --all-files
```
