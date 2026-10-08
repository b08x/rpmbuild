# Facts

- The existing `rpm_dev` role is renamed to `setup_server`.
- The `setup_server` role is exclusively responsible for installing system packages, setting up the user account, and configuring `mock` for local builds.
- A new Ansible role named `packages` (previously `builder`) is created.
- The `packages` role contains a `files/` subdirectory to track `.spec` files and source files in version control. (Note: the sources and .spec go into files/<package_name>/, with sources located in <package_name>/sources/)
- The `packages` role ensures the `~/rpmbuild/` directory tree (including `SPECS`, `SOURCES`, etc.) exists on the target server for the user.
- The `packages` role copies the tracked `.spec` files and sources from its `files/` directory into the target user's corresponding `~/rpmbuild/SPECS` and `~/rpmbuild/SOURCES` directories.
- Existing variables prefixed with `rpm_dev_` or `builder_` are renamed to use `setup_server_` or `packages_` prefixes as appropriate across the codebase.
- Playbooks that previously used the `rpm_dev` role (e.g., `rpmbuild.yml`) are updated to call both `setup_server` and `packages` roles sequentially.

