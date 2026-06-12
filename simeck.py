pt = 0xabcdef0123456789
key = 0x01234567

def rotl(val, r):
    return ((val << r) | (val >> (32 - r))) & ((1<<32) - 1)

def fungsiF(a,b):
    return (a & (rotl(a, 5)) ^ b ^(rotl (a,1)))

def xorkey(val, key):
    return val ^ key

def swap (a, b):
    return b, a 

for i in range(1):
    kiri = (pt >> 32) & 0xFFFFFFFF
    kanan = pt & 0xFFFFFFFF

    b = fungsiF(kiri, kanan)
    c = xorkey (b, key)
    kiri, kanan = swap(kiri, c)
    pt = (kiri << 32) | kanan

print(pt, format(pt, '016x'))



