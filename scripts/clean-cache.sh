#!/usr/bin/env bash
# ==============================================================================
# clean-cache.sh - Mock Cache & Chroot Cleanup Helper
# ==============================================================================
# Scrubs mock caches, chroots, and build trees to reclaim disk space and reset
# pristine packaging environments.
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

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Clean mock caches, build chroots, and local rpmbuild directories.

Options:
  -r, --root TARGET         Clean only the specified mock configuration target
  --all                     Scrub all mock chroots and caches (default if no type specified)
  --cache                   Scrub general mock cache
  --chroot                  Scrub chroot directory
  --root-cache              Scrub base root chroot cache
  --yum-cache, --dnf-cache  Scrub package manager metadata and rpm cache
  --ccache                  Scrub compiler cache (ccache)
  --rpmbuild                Clean ~/rpmbuild/BUILD and ~/rpmbuild/BUILDROOT directories
  -h, --help                Show this help message and exit

Examples:
  $(basename "$0")                          # Scrub all mock caches and chroots
  $(basename "$0") -r fedora-43-x86_64      # Scrub everything for fedora-43-x86_64
  $(basename "$0") --dnf-cache              # Refresh repository metadata only
  $(basename "$0") --rpmbuild               # Clean local rpmbuild workspace
EOF
}

main() {
    local target=""
    local scrub_type=""
    local clean_rpmbuild=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -r|--root)
                target="$2"
                shift 2
                ;;
            --all)
                scrub_type="all"
                shift
                ;;
            --cache)
                scrub_type="cache"
                shift
                ;;
            --chroot)
                scrub_type="chroot"
                shift
                ;;
            --root-cache)
                scrub_type="root-cache"
                shift
                ;;
            --yum-cache|--dnf-cache)
                scrub_type="yum-cache"
                shift
                ;;
            --ccache)
                scrub_type="ccache"
                shift
                ;;
            --rpmbuild)
                clean_rpmbuild=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    # Default to "all" if no specific mock scrub type requested (unless only rpmbuild clean was asked)
    if [[ -z "$scrub_type" && "$clean_rpmbuild" == false ]]; then
        scrub_type="all"
    fi

    # Check mock binary if mock scrub requested
    if [[ -n "$scrub_type" ]]; then
        if ! command -v mock >/dev/null 2>&1; then
            log_error "'mock' utility is not installed or not in PATH."
            exit 1
        fi

        local mock_cmd=("mock")
        if [[ -n "$target" ]]; then
            mock_cmd+=("-r" "${target}")
            log_info "Scrubbing '${scrub_type}' for target '${target}'..."
        else
            log_info "Scrubbing '${scrub_type}' across all mock environments..."
        fi

        mock_cmd+=("--scrub=${scrub_type}")
        "${mock_cmd[@]}"
        log_success "Mock scrub (${scrub_type}) completed."
    fi

    # Clean local rpmbuild workspace if requested
    if [[ "$clean_rpmbuild" == true ]]; then
        local rpmbuild_dir="${HOME}/rpmbuild"
        log_info "Cleaning local rpmbuild workspace at ${rpmbuild_dir}..."
        if [[ -d "${rpmbuild_dir}/BUILD" ]]; then
            rm -rf "${rpmbuild_dir}/BUILD"/*
        fi
        if [[ -d "${rpmbuild_dir}/BUILDROOT" ]]; then
            rm -rf "${rpmbuild_dir}/BUILDROOT"/*
        fi
        log_success "Local rpmbuild workspace cleaned."
    fi
}

main "$@"
