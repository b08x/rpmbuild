# Facts

- The existing `rpm_dev` role is renamed to `setup_server`.
- The `setup_server` role is exclusively responsible for installing system packages, setting up the user account, and configuring `mock` for local builds.
- A new Ansible role named `builder` is created.
- The `builder` role contains a `files/` subdirectory to track `.spec` files and source files in version control. (Note: the sources and .spec should go into files/<package_name>/)
- The `builder` role ensures the `~/rpmbuild/` directory tree (including `SPECS`, `SOURCES`, etc.) exists on the target server for the user.
- The `builder` role copies the tracked `.spec` files and sources from its `files/` directory into the target user's corresponding `~/rpmbuild/SPECS` and `~/rpmbuild/SOURCES` directories.
- Existing variables prefixed with `rpm_dev_` are renamed to use `setup_server_` or `builder_` prefixes as appropriate across the codebase.
- Playbooks that previously used the `rpm_dev` role (e.g., `rpmbuild.yml`) are updated to call both `setup_server` and `builder` roles sequentially.
