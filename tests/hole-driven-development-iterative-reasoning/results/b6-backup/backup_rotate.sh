#!/bin/bash
# backup_rotate.sh
#
# Rotate backup files in a directory:
# - Keep daily backups for 7 days
# - Keep weekly backups for 4 weeks
# - Keep monthly backups for 12 months
# - Delete everything older
#
# Assumes backup files are named with dates: backup-YYYY-MM-DD.tar.gz
#
# Usage: backup_rotate.sh /path/to/backups

backup_rotate() {
    local backup_dir="$1"

    # HOLE_1: Validate input [FILLED]
    if [[ -z "$backup_dir" ]]; then
        echo "Usage: backup_rotate.sh /path/to/backups" >&2
        return 1
    fi
    if [[ ! -d "$backup_dir" ]]; then
        echo "Error: '$backup_dir' is not a directory" >&2
        return 1
    fi

    # HOLE_2: List backup files [FILLED]
    local backup_files=()
    for f in "$backup_dir"/backup-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].tar.gz; do
        [[ -f "$f" ]] && backup_files+=("$(basename "$f")")
    done
    if [[ ${#backup_files[@]} -eq 0 ]]; then
        echo "No backup files found in '$backup_dir'"
        return 0
    fi

    # HOLE_3: Compute age boundaries [FILLED]
    local now_epoch
    now_epoch=$(date +%s)
    local cutoff_daily=$(( now_epoch - 7 * 86400 ))       # 7 days ago
    local cutoff_weekly=$(( now_epoch - 28 * 86400 ))     # 4 weeks ago
    local cutoff_monthly=$(( now_epoch - 365 * 86400 ))   # 12 months ago (approx)

    # HOLE_4: Classify and select keepers [FILLED]
    declare -A keep_files
    declare -A seen_weeks
    declare -A seen_months

    # Sort reverse-chronologically so newest file per bucket wins
    local sorted_files
    sorted_files=$(printf '%s\n' "${backup_files[@]}" | sort -r)

    while IFS= read -r fname; do
        # Extract date from filename: backup-YYYY-MM-DD.tar.gz
        local file_date="${fname#backup-}"
        file_date="${file_date%.tar.gz}"
        local file_epoch
        file_epoch=$(date -d "$file_date" +%s 2>/dev/null) || continue

        if (( file_epoch >= cutoff_daily )); then
            # Daily window: keep all
            keep_files["$fname"]=daily
        elif (( file_epoch >= cutoff_weekly )); then
            # Weekly window: keep one per ISO week
            local week_key
            week_key=$(date -d "$file_date" +%G-%V)
            if [[ -z "${seen_weeks[$week_key]+x}" ]]; then
                seen_weeks["$week_key"]=1
                keep_files["$fname"]=weekly
            fi
        elif (( file_epoch >= cutoff_monthly )); then
            # Monthly window: keep one per month
            local month_key="${file_date:0:7}"  # YYYY-MM
            if [[ -z "${seen_months[$month_key]+x}" ]]; then
                seen_months["$month_key"]=1
                keep_files["$fname"]=monthly
            fi
        fi
        # else: older than 12 months, not kept
    done <<< "$sorted_files"

    # HOLE_5: Delete non-kept files [FILLED]
    local deleted=0 kept=0
    for fname in "${backup_files[@]}"; do
        if [[ -n "${keep_files[$fname]+x}" ]]; then
            echo "  KEEP [${keep_files[$fname]}] $fname"
            (( kept++ ))
        else
            rm "$backup_dir/$fname"
            echo "  DELETE $fname"
            (( deleted++ ))
        fi
    done
    echo "Done: kept $kept, deleted $deleted (of ${#backup_files[@]} total)"
}

backup_rotate "$1"
