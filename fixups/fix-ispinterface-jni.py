#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
#
# libcamera_ispinterface_jni.xiaomi.so (HyperOS 3.0.9) was built against a
# libgui where the virtual
#     Surface::connect(int, const sp<SurfaceListener>&, bool)
# sits at vtable offset 0x158. On Android 17 libgui that slot holds
# Surface::detachNextBuffer(), and connect became
#     Surface::connect(int, const sp<SurfaceListener>&, bool, bool, bool)
# at offset 0x150. IspInterfaceContext::setupOutputStream() therefore calls
# detachNextBuffer(), gets NO_INIT and the ISP never gets an output stream.
#
# Redirect that single call through a small code cave placed right after
# .plt (zero padding inside the R+X segment's last page), which calls the
# Android 17 slot with the two new bools set to false - exactly what
# libgui's own Surface::connect(int) does - and jumps back.

import hashlib, struct, sys

ORIG_SHA256    = '18f4b408e343b48045240ac890ee8113f57f376a418a37fdd13c68a565c0df07'
PATCHED_SHA256 = '87295699d84d1455dfa768c6eb6bdf32571c4493a5f71ee830347d769df7bb06'

CALL_SITE = 0x1710c   # ldr x8, [x8, #0x158] ; blr x8
RETURN_TO = 0x17114
CAVE      = 0x1ae40   # end of .plt == end of R+X PT_LOAD filesz

def b(src, dst):
    off = (dst - src) // 4
    return 0x14000000 | (off & 0x3ffffff)

def u32(x): return struct.pack('<I', x)

path = sys.argv[1]
data = bytearray(open(path, 'rb').read())

LDR_158 = 0xF940AD08  # ldr x8, [x8, #0x158]
BLR_X8  = 0xD63F0100  # blr x8
NOP     = 0xD503201F

sha = hashlib.sha256(data).hexdigest()
if sha == PATCHED_SHA256:
    print('already patched'); sys.exit(0)
if sha != ORIG_SHA256:
    sys.exit('unexpected input file (sha256 %s)' % sha)

cur = struct.unpack_from('<II', data, CALL_SITE)
if cur != (LDR_158, BLR_X8):
    sys.exit('unexpected code at call site: %08x %08x' % cur)
if any(data[CAVE:CAVE + 0x20]):
    sys.exit('code cave is not empty')

# Program headers: find the R+X PT_LOAD that ends exactly at CAVE
e_phoff, = struct.unpack_from('<Q', data, 0x20)
e_phentsize, e_phnum = struct.unpack_from('<HH', data, 0x36)
for i in range(e_phnum):
    ph = e_phoff + i * e_phentsize
    p_type, p_flags, p_off, p_vaddr, _, p_filesz, p_memsz, _ = struct.unpack_from('<IIQQQQQQ', data, ph)
    if p_type == 1 and p_flags == 5 and p_vaddr + p_filesz == CAVE and p_off == p_vaddr:
        struct.pack_into('<QQ', data, ph + 0x20, p_filesz + 0x20, p_memsz + 0x20)
        break
else:
    sys.exit('R+X PT_LOAD ending at the cave not found')

cave = [
    0xF940A908,                 # ldr  x8, [x8, #0x150]  (A17 Surface::connect 5-arg)
    0x2A1F03E4,                 # mov  w4, wzr
    0x2A1F03E5,                 # mov  w5, wzr
    BLR_X8,                     # blr  x8
    b(CAVE + 0x10, RETURN_TO),  # b    back
]
for i, insn in enumerate(cave):
    data[CAVE + 4 * i:CAVE + 4 * i + 4] = u32(insn)
data[CALL_SITE:CALL_SITE + 8] = u32(b(CALL_SITE, CAVE)) + u32(NOP)

sha = hashlib.sha256(data).hexdigest()
if sha != PATCHED_SHA256:
    sys.exit('patch result mismatch (sha256 %s)' % sha)
open(path, 'wb').write(data)
print('patched', path)
