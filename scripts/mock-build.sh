#!/usr/bin/env bash
# ==============================================================================
# mock-build.sh - RPM Mock Build Automation Helper
# ==============================================================================
# Builds RPM and SRPM packages inside clean, isolated mock chroots across
# Fedora, AlmaLinux, and Rocky Linux environments.
# ==============================================================================

set -euo pipefail

# ANSI color codes
readonly COLOR_BLUE="\033[1;34m"
readonly COLOR_GREEN="\033[1;32m"
readonly COLOR_YELLOW="\033[1;33m"
readonly COLOR_RED="\033[1;31m"
readonly COLOR_RESET="\033[0m"

log_info() {
    echo -e "${COLOR_BLUE}[INFO]${COLOR_RESET} $*"
}

log_success() {
    echo -e "${COLOR_GREEN}[SUCCESS]${COLOR_RESET} $*"
}

log_warn() {
    echo -e "${COLOR_YELLOW}[WARN]${COLOR_RESET} $*"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $*" >&2
}

# Auto-detect default target based on host distribution
detect_default_target() {
    local arch
    arch="$(uname -m)"

    if [[ -f /etc/os-release ]]; then
        # shellcheck disable=SC1091
        source /etc/os-release
        case "${ID:-}" in
            fedora)
                echo "fedora-${VERSION_ID:-43}-${arch}"
                return 0
                ;;
            rocky)
                local major="${VERSION_ID%%.*}"
                echo "rocky-${major:-10}-${arch}"
                return 0
                ;;
            almalinux)
                local major="${VERSION_ID%%.*}"
                echo "almalinux-${major:-10}-${arch}"
                return 0
                ;;
        esac
    fi

    echo "fedora-43-${arch}"
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] [PACKAGE_SOURCE]

Build RPM/SRPM packages inside isolated mock environments.

Arguments:
  PACKAGE_SOURCE            Path to a .spec file or .src.rpm package

Options:
  -r, --root TARGET         Mock configuration target (default: auto-detected)
                            Examples: fedora-43-x86_64, rocky-10-x86_64,
                                      rocky+epel-10-x86_64, almalinux-10-x86_64
  -s, --sources DIR         Directory containing sources/patches (default: dirname of spec or ~/rpmbuild/SOURCES)
  -o, --resultdir DIR       Directory to store build results and logs
  --init                    Initialize the mock chroot only and exit
  --shell                   Open an interactive shell inside the mock chroot
  --clean                   Scrub/clean chroot before building
  --no-clean                Do not clean chroot after build
  --enable-network          Enable network access during package build
  --with-srpm-only          Build only the SRPM from a spec file, skip binary RPM
  -h, --help                Show this help message and exit

Examples:
  $(basename "$0") mypackage.spec
  $(basename "$0") -r rocky-10-x86_64 mypackage.src.rpm
  $(basename "$0") -r almalinux-10-x86_64 --spec SPECS/mypackage.spec --sources SOURCES
  $(basename "$0") -r fedora-43-x86_64 --init
  $(basename "$0") -r fedora-43-x86_64 --shell
EOF
}

main() {
    local target=""
    local sources_dir=""
    local result_dir=""
    local init_only=false
    local shell_only=false
    local clean_before=false
    local no_clean=false
    local enable_network=false
    local srpm_only=false
    local package_source=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -r|--root)
                target="$2"
                shift 2
                ;;
            -s|--sources)
                sources_dir="$2"
                shift 2
                ;;
            -o|--resultdir)
                result_dir="$2"
                shift 2
                ;;
            --init)
                init_only=true
                shift
                ;;
            --shell)
                shell_only=true
                shift
                ;;
            --clean)
                clean_before=true
                shift
                ;;
            --no-clean)
                no_clean=true
                shift
                ;;
            --enable-network)
                enable_network=true
                shift
                ;;
            --with-srpm-only)
                srpm_only=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                if [[ -z "$package_source" ]]; then
                    package_source="$1"
                else
                    log_error "Unexpected argument: $1"
                    usage
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Check mock executable
    if ! command -v mock >/dev/null 2>&1; then
        log_error "'mock' utility is not installed or not in PATH."
        log_info "Run: ansible-playbook rpmbuild.yml to provision the build environment."
        exit 1
    fi

    # Check mock group membership
    if ! id -nG | grep -qw "mock"; then
        log_warn "Current user '$USER' is not in the 'mock' group."
        log_warn "You may need to run 'newgrp mock' or re-login if you were recently added."
    fi

    # Resolve target
    if [[ -z "$target" ]]; then
        target="$(detect_default_target)"
        log_info "Auto-detected mock target: ${target}"
    else
        log_info "Using specified mock target: ${target}"
    fi

    # Handle --init
    if [[ "$init_only" == true ]]; then
        log_info "Initializing mock chroot for target '${target}'..."
        mock -r "${target}" --init
        log_success "Chroot initialized successfully."
        exit 0
    fi

    # Handle --shell
    if [[ "$shell_only" == true ]]; then
        log_info "Entering shell inside mock chroot '${target}'..."
        mock -r "${target}" --shell
        exit 0
    fi

    # Package source verification
    if [[ -z "$package_source" ]]; then
        log_error "No package source specified (.spec or .src.rpm)."
        usage
        exit 1
    fi

    if [[ ! -f "$package_source" ]]; then
        log_error "File not found: ${package_source}"
        exit 1
    fi

    # Base mock options
    local mock_opts=("-r" "${target}")

    if [[ "$clean_before" == true ]]; then
        mock_opts+=("--clean")
    fi

    if [[ "$no_clean" == true ]]; then
        mock_opts+=("--no-clean")
    fi

    if [[ "$enable_network" == true ]]; then
        mock_opts+=("--enable-network")
    fi

    if [[ -n "$result_dir" ]]; then
        mkdir -p "${result_dir}"
        mock_opts+=("--resultdir=${result_dir}")
    fi

    # Build execution
    case "$package_source" in
        *.spec)
            log_info "Building from RPM spec file: ${package_source}"
            if [[ -z "$sources_dir" ]]; then
                if [[ -d "$(dirname "$package_source")/../SOURCES" ]]; then
                    sources_dir="$(cd "$(dirname "$package_source")/../SOURCES" && pwd)"
                elif [[ -d "${HOME}/rpmbuild/SOURCES" ]]; then
                    sources_dir="${HOME}/rpmbuild/SOURCES"
                else
                    sources_dir="$(dirname "$package_source")"
                fi
            fi
            log_info "Using sources directory: ${sources_dir}"

            if [[ "$srpm_only" == true ]]; then
                log_info "Building SRPM only..."
                mock "${mock_opts[@]}" --buildsrpm --spec "${package_source}" --sources "${sources_dir}"
                log_success "SRPM generated successfully."
            else
                log_info "Building SRPM and binary RPMs..."
                # First build SRPM
                local tmp_result
                tmp_result="$(mktemp -d -t mock-srpm-XXXXXX)"
                mock "${mock_opts[@]}" --resultdir="${tmp_result}" --buildsrpm --spec "${package_source}" --sources "${sources_dir}"
                local built_srpm
                built_srpm="$(find "${tmp_result}" -name "*.src.rpm" | head -n 1)"
                if [[ -z "$built_srpm" || ! -f "$built_srpm" ]]; then
                    log_error "Failed to generate SRPM from spec file."
                    rm -rf "${tmp_result}"
                    exit 1
                fi
                log_info "SRPM generated: $(basename "$built_srpm"). Rebuilding binary packages..."
                mock "${mock_opts[@]}" --rebuild "${built_srpm}"
                rm -rf "${tmp_result}"
                log_success "Package build completed successfully for ${target}!"
            fi
            ;;
        *.src.rpm)
            log_info "Rebuilding from SRPM: ${package_source}"
            mock "${mock_opts[@]}" --rebuild "${package_source}"
            log_success "Rebuild completed successfully for ${target}!"
            ;;
        *)
            log_error "Unsupported package format: ${package_source}. Expected .spec or .src.rpm"
            exit 1
            ;;
    esac
}

main "$@"
