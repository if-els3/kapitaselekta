plain = 0x0123456789ABCDEF
key = 0x9876543210FEDCBA

def hex_nib(data, panjang=16):
    hasil = []
    for i in range(panjang):
        nib = (data >> (4 * i )) & 0xf
        hasil.append(nib)

    hasil.reverse()
    return hasil

def nib_hex(data, panjang=16):
    hasil = 0
    for i in range(panjang):
        val = (data << 4 * (panjang - (i + 1))) & 0xffffffffffffffff
        hasil |= val
    
    return hasil

plain_nib = hex_nib(plain)
key_nib = hex_nib(key)

def add_key(plain, key):
    hasil = []
    for i in range(16):
        hasil.append(plain[i] ^ key[i])
    return hasil

A = add_key(plain_nib, key_nib)
print(A)