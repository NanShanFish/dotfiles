-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here
-- 缩进字符
vim.o.tabstop = 2
vim.bo.tabstop = 2
vim.o.softtabstop = 2
vim.o.shiftround = true
-- >> << 时移动长度
vim.o.shiftwidth = 2
vim.bo.shiftwidth = 2

vim.o.list = true
vim.o.listchars = "space:·"
vim.g.guifont = "maple mono nf"
-- 禁止折行
vim.wo.wrap = false
vim.o.whichwrap = "<,>,[,]"

vim.g.autoformat = false
