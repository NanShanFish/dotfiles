-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here
local map = vim.keymap.set
local opt = { noremap = true, silent = true }

map({ "n", "v" }, "d", '"_d', opt)
map({ "n", "v" }, "D", "d", opt)
map({ "n", "v" }, "c", '"_c', opt)
map({ "n", "v" }, "x", '"_x', opt)
map("n", "<CR>", "o<Esc>", opt)
map({ "i", "x", "n", "s" }, "<C-s>", "<cmd>w<cr><esc>", opt)
map({ "i", "x", "n", "s" }, "<C-q>", "<cmd>qa<cr><esc>", opt)
map("n", "<leader>q", "<cmd>wqa<CR>", opt)
map("n", "|", "<cmd>vsp<CR><C-w>w", opt)
map("n", "\\", "<cmd>sp<CR><C-w>w", opt)
-- map('n', '<leader>c', '<cmd>close<CR>', opt)
map("n", "<leader>t", "<cmd>below 10sp | term<CR>a", opt)
map("n", "H", "<cmd>BufferLineCyclePrev<CR>", opt)
map("n", "L", "<cmd>BufferLineCycleNext<CR>", opt)

-- -------------------------------------------------
--                TERMINAL MODE                     --
-- -------------------------------------------------
map("t", "<C-h>", "<C-\\><C-n><C-w>h", opt)
map("t", "<C-j>", "<C-\\><C-n><C-w>j", opt)
map("t", "<C-k>", "<C-\\><C-n><C-w>k", opt)
map("t", "<C-l>", "<C-\\><C-n><C-w>l", opt)
map("t", "<Esc>", "<C-\\><C-n>", opt)
