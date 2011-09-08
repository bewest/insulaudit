let SessionLoad = 1
if &cp | set nocp | endif
let s:cpo_save=&cpo
set cpo&vim
nmap gx <Plug>NetrwBrowseX
nnoremap <silent> <Plug>NetrwBrowseX :call netrw#NetrwBrowseX(expand("<cWORD>"),0)
let &cpo=s:cpo_save
unlet s:cpo_save
set autoindent
set backspace=indent,eol,start
set expandtab
set fileencodings=ucs-bom,utf-8,default,latin1
set helplang=en
set history=50
set nomodeline
set printoptions=paper:letter
set ruler
set runtimepath=~/.vim,/var/lib/vim/addons,/usr/share/vim/vimfiles,/usr/share/vim/vim72,/usr/share/vim/vimfiles/after,/var/lib/vim/addons/after,~/.vim/after,/usr/share/lilypond/2.12.3/vim/
set shiftwidth=2
set suffixes=.bak,~,.swp,.o,.info,.aux,.log,.dvi,.bbl,.blg,.brf,.cb,.ind,.idx,.ilg,.inx,.out,.toc
set tabstop=2
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/Documents/git/insulaudit
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +1 ./src/insulaudit/lib.py
badd +0 ./src/insulaudit/clmm/radio.py
badd +0 ./src/insulaudit/clmm/usbstick.py
badd +0 ./src/insulaudit/clmm/__init__.py
badd +0 ./src/insulaudit/main.py
badd +0 ./src/insulaudit/config.py
badd +0 ./src/insulaudit/console/subcommand.py
badd +0 ./src/insulaudit/console/device.py
badd +0 ./src/insulaudit/console/application.py
badd +0 ./src/insulaudit/console/utils.py
badd +0 ./src/insulaudit/console/command.py
badd +0 ./src/insulaudit/console/__init__.py
badd +0 ./src/insulaudit/log.py
badd +0 ./src/insulaudit/data/glucose.py
badd +0 ./src/insulaudit/data/__init__.py
badd +0 ./src/insulaudit/core/command.py
badd +0 ./src/insulaudit/core/loggable.py
badd +0 ./src/insulaudit/core/response.py
badd +0 ./src/insulaudit/core/session.py
badd +0 ./src/insulaudit/core/CommBuffer.py
badd +0 ./src/insulaudit/core/__init__.py
badd +0 ./src/insulaudit/core/flow.py
badd +0 ./src/insulaudit/core/link.py
badd +0 ./src/insulaudit/core/exceptions.py
badd +0 ./src/insulaudit/scan.py
badd +0 ./src/insulaudit/__init__.py
badd +0 ./src/insulaudit/devices/clmm/console.py
badd +0 ./src/insulaudit/devices/clmm/proto.py
badd +0 ./src/insulaudit/devices/clmm/__init__.py
badd +0 ./src/insulaudit/devices/lsultramini.py
badd +0 ./src/insulaudit/devices/onetouch2.py
badd +0 ./src/insulaudit/devices/__init__.py
badd +0 ./a.py
badd +0 ./docs/conf.py
badd +0 ./loop.py
badd +0 ./pseudocode.py
badd +0 ./mini.py
badd +0 ./get-pip.py
badd +0 ./onetouch.py
badd +0 ./cl2.py
badd +0 ./july.py
badd +1 docs/clmm.rst
badd +0 docs/foobar.rst
badd +0 docs/index.rst
badd +0 docs/insulaudit-intro.rst
badd +0 docs/insulaudit.rst
badd +0 docs/lifescan.rst
badd +0 docs/medtronic-intro.rst
badd +0 docs/medtronic.rst
badd +0 README
args docs/clmm.rst docs/foobar.rst docs/index.rst docs/insulaudit-intro.rst docs/insulaudit.rst docs/lifescan.rst docs/medtronic-intro.rst docs/medtronic.rst
edit README
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
edit README
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal nobinary
setlocal bufhidden=
setlocal buflisted
setlocal buftype=
setlocal nocindent
setlocal cinkeys=0{,0},0),:,0#,!^F,o,O,e
setlocal cinoptions=
setlocal cinwords=if,else,while,do,for,switch
setlocal comments=s1:/*,mb:*,ex:*/,://,b:#,:%,:XCOMM,n:>,fb:-
setlocal commentstring=/*%s*/
setlocal complete=.,w,b,u,t,i
setlocal completefunc=
setlocal nocopyindent
setlocal nocursorcolumn
setlocal nocursorline
setlocal define=
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=
setlocal expandtab
if &filetype != ''
setlocal filetype=
endif
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=0
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
setlocal foldmethod=manual
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=foldtext()
setlocal formatexpr=
setlocal formatoptions=tcq
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal grepprg=
setlocal iminsert=0
setlocal imsearch=0
setlocal include=
setlocal includeexpr=
setlocal indentexpr=
setlocal indentkeys=0{,0},:,0#,!^F,o,O,e
setlocal noinfercase
setlocal iskeyword=@,48-57,_,192-255
setlocal keywordprg=
setlocal nolinebreak
setlocal nolisp
setlocal nolist
setlocal makeprg=
setlocal matchpairs=(:),{:},[:]
setlocal nomodeline
setlocal modifiable
setlocal nrformats=octal,hex
setlocal nonumber
setlocal numberwidth=4
setlocal omnifunc=
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal shiftwidth=2
setlocal noshortname
setlocal nosmartindent
setlocal softtabstop=0
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal statusline=
setlocal suffixesadd=
setlocal swapfile
setlocal synmaxcol=3000
if &syntax != ''
setlocal syntax=
endif
setlocal tabstop=2
setlocal tags=
setlocal textwidth=0
setlocal thesaurus=
setlocal nowinfixheight
setlocal nowinfixwidth
setlocal wrap
setlocal wrapmargin=0
silent! normal! zE
let s:l = 1 - ((0 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
1
normal! 0
tabnext 1
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
