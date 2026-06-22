function bwp --description 'Get Bitwarden password by item name, with cache and auto unlock'
    argparse 'n/new' -- $argv
    or return 1

    set -l force_new
    if set -q _flag_new
        set force_new 1
    end

    set -l item_name $argv[1]

    if test -z "$item_name"; and not set -q _flag_new
        set force_new 1
    end

    if bw status 2>/dev/null | grep -q '"locked"'
        set -gx BW_SESSION (bw unlock --raw)
        or begin
            echo "Unlock failed." >&2
            return 1
        end
    end

    set -l cache_file /tmp/bw_cache

    if set -q force_new; or not test -f $cache_file
        bw list items | jq -r '.[].name' >$cache_file
        or begin
            echo "Failed to generate cache. Is the vault unlocked?" >&2
            return 1
        end
    end

    if set -q _flag_new; and test -z "$item_name"
        return 0
    end

    if test -z "$item_name"
        if not command -v fzf >/dev/null
            echo "Error: fzf is not installed. Install fzf to use interactive selection." >&2
            return 1
        end
        set item_name (cat $cache_file | fzf --prompt="Select item: ")
        or return 1   # 用户取消选择
    end

    bw get password "$item_name" 2>/dev/null
    or echo "Item '$item_name' not found or error occurred." >&2
end
