function __zoxide_z_complete
    set -l tokens (builtin commandline --current-process --tokenize)
    set -l curr_tokens (builtin commandline --cut-at-cursor --current-process --tokenize)

    if test (builtin count $tokens) -le 2 -a (builtin count $curr_tokens) -eq 1
        # 如果参数小于2，使用原生 cd 的补全
        complete --do-complete "'' "(builtin commandline --cut-at-cursor --current-token) | string match --regex -- '.*/$'
    else if test (builtin count $tokens) -eq (builtin count $curr_tokens)
        # 如果最后一个参数为空，触发 zoxide 交互式选择
        set -l query $tokens[2..-1]
        set -l result (command zoxide query --exclude (__zoxide_pwd) --interactive -- $query)
        and __zoxide_cd $result
        and builtin commandline --function cancel-commandline repaint
    end
end

# 移除原有 cd 补全，绑定给 zoxide 版本的 cd
complete --erase --command cd
complete --command cd --no-files --arguments '(__zoxide_z_complete)'

# 顺便把 cdi 的补全也挂上（借用 cd 的补全逻辑）
complete --erase --command cdi
complete --command cdi --no-files --arguments '(__zoxide_z_complete)'
