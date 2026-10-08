# Packages Role

Ansible role for managing the user's local `rpmbuild` tree, macro configurations (`~/.rpmmacros`), and synchronizing tracked `.spec` files and source archives from version control.

## Overview

The `packages` role is designed to:
1. Ensure the standard RPM build hierarchy (`BUILD`, `RPMS`, `SOURCES`, `SPECS`, `SRPMS`) exists in the target user's home directory.
2. Deploy distribution-tailored `~/.rpmmacros` configurations.
3. Synchronize package spec files and source assets organized by package name in `files/` into `~/rpmbuild/SPECS/` and `~/rpmbuild/SOURCES/`.

## Directory Layout in `files/`

Each package managed by this role is structured as an isolated directory within `roles/packages/files/`:

```text
roles/packages/files/
└── <package-name>/
    ├── <package-name>.spec
    └── sources/
        ├── <source-tarball>.tar.gz
        └── <patch-or-asset>.patch
```

### Sync Rules:
- **Spec files**: Any `*.spec` file located in `<package-name>/` is copied to `{{ packages_build_dir }}/SPECS/`.
- **Source files**: All source archives, patches, and assets located inside `<package-name>/sources/` are copied to `{{ packages_build_dir }}/SOURCES/`.
- Placeholder files such as `.gitkeep` are ignored during synchronization.

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `packages_user` | `{{ setup_server_user.name \| default(ansible_user_id) }}` | Target user account owning the `rpmbuild` environment |
| `packages_create_directories` | `true` | Whether to create the standard RPM build directories |
| `packages_setup_macros` | `true` | Whether to deploy the user `.rpmmacros` template |
| `packages_home_dir` | `{{ ansible_env.HOME }}` | Home directory of the build user |
| `packages_build_dir` | `{{ packages_home_dir }}/rpmbuild` | Path to the `rpmbuild` root directory (`%_topdir`) |
| `packages_directories` | `[BUILD, RPMS, SOURCES, SPECS, SRPMS]` | RPM build subdirectories to ensure |

*Note: For backward compatibility, legacy `builder_*` variable names are supported as fallbacks.*

## Example Playbook

```yaml
- name: Configure RPM packaging environment
  hosts: builder
  become: false
  roles:
    - role: packages
      tags: ["packages"]
```

## Tags

- `packages`: Runs all tasks within the role.
- `directories`: Creates the `rpmbuild` directory tree.
- `configuration`: Deploys user `.rpmmacros`.
- `sync`: Synchronizes spec files and sources from `files/`.
