#!/bin/bash

#cat f - g
#      Output f's contents, then standard input, then g's contents.
#
#cat    Copy standard input to standard output.

# do k8s set
function handle_stdin() {
#    read stdin_str
    stdin_str=$(cat -)
#    stdin_str=$(cat)
    echo "do $stdin_str"
    echo '----------------------'
}

function do_some() {
#    echo abc
    cat 1.txt
    echo aaaaaaaa
    echo '22222222'
    echo '333333333'
}

function exec_python() {
    python -c 'import sys; in_str=sys.stdin.read(); print("python: " + in_str)'
    printf "tool input str\ntool input str2\n"  | python tool.py
}

function main() {
#    do_some | handle_stdin
  do_some | exec_python | handle_stdin
}

main