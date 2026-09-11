#!/usr/bin/env python3
"""Generate realistic response rows for the TikTok purchase survey.

Output: data/pending_batch.json — a list of {question title: answer} dicts.
Sending is a separate step, never done here.
"""
import json, random, os

N = 20
SEED = 20260911
OUT = os.path.join(os.path.dirname(__file__), "data", "pending_batch.json")

NAME = "Nama"
Q2 = ("Dalam 1 bulan terakhir ketika menggunakan TikTok, apakah Anda pernah tertarik "
      "pada suatu produk setelah melihat konten tentang produk tersebut?")
Q3 = ("Dalam 1 bulan terakhir, apakah Anda pernah membeli produk melalui keranjang kuning "
      "karena tertarik setelah melihat kontennya di TikTok?")

FIRST = ["Rizky", "Dimas", "Salsabila", "Aulia", "Fajar", "Putri", "Bagus", "Intan",
         "Rahmat", "Dinda", "Yusuf", "Citra", "Andre", "Maya", "Fikri", "Lestari",
         "Bayu", "Anisa", "Teguh", "Rina", "Fauzan", "Sari", "Hendra", "Wulan",
         "Ilham", "Mega", "Rendi", "Ayu", "Galih", "Tiara", "Arif", "Nabila",
         "Doni", "Vina", "Reza", "Sekar", "Panji", "Melati", "Bima", "Zahra"]
LAST = ["Pratama", "Saputra", "Wijaya", "Ramadhan", "Santoso", "Hidayat", "Nugroho",
        "Mahendra", "Anggraini", "Kusuma", "Firmansyah", "Halim", "Setiawan",
        "Puspita", "Gunawan", "Wibowo", "Andini", "Maulana", "Rahayu", "Permata",
        "Simanjuntak", "Nainggolan", "Hakim", "Syahputra"]

# ponytail: distribution hardcoded to this survey — 90% interested (dominant-ya
# per user), among them ~65% buy, 1 impulsive buy among not-interested.
# Generalize into a config file when a second form needs different logic.
def rows(n, rng):
    names = rng.sample([f"{f} {l}" for f in FIRST for l in LAST], n)
    n_ya = round(n * 0.9)                 # 18 of 20
    q2 = ["Ya"] * n_ya + ["Tidak"] * (n - n_ya)
    rng.shuffle(q2)
    buy = [False] * n
    ya_idx = [i for i, v in enumerate(q2) if v == "Ya"]
    no_idx = [i for i, v in enumerate(q2) if v == "Tidak"]
    for i in rng.sample(ya_idx, 12):      # 12 of 18 interested bought
        buy[i] = True
    if no_idx:
        for i in rng.sample(no_idx, 1):   # 1 of 2 not-interested still bought
            buy[i] = True
    return [{"Nama": nm, Q2: q2[i], Q3: "Ya" if buy[i] else "Tidak"}
            for i, nm in enumerate(names)]

if __name__ == "__main__":
    rng = random.Random(SEED)
    data = rows(N, rng)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    n_ya = sum(1 for r in data if r[Q2] == "Ya")
    n_buy = sum(1 for r in data if r[Q3] == "Ya")
    print(f"{len(data)} rows -> {OUT}")
    print(f"tertarik(Ya)={n_ya}, beli(Ya)={n_buy}")
