#!/bin/bash
# backup_rotate.sh
#
# Rotate backup files in a directory:
# - Keep daily backups for 7 days
# - Keep weekly backups for 4 weeks
# - Keep monthly backups for 12 months
# - Delete everything older
#
# Backup files are named with dates like: backup-2024-01-15.tar.gz
#
# Usage: backup_rotate.sh /path/to/backups

backup_rotate() {
    local backup_dir="$1"

    if [[ -z "$backup_dir" ]]; then
        echo "Usage: backup_rotate /path/to/backups" >&2
        return 1
    fi

    if [[ ! -d "$backup_dir" ]]; then
        echo "Error: directory '$backup_dir' does not exist" >&2
        return 1
    fi

    local today
    today=$(date +%s)

    local days_7=$(( 7 * 86400 ))
    local days_28=$(( 28 * 86400 ))
    local days_365=$(( 365 * 86400 ))

    local kept_weeks=()
    local kept_months=()

    for file in "$backup_dir"/backup-*.tar.gz; do
        [[ -e "$file" ]] || continue

        local basename
        basename=$(basename "$file")

        # Extract date from filename: backup-YYYY-MM-DD.tar.gz
        local date_str
        date_str=$(echo "$basename" | grep -oP '\d{4}-\d{2}-\d{2}')
        if [[ -z "$date_str" ]]; then
            continue
        fi

        local file_epoch
        file_epoch=$(date -d "$date_str" +%s 2>/dev/null) || continue

        local age=$(( today - file_epoch ))

        # Daily: keep everything within 7 days
        if (( age <= days_7 )); then
            continue
        fi

        # Weekly: keep one per ISO week for the last 4 weeks
        if (( age <= days_28 )); then
            local week_key
            week_key=$(date -d "$date_str" +%G-W%V)

            if [[ " ${kept_weeks[*]} " == *" $week_key "* ]]; then
                echo "Deleting (extra weekly): $file"
                rm "$file"
            else
                kept_weeks+=("$week_key")
            fi
            continue
        fi

        # Monthly: keep one per month for the last 12 months
        if (( age <= days_365 )); then
            local month_key
            month_key=$(date -d "$date_str" +%Y-%m)

            if [[ " ${kept_months[*]} " == *" $month_key "* ]]; then
                echo "Deleting (extra monthly): $file"
                rm "$file"
            else
                kept_months+=("$month_key")
            fi
            continue
        fi

        # Older than 12 months: delete
        echo "Deleting (older than 12 months): $file"
        rm "$file"
    done
}

# Run if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    backup_rotate "$1"
fi
