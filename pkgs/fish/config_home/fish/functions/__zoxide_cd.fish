function __zoxide_cd
    # 动态复制 Fish 原生的 cd 函数，防止死循环
    if ! builtin functions --query __zoxide_cd_internal
        if status list-files functions/cd.fish &>/dev/null
            status get-file functions/cd.fish | string replace --regex -- '^function cd\s' 'function __zoxide_cd_internal ' | source
        else
            string replace --regex -- '^function cd\s' 'function __zoxide_cd_internal ' <$__fish_data_dir/functions/cd.fish | source
        end
    end

    if set -q __zoxide_loop
        builtin echo "zoxide: infinite loop detected"
        return 1
    end
    __zoxide_loop=1 __zoxide_cd_internal $argv
end
