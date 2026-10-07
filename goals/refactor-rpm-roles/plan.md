# Execution Plan

## Solution Approach
Split the existing monolithic `rpm_dev` role into two specialized roles: `setup_server` for system-level configuration (packages, users, mock) and `builder` for managing the user's local RPM build environment (directories, macros, spec/source files). We will systematically rename the existing role and its variables, create the new role, port over the build environment tasks, and add tasks to synchronize version-controlled files. Finally, we'll update the playbooks.

## Ordered Steps
1. **Rename the role directory:** Move `roles/rpm_dev` to `roles/setup_server`.
2. **Update `setup_server` variables and references:** Inside `roles/setup_server`, rename all `rpm_dev_` variables to `setup_server_` (e.g., `rpm_dev_user` -> `setup_server_user`, `rpm_dev_setup_mock` -> `setup_server_setup_mock`). Update tags and README references.
3. **Remove builder tasks from `setup_server`:** Remove `build_env.yml` inclusion from `roles/setup_server/tasks/main.yml`. Delete `build_env.yml` and `templates/home/.rpmmacros.j2` from `setup_server`.
4. **Create the `builder` role:** Create `roles/builder` with standard subdirectories (`tasks`, `defaults`, `templates`, `files`).
5. **Re-implement build environment tasks in `builder`:** Add tasks to `roles/builder/tasks/main.yml` (and `build_env.yml`) to create the `~/rpmbuild/` directory tree and deploy `.rpmmacros`. Add the `builder_` prefixed variables to `defaults`.
6. **Implement file sync task in `builder`:** Add tasks to `roles/builder` that loop over packages in `files/`, copying `.spec` files to `~/rpmbuild/SPECS/` and other source files to `~/rpmbuild/SOURCES/`.
7. **Update playbooks:** Update `rpmbuild.yml` and `playbooks/rpm_dev.yml` (possibly renaming the latter to `playbooks/setup_builder.yml` to match intent) to define the new variables (`setup_server_user`, `builder_user`, etc.) and call both `setup_server` and `builder` roles.

## Verification
- Run `ansible-playbook --syntax-check rpmbuild.yml` to ensure YAML/Ansible syntax is valid.
- Run `ansible-lint` on both `roles/setup_server` and `roles/builder`.
- Execute a test run of the playbook using a test inventory or `--check` mode to ensure directories and tasks execute correctly.
- Verify `rpmbuild/SPECS/` and `rpmbuild/SOURCES/` on the target simulate receiving files.

## Risks and Unknowns
- Syncing files from `files/<package_name>/`: The file copying task needs to correctly distinguish `.spec` files from other source tarballs/patches to put them in the correct destination directories (`SPECS` vs `SOURCES`). We will use Ansible's `find` and `copy` modules carefully.
