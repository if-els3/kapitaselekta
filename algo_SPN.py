# ============ FUNGSI ============

def fungsi_xor(plaintext, key):
    hasil = plaintext ^ key
    return f"{hasil:016X}"          # langsung jadi string 16 digit

def fungsi_sbox(inp):
    sbox = [0xE,0x4,0xD,0x1,
            0x2,0xF,0xB,0x8,
            0x3,0xA,0x6,0xC,
            0x5,0x9,0x0,0x7]
    hasil = ""
    for digit in inp:
        idx = int(digit, 16)
        hasil += hex(sbox[idx])[2:].upper()
    return hasil

def fungsi_permutasi(inp):
    permutasi = [0,5,10,15,4,9,14,3,8,13,2,7,12,1,6,11]
    hasil = [""] * 16
    for i in range(16):
        hasil[i] = inp[permutasi[i]]
    return "".join(hasil)

def mul2(a):
    a = a << 1
    if a & 0x10:
        a = a ^ 0x13
    return a & 0xF

def mul3(a):
    return mul2(a) ^ a

def fungsi_kali_matriks(inp):
    hasil = ""
    for blok in range(0, 16, 4):          # tiap 4 digit
        a = [int(inp[blok+j], 16) for j in range(4)]
        b0 = mul2(a[0]) ^ mul3(a[1]) ^ a[2]       ^ a[3]
        b1 = a[0]       ^ mul2(a[1]) ^ mul3(a[2]) ^ a[3]
        b2 = a[0]       ^ a[1]       ^ mul2(a[2]) ^ mul3(a[3])
        b3 = mul3(a[0]) ^ a[1]       ^ a[2]       ^ mul2(a[3])
        for nilai in [b0, b1, b2, b3]:
            hasil += hex(nilai)[2:].upper()
    return hasil

# ============ MAIN ============

plaintext = 0x1234ABCDEF567890
key       = 0x1234567890ABCDEF

hasil_xor  = fungsi_xor(plaintext, key)
hasil_sbox = fungsi_sbox(hasil_xor)
hasil_permutasi = fungsi_permutasi(hasil_sbox)
hasil_kali_matriks = fungsi_kali_matriks(hasil_permutasi)

print(f"Hasil XOR       : {hasil_xor}")
print(f"Hasil S-BOX     : {hasil_sbox}")
print(f"Hasil Permutasi : {hasil_permutasi}")
print(f"Hasil Kali Matriks : {hasil_kali_matriks}") 


#=============================================
#PENJELASAN
#=============================================

# =====================================================================
#  BLOCK CIPHER 64-BIT
#  Alur sesuai diagram:
#  PLAINTEXT --XOR(Key)--> S-BOX --PERMUTASI--> KALI MATRIKS --> CIPHERTEXT
# =====================================================================


# ---------------------------------------------------------------------
# PROSES 1 : XOR DENGAN KUNCI
# ---------------------------------------------------------------------
# Di diagram : kotak "XOR" yang menerima PLAINTEXT (atas) dan Key (kiri).
# Fungsinya  : mencampur plaintext 64 bit dengan key 64 bit.
# Operasinya : XOR bit per bit ( ^ ).
# Outputnya  : 64 bit (16 digit hex) yang masuk ke deretan S-Box.
# ---------------------------------------------------------------------
def fungsi_xor(plaintext, key):
    hasil = plaintext ^ key          # XOR 64 bit: tiap bit dibanding plaintext vs key
    return f"{hasil:016X}"           # ubah ke string hex 16 digit (padding nol di depan)


# ---------------------------------------------------------------------
# PROSES 2 : FUNGSI S (S-BOX) -> SUBSTITUSI
# ---------------------------------------------------------------------
# Di diagram : 16 kotak "S" (4 blok x 4 kotak).
# Fungsinya  : tiap 4 bit (1 digit hex) DIGANTI nilai lain lewat tabel.
#              Posisi tetap, NILAI yang berubah.
# Tabel S    : input 0..F selalu urut, yang ditulis cukup OUTPUT-nya saja.
#              index list = nilai input, isi list = nilai output.
# ---------------------------------------------------------------------
def fungsi_sbox(inp):
    sbox = [0xE,0x4,0xD,0x1,         # input 0->E, 1->4, 2->D, 3->1
            0x2,0xF,0xB,0x8,         # input 4->2, 5->F, 6->B, 7->8
            0x3,0xA,0x6,0xC,         # input 8->3, 9->A, A->6, B->C
            0x5,0x9,0x0,0x7]         # input C->5, D->9, E->0, F->7
    hasil = ""
    for digit in inp:                # proses tiap digit hex
        idx = int(digit, 16)         # ubah digit hex jadi angka 0..15 (jadi index)
        hasil += hex(sbox[idx])[2:].upper()   # ambil output dari tabel, buang prefix '0x'
    return hasil


# ---------------------------------------------------------------------
# PROSES 3 : FUNGSI PERMUTASI -> MENGACAK POSISI
# ---------------------------------------------------------------------
# Di diagram : garis-garis MENYILANG antara S-Box dan Kali Matriks.
# Fungsinya  : memindahkan posisi digit. NILAI tetap, POSISI yang berubah.
# Cara baca  : hasil[i] diambil dari inp[ permutasi[i] ]  ("ambil dari posisi").
# ---------------------------------------------------------------------
def fungsi_permutasi(inp):
    permutasi = [0,5,10,15,4,9,14,3,8,13,2,7,12,1,6,11]   # tabel posisi sumber
    hasil = [""] * 16
    for i in range(16):
        hasil[i] = inp[permutasi[i]]   # posisi i diisi digit dari posisi permutasi[i]
    return "".join(hasil)              # gabung list jadi string


# ---------------------------------------------------------------------
# HELPER : PERKALIAN DI GF(2^4) dengan modulus x^4 + x + 1 (= 0x13)
# ---------------------------------------------------------------------
# mul2 = kali 2 (kali x), mul3 = kali 3. "+" pada GF artinya XOR.
# Kalau muncul x^4 (bit 0x10) -> direduksi: x^4 = x + 1 -> XOR 0x13.
# ---------------------------------------------------------------------
def mul2(a):
    a = a << 1                       # geser kiri = kali 2 (kali x)
    if a & 0x10:                     # kalau muncul suku x^4
        a = a ^ 0x13                 # reduksi pakai modulus x^4 + x + 1
    return a & 0xF                   # ambil 4 bit terakhir

def mul3(a):
    return mul2(a) ^ a               # 3a = 2a + a  (XOR)


# ---------------------------------------------------------------------
# PROSES 4 : FUNGSI KALI MATRIKS -> PENCAMPURAN (DIFFUSION)
# ---------------------------------------------------------------------
# Di diagram : 4 kotak "Kali Matriks", outputnya jadi CIPHERTEXT.
# Fungsinya  : tiap 4 digit (1 subblok) dikalikan matriks 4x4 di GF(2^4).
# Rumus      :
#   b0 = 2a0 + 3a1 +  a2 +  a3
#   b1 =  a0 + 2a1 + 3a2 +  a3
#   b2 =  a0 +  a1 + 2a2 + 3a3
#   b3 = 3a0 +  a1 +  a2 + 2a3
#   ( "+" = XOR ,  "2x"/"3x" = mul2/mul3 )
# ---------------------------------------------------------------------
def fungsi_kali_matriks(inp):
    hasil = ""
    for blok in range(0, 16, 4):                       # ambil per 4 digit (1 subblok)
        a = [int(inp[blok+j], 16) for j in range(4)]   # a0..a3 dari subblok ini
        b0 = mul2(a[0]) ^ mul3(a[1]) ^ a[2]       ^ a[3]
        b1 = a[0]       ^ mul2(a[1]) ^ mul3(a[2]) ^ a[3]
        b2 = a[0]       ^ a[1]       ^ mul2(a[2]) ^ mul3(a[3])
        b3 = mul3(a[0]) ^ a[1]       ^ a[2]       ^ mul2(a[3])
        for nilai in [b0, b1, b2, b3]:
            hasil += hex(nilai)[2:].upper()
    return hasil


# =====================================================================
#  MAIN : jalankan keempat proses berurutan (sesuai alur diagram)
# =====================================================================
plaintext = 0x1234ABCDEF567890      # PLAINTEXT 64 bit (kotak atas di diagram)
key       = 0x1234567890ABCDEF      # KEY 64 bit       (kotak kiri di diagram)

hasil_xor          = fungsi_xor(plaintext, key)        # PROSES 1: XOR
hasil_sbox         = fungsi_sbox(hasil_xor)            # PROSES 2: S-Box
hasil_permutasi    = fungsi_permutasi(hasil_sbox)      # PROSES 3: Permutasi
hasil_kali_matriks = fungsi_kali_matriks(hasil_permutasi)  # PROSES 4: Kali Matriks

print(f"Plaintext          : {plaintext:016X}")
print(f"Key                : {key:016X}")
print(f"Hasil XOR          : {hasil_xor}")
print(f"Hasil S-BOX        : {hasil_sbox}")
print(f"Hasil Permutasi    : {hasil_permutasi}")
print(f"Hasil Kali Matriks : {hasil_kali_matriks}")    # ini = CIPHERTEXT 64 bit
