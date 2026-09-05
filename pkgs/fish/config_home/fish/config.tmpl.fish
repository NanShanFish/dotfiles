set -U fish_greeting ""

fish_add_path --append ~/.local/bin
fish_add_path --append ~/.cargo/bin ~/.rustup/toolchains/nightly-x86_64-unknown-linux-gnu/bin/
fish_add_path --append ~/.bun/bin

###  ENVIRONMENT VARIABLES  ###
set -Ux EDITOR /bin/nvim
set -Ux VISUAL /bin/nvim
set -Ux XDG_DOWNLOAD_DIR "@@dls_dir@@"
set -Ux XDG_DOCUMENTS_DIR "@@doc_dir@@"
set -gx LANG "zh_CN.UTF-8"

# pnpm
set -Ux PNPM_HOME "$HOME/.local/share/pnpm"
# pnpm end

true
