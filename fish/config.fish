set -U fish_greeting
if status --is-login; and status --is-interactive
    then
    startx
end

export EDITOR=vi

#alias vi='sudo -E -u shan vi'
alias netch='fastfetch'
alias cat='bat'
#alias nvim='sudo -E -u shan neovide'
alias nvim='neovide'
alias G='git'
