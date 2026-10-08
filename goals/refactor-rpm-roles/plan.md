# Execution Plan

## Solution Approach
Split the existing monolithic `rpm_dev` role into two specialized roles: `setup_server` for system-level configuration (packages, users, mock) and `packages` (previously `builder`) for managing the user's local RPM build environment (directories, macros, spec/source files). We will systematically rename the existing role and its variables, create the new role, port over the build environment tasks, and add tasks to synchronize version-controlled files. Finally, we'll update the playbooks.

## Ordered Steps
1. **Rename the role directory:** Move `roles/rpm_dev` to `roles/setup_server`.
2. **Update `setup_server` variables and references:** Inside `roles/setup_server`, rename all `rpm_dev_` variables to `setup_server_` (e.g., `rpm_dev_user` -> `setup_server_user`, `rpm_dev_setup_mock` -> `setup_server_setup_mock`). Update tags and README references.
3. **Remove builder tasks from `setup_server`:** Remove `build_env.yml` inclusion from `roles/setup_server/tasks/main.yml`. Delete `build_env.yml` and `templates/home/.rpmmacros.j2` from `setup_server`.
4. **Create the `packages` role:** Create `roles/packages` with standard subdirectories (`tasks`, `defaults`, `templates`, `files`).
5. **Re-implement build environment tasks in `packages`:** Add tasks to `roles/packages/tasks/main.yml` (and `build_env.yml`) to create the `~/rpmbuild/` directory tree and deploy `.rpmmacros`. Add the `packages_` prefixed variables to `defaults`.
6. **Implement file sync task in `packages`:** Add tasks to `roles/packages` that loop over packages in `files/`, copying `<pkg>/*.spec` files to `~/rpmbuild/SPECS/` and `<pkg>/sources/*` to `~/rpmbuild/SOURCES/`.
7. **Update playbooks:** Update `rpmbuild.yml` and `playbooks/setup_builder.yml` to define the new variables (`setup_server_user`, `packages_user`, etc.) and call both `setup_server` and `packages` roles.

## Verification
- Run `ansible-playbook --syntax-check rpmbuild.yml` to ensure YAML/Ansible syntax is valid.
- Run `ansible-lint` on both `roles/setup_server` and `roles/packages`.
- Execute a test run of the playbook using a test inventory or `--check` mode to ensure directories and tasks execute correctly.
- Verify `rpmbuild/SPECS/` and `rpmbuild/SOURCES/` on the target simulate receiving files.

## Risks and Unknowns
- Syncing files from `files/<package_name>/`: The file copying task distinguishes `.spec` files from source files inside `sources/` to place them into the correct destination directories (`SPECS` vs `SOURCES`).

