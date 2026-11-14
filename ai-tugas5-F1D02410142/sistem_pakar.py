import json
import sys
import textwrap

FILE_KB = "kb_wifi.json"
LEBAR = 78


def garis(karakter="-"):
    print(karakter * LEBAR)


def cetak(teks, indent=0, lanjut=4):
    """Cetak teks panjang dengan pemenggalan baris yang rapi."""
    print(textwrap.fill(teks, width=LEBAR,
                        initial_indent=" " * indent,
                        subsequent_indent=" " * (indent + lanjut)))


def muat_kb(path=FILE_KB):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def syarat_terpenuhi(aturan, memori):
    """mode 'dan': semua syarat ada di memori; mode 'atau': salah satu cukup."""
    ada = [s in memori for s in aturan["jika"]]
    return all(ada) if aturan["mode"] == "dan" else any(ada)


def fakta_dasar(kb):
    """Fakta yang tidak pernah menjadi hasil aturan -> ditanyakan ke user."""
    hasil = {r["maka"] for r in kb["aturan"]}
    urut = []
    for r in kb["aturan"]:
        for s in r["jika"]:
            if s not in hasil and s not in urut:
                urut.append(s)
    return urut


def forward_chaining(kb, fakta_awal):
    memori = set(fakta_awal)
    asal = {}  
    log = []
    siklus = 0
    while True:
        siklus += 1
       
        cocok = [r for r in kb["aturan"]
                 if r["maka"] not in memori and syarat_terpenuhi(r, memori)]
        if not cocok:
            log.append(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            break
        r = cocok[0]  
        memori.add(r["maka"])
        asal[r["maka"]] = r
        log.append(f"Siklus {siklus}: {r['id']} -> {r['maka']}")
    return memori, asal, log


def cetak_alasan(fakta, asal, memori, tingkat=0):
    r = asal[fakta]
    syarat_ada = [s for s in r["jika"] if s in memori]
    cetak(f"{fakta}  <-  {r['id']} ({', '.join(syarat_ada)}) [{r['sumber']}]",
          indent=2 + 3 * tingkat, lanjut=5)
    for s in syarat_ada:
        if s in asal:
            cetak_alasan(s, asal, memori, tingkat + 1)


def tanya_ya_tidak(teks):
    while True:
        jawab = input(teks + " (y/t) > ").strip().lower()
        if jawab in ("y", "t"):
            return jawab == "y"
        print("    Jawab dengan y atau t.")


def ajukan_pertanyaan(kb):
    daftar = fakta_dasar(kb)
    fakta_awal = []
    for i, f in enumerate(daftar, 1):
        teks = textwrap.fill(f"{i}. {kb['pertanyaan'][f]}", width=LEBAR - 10,
                             subsequent_indent="   ")
        if tanya_ya_tidak(teks):
            fakta_awal.append(f)
    return fakta_awal


def main():
    kb = muat_kb()
    garis("=")
    cetak(kb["judul"].upper(), indent=1)
    garis("=")
    print("Jawab dengan y (ya) atau t (tidak).\n")

    while True:
        fakta_awal = ajukan_pertanyaan(kb)

        # pemeriksaan jawaban yang saling bertentangan
        
        if ("hanya satu perangkat bermasalah" in fakta_awal
                and "semua perangkat bermasalah" in fakta_awal):
            print("\n[!] Pertanyaan 1 dan 2 tidak boleh sama-sama dijawab ya. "
                  "Silakan ulangi.\n")
            continue
        break

    print()
    garis()
    print("FAKTA AWAL")
    if fakta_awal:
        for f in fakta_awal:
            cetak(f"- {f}", indent=2, lanjut=2)
    else:
        print("  (tidak ada)")

    memori, asal, log = forward_chaining(kb, fakta_awal)
    print("\nPROSES (FORWARD CHAINING)")
    for baris in log:
        cetak(baris, indent=2, lanjut=4)

    akhir = [k for k in kb["kesimpulan"] if k in asal]
    print("\nKESIMPULAN")
    if akhir:
        for k in akhir:
            cetak(f"* {k}", indent=2, lanjut=2)
        print("\nALASAN")
        for k in akhir:
            cetak_alasan(k, asal, memori)
    else:
        print("  Tidak ada kesimpulan dari fakta yang diberikan.")

    print("\nCATATAN")
    cetak(kb["batas"], indent=2, lanjut=0)
    garis("=")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        sys.exit(f"File {FILE_KB} tidak ditemukan. Jalankan dari folder yang sama.")