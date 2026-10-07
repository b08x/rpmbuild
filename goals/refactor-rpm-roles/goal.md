# Goal: Refactor RPM roles to `setup_server` and `builder`

Split the monolithic `rpm_dev` role into two distinct roles. The `setup_server` role will focus strictly on system-level prerequisites (package installation, user setup, and mock configuration), while a new `builder` role will manage the user's local `rpmbuild` environment and sync tracked `.spec` files and sources from version control to the target directories.

## Specifications
- **Facts:** See [facts.md](./facts.md) for the specific requirements and decisions.
- **Plan:** See [plan.md](./plan.md) for the ordered execution steps.

## Done Condition
This goal is complete when the `rpm_dev` role is successfully split into `setup_server` and `builder`, all variables and playbooks are updated, `.spec` and source files successfully sync to their respective `~/rpmbuild` subdirectories on the target during a playbook run, and `ansible-lint` passes without errors on the new roles.
