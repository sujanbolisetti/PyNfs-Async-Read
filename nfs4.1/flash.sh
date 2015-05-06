is_compact_flash ()
{
    hdparm -I $1 | sed -n '\_Commands/features:_,\_Security:_p' | \
        grep -q CFA && return 0 || return 1
}

disk=/dev/sdc1
if is_compact_flash $disk; then
    echo "$disk is a compact flash disk"
else
    echo "$disk is not a compact flash disk"
fi
