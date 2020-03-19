" show line number
set nu

" set colorscheme
colorscheme evening

"set tab=4 and show tab in .py file
set ts=4 
set sts=4
set sw=4
autocmd FileType python set list lcs=tab:\|\  

" jump to the last position when reopening a file
 if has("autocmd")
   au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
 endif

"high light a word
set hlsearch

