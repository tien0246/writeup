# Meowware Writeup

I got infected. Help me find out what was stolen!

Challenge:  
- **Name**: Meowware  
- **Points**: 996  
- **Author**: Elma  

## Initial Analysis
I started by analyzing the provided ELF file using the `file` command:

```bash
$ file ./client
./client: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), BuildID[sha1]=53a87fd5741a38f22047405a7e29d947de8cdd45, for GNU/Linux 3.2.0, statically linked, no section header
```

Running the program yielded no visible output. Loading it into IDA revealed very little information, suggesting it was packed. I tried unpacking it with UPX, but it failed:

```bash
$ upx -d ./client
upx: ./client: NotPackedException: not packed by UPX
```

This indicated a custom packer, requiring manual unpacking.

## Tracing Execution
I used `strace` and `ltrace` to observe the program's behavior, but it terminated quickly after a `clone` syscall:

```bash
clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|CLONE_CHILD_SETTID|SIGCHLD, child_tidptr=0x1138f690) = 426
wait4(426, [{WIFEXITED(s) && WEXITSTATUS(s) == 0}], 0, NULL) = 426
--- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=426, si_uid=1000, si_status=0, si_utime=0, si_stime=0} ---
clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|CLONE_CHILD_SETTID|SIGCHLD, child_tidptr=0x1138f690) = 427
exit_group(0)                           = ?
+++ exited with 0 +++
```

To gain more insight, I used `bpftrace` with a custom script ([link](https://gist.github.com/tien0246/3750e630af623effa3f92c7395ebf4b9)):

```bash
[Parent PID 1175] Forked child PID 1176
[PID 1176] Enter syscall: ptrace
        request: 0x0
        pid:     0
[PID 1176] Exit syscall: ptrace, return: 0x0
[PID 1176] Main process exit
=============================================================
[Parent PID 1175] Forked child PID 1177
[PID 1175] Main process exit
=============================================================
[Parent PID 1177] Forked child PID 1178
[PID 1178] Enter syscall: ptrace
        request: 0x0
        pid:     0
[PID 1178] Exit syscall: ptrace, return: 0x0
[PID 1178] Main process exit
=============================================================
[Parent PID 1177] Forked child PID 1179
[PID 1177] Main process exit
[PID 1179] Enter syscall: socket
        family:  2
        type:    1
        protocol: 0
[PID 1179] Exit syscall: socket, return: 0x3
=============================================================
[PID 1179] Enter syscall: connect
        fd:      3
        addrlen: 16
PID 1179 is connecting to 139.59.228.105:443 
[PID 1179] Exit syscall: connect, return: 0xffffffffffffff92
[PID 1179] Main process exit
```

The output showed the program forks multiple times, uses `ptrace` for anti-debugging, and eventually connects to a C2 server at `139.59.228.105:443`.

## Unpacking with GDB
Knowing about the `ptrace` anti-debugging, I used GDB to dump the unpacked program:

```bash
$ gdb ./client
(gdb) catch syscall ptrace
(gdb) info proc mappings
process 974
Mapped address spaces:
Start Addr         End Addr           Size               Offset             Perms File
0x0000000000400000 0x0000000000401000 0x1000             0x0                r--p
0x0000000000401000 0x00000000004c8000 0xc7000            0x0                r-xs  /memfd:upx (deleted)
0x00000000004c8000 0x00000000004f9000 0x31000            0x0                r--p
0x00000000004f9000 0x0000000000504000 0xb000             0x0                rw-p
0x0000000000568000 0x000000000058a000 0x22000            0x0                rw-p  [heap]
0x00007ffff7ff7000 0x00007ffff7ff8000 0x1000             0x0                r--p  /mnt/c/Users/TIEN/Downloads/dist-meowware/dist-meowware/client
0x00007ffff7ff9000 0x00007ffff7ffd000 0x4000             0x0                r--p  [vvar]
0x00007ffff7ffd000 0x00007ffff7fff000 0x2000             0x0                r-xp  [vdso]
0x00007ffffffdd000 0x00007ffffffff000 0x22000            0x0                rw-p  [stack]
```

Noticing a segment named `upx`, I dumped the memory from `0x400000` to `0x504000`:

```bash
(gdb) dump memory dump 0x400000 0x504000
```

Loading the dump into IDA revealed a clean, fully unpacked binary.

## Reverse Engineering
Since the program used a socket connection, I located the `syscall(0x2C)` for `connect`, leading to the main function at `sub_402712`. The decoding function was found at `sub_402307`, which used AES-CBC with a key at `qword_4FB462` and an IV of 0. The key was set in `sub_401DCD`.

I initially tried `uEmu` to dump the key, but unsupported instructions caused issues. Instead, I wrote a Python script to replicate the decoding:

```python
from Crypto.Cipher import AES

KEY_4C8240 = bytes([
    0xD6, 0x29, 0x87, 0x4C, 0xA5, 0xF3, 0x71, 0xB9,
    0xE8, 0x54, 0x32, 0x0F, 0xC1, 0x6A, 0xB5, 0x7D,
    0x91, 0x3E, 0x8A, 0x2C, 0xB4, 0x57, 0x69, 0xDF,
    0x3A, 0x84, 0x72, 0xF1, 0xC6, 0x9E, 0x4B, 0x25,
])

IV_401DCD = bytes([
    0x35, 0x7C, 0x94, 0xAF, 0x66, 0xD2, 0x87, 0x15,
    0xC8, 0x4B, 0x9E, 0x23, 0x5D, 0x7A, 0xF1, 0xB8,
])

UNK_4C8020 = bytes.fromhex(
    "B8D0BEA0C5E57F6281D123D5D8DFC5E164E3C8D0105B72FFBD01CCB82CE1C4B1"
    "007AA34308636464EB162BF3A35846677EA9C61B749F8B3F06320774F048461C"
    "12F9FFE1FE35E37C0F105E4A7876B4541D0F8436D7513915B93B42A13AEB02FF"
)

cipher = AES.new(KEY_4C8240, AES.MODE_CBC, IV_401DCD)
plain = cipher.decrypt(UNK_4C8020)

ptr = 0
host = plain.split(b'\x00', 1)[0].decode()
ptr += len(host) + 1
port = int.from_bytes(plain[ptr:ptr+2], 'little')
ptr += 2

def cstr(off):
    end = plain.find(b'\x00', off)
    s = plain[off:end].decode()
    return s, end+1

cmd_exit, ptr = cstr(ptr)
cmd_write, ptr = cstr(ptr)
cmd_read, ptr = cstr(ptr)
cmd_shell, ptr = cstr(ptr)
aes_session_key = plain[ptr:ptr+32]

print("C2 host :", host)
print("C2 port :", port)
print("Commands:", [cmd_exit, cmd_write, cmd_read, cmd_shell])
print("Session key (hex)  :", aes_session_key.hex())
print("Session key (ascii):", aes_session_key.decode())
```

Output:

```bash
C2 host : 139.59.228.105
C2 port : 443
Commands: ['EXIT', 'WRITE', 'READ', 'SHELL']
Session key (hex)  : 4c75636b7920537461722077617320686572652c20435446206b657920333721
Session key (ascii): Lucky Star was here, CTF key 37!
```

## Decrypting Network Traffic
Using the session key and a provided PCAP, I decrypted the network traffic:

```python
from Crypto.Cipher import AES
import binascii, string

KEY = b"Lucky Star was here, CTF key 37!"
IV = b"\x00"*16

raw_hex_blobs = [
    "0000002060898dad37aa74728774033d1c8b694d099617f6ddb7d664ac0e72d8341a67dc",
    "0000001093c11ff838da6207b31f39595ca4516d",
    "000000306124dee35b39ee393b7bd5bee4aec5406c7c709e5ea55cadf6b860150110934b690aa6cfa044be2e6dce3150dc681844",
    "00000010715e15de02bcabe4ebfa0a63b9fdebc9",
    "000000103e4995df9655e1c394ab9d4bd53f67bc",
    "00000020a6f2962ad75226b7a293e725524a77b6f45399bc663ed01558e2981dcb039028",
    "00000040cdbb20b6427455414f0e7f0b1dce71e70b0d62ae19bafa2bbb7a8f49c06e8fac908b6601af41f10c3f3c565ed21adaa5d553e8048cf50d99c06bc9bce0ebc6d9",
    "000000409b60068d0b129f91d5045cb084bccd0085a2fcb4540920ac88264be02c8f73e9752fed75c17c3021b26d65eb05d2651f090056a791d13de16290b00ca9ba16c5",
    "0000004033e9d74d53807b8c9eb7636ddf0747bab3f12c3faaabf7b4db19cc2d291ccda09c2d1c23ef4cc1b9424a855d95fededff21b39d330581d7d165070401f2003e1",
    "000000105d396ad17b51f4d0ce3daf1b9b44b222",
    "0000001063840b73410e61619d66af686dd00a4e",
]

def decrypt_blob(hex_blob: str):
    hex_blob = hex_blob.strip()
    if len(hex_blob) < 8:
        return None, "too short"
    plen = int(hex_blob[:8], 16)
    cipher_hex = hex_blob[8:8+plen*2]
    if len(cipher_hex) != plen*2:
        return None, f"length mismatch ({plen} vs {len(cipher_hex)//2})"
    cipher_bytes = bytes.fromhex(cipher_hex)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    plain = cipher.decrypt(cipher_bytes)
    pad = plain[-1]
    if 1 <= pad <= 16 and plain.endswith(bytes([pad])*pad):
        plain = plain[:-pad]
    return cipher_hex, plain

def to_ascii(b: bytes):
    return ''.join(chr(c) if chr(c) in string.printable and c not in b'\r\n\t\x0b\x0c' else '.' for c in b)

results = []
for idx, h in enumerate(raw_hex_blobs, 1):
    cipher_hex, plain = decrypt_blob(h)
    if cipher_hex is None:
        results.append(f"Blob {idx}: error {plain}")
        continue
    ascii_repr = to_ascii(plain)
    results.append(f"Blob {idx}:\n  cipher: {cipher_hex}\n  plain : {binascii.hexlify(plain).decode()}\n  ascii : {ascii_repr}\n")

print("\n".join(results))
```

The key output was:

```bash
Blob 7:
  cipher: cdbb20b6427455414f0e7f0b1dce71e70b0d62ae19bafa2bbb7a8f49c06e8fac908b6601af41f10c3f3c565ed21adaa5d553e8048cf50d99c06bc9bce0ebc6d9
  plain : 21001000340d0f034119583d5c2a5d5b65797b7570785f6c6f6f6b696e675f7265616c5f637574655f746f646179217d
  ascii : !...4...A.X=\*][ey{upx_looking_real_cute_today!}
```

## Flag
The flag was extracted from Blob 7:

```bash
flag: grey{upx_looking_real_cute_today!}
```

This concluded the analysis, revealing the stolen data as the flag.