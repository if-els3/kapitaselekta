
def rotl(val, r_bits, width=8):
    mask = (1 << width) - 1
    return ((val << r_bits) | (val >> (width - r_bits))) & mask

def fungsif0(x, key):
    return ((rotl(x, 1) ^ rotl(x, 2) ^ rotl(x, 7)) + key) & 0xFF

def fungsif1(x, key):
    return (rotl(x, 3) ^ rotl(x, 4) ^ rotl(x, 6)) ^ key

def swap(h,g,f,e,d,c,b,a):
    return g,f,e,d,c,b,a,h

def splitPlaintext(x):
    return (x>>56 & 0xFF, (x>>48) & 0xFF, (x>>40) & 0xFF, (x>>32) & 0xFF, (x>>24) & 0xFF, (x>>16) & 0xFF, (x>>8) & 0xFF, x & 0xFF)

def splitKeys(x):
    return (x>>24) & 0xFF, (x>>16) & 0xFF, (x>>8) & 0xFF, x & 0xFF

hexInput = 0xabcdef0123456789
k = 0x01b2c3d4

k3, k2, k1, k0 = splitKeys(k)
h, g, f, e, d, c, b, a = splitPlaintext(hexInput)

for i in range(8):
    temp_a = a
    temp_b = (fungsif1(a, k0) + b) & 0xFF  # Perbaikan: Masking 0xFF
    temp_c = c
    temp_d = fungsif0(c, k1) ^ d
    temp_e = e
    temp_f = (fungsif1(e, k2) + f) & 0xFF  # Perbaikan: Masking 0xFF
    temp_g = g
    temp_h = fungsif0(f, k3) ^ h

    # 5. Perbaikan: Swap diletakkan di dalam loop
    h, g, f, e, d, c, b, a = swap(temp_h, temp_g, temp_f, temp_e, temp_d, temp_c, temp_b, temp_a)
    
    # Menampilkan hasil setiap ronde agar persis seperti tabel dokumen
    print(f"Ronde {i+1}: 0x{h:02x} 0x{g:02x} 0x{f:02x} 0x{e:02x} 0x{d:02x} 0x{c:02x} 0x{b:02x} 0x{a:02x}")