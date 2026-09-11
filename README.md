# gform-filler

Isi Google Form publik otomatis dari Python / CLI. Tanpa API key, tanpa login —
script baca struktur internal form (`FB_PUBLIC_LOAD_DATA_`) langsung dari
halaman form, lalu POST ke endpoint `formResponse`.

**General**: satu library untuk semua form publik. Ganti URL, gak perlu ubah kode.

## Cocok untuk apa

- ✅ Google Form **publik** (gak wajib login Google)
- ✅ Tipe pertanyaan: **short answer, paragraph, multiple choice (radio),
  dropdown, checkbox, linear scale, date, time**
- ✅ Form 1 halaman maupun multi-section (urut dari atas)
- ✅ Isi satu kali (CLI / Python) atau batch berkali-kali (dengan jeda)
- ❌ Form yang **wajib login Google** (setting "collect email" aktif, atau
  akses terbatas organisasi) — gak bisa
- ❌ Upload file di form — gak didukung

## Prasyarat

Python 3.8+ saja, **tanpa dependency**.

## Tata cara pakai

### 1. Inspect form — lihat pertanyaan & opsi yang valid

```bash
python3 gform_filler.py inspect "https://docs.google.com/forms/d/e/<FORM_ID>/viewform"
```

Output: judul form, tipe tiap pertanyaan, `entry` ID, dan daftar opsi.
**Salin judul pertanyaan persis** (huruf besar-kecil & tanda baca) — judul itu
kunci jawabannya.

### 2. Buat file jawaban `answers.json`

```json
{
  "Nama": "Budi Santoso",
  "Status": "Mahasiswa",
  "Platform": ["TikTok", "Instagram"],
  "Skor": "4",
  "Tanggal": "2026-09-11",
  "Jam": "14:30"
}
```

| Tipe | Format nilai |
|---|---|
| short / paragraph | string |
| radio / dropdown | satu string, **harus persis** salah satu opsi |
| checkbox | list of string (boleh lebih dari satu) |
| scale | string angka, contoh `"4"` |
| date | `"2026-09-11"` |
| time | `"14:30"` |

### 3. Preview payload (gak dikirim)

```bash
python3 gform_filler.py submit <URL> answers.json --dry-run
```

### 4. Kirim

```bash
python3 gform_filler.py submit <URL> answers.json
```

`HTTP 200` = masuk. Cek di tab Responses form.

### 5. Batch (opsional)

```bash
python3 -c "
import sys, json, time; sys.path.insert(0,'.')
from gform_filler import inspect, submit
form = inspect('<URL>')
for r in json.load(open('rows.json', encoding='utf-8')):
    print(r['Nama'], submit(form, r)[0])
    time.sleep(4)   # jeda antar submit — jangan kirim massal
"
```

## Contoh generator responden

`generate_responses.py` = contoh pembuat batch jawaban random-realistis untuk
sebuah survei (pool nama Indonesia, distribusi jawaban dengan korelasi logis
antarpertanyaan). Salin sebagai template untuk form/skenario lain: ganti judul
pertanyaan + pool jawaban + rasionya, output-nya JSON siap dikirim.

```bash
python3 generate_responses.py   # -> data/pending_batch.json
```

## API Python

```python
from gform_filler import inspect, submit

form = inspect("https://docs.google.com/forms/d/e/<ID>/viewform")
submit(form, {"Nama": "Budi", "Status": "Mahasiswa", "Platform": ["TikTok"]})
```

`inspect()` juga menerima path file HTML yang sudah disimpan — berguna untuk
test offline.

## Batasan & tips

- Setting **"Kumpulkan alamat email"** harus mati; kalau aktif, Google minta
  login dan submit anonim gagal.
- Jawaban radio/dropdown divalidasi: opsi yang gak ada di form = error, gak
  terkirim. Pertanyaan wajib kosong = error.
- Pacing tanggung sendiri (pakai `time.sleep` antar submit).
- Form multi-section di-submit sekali lewat (`pageHistory=0`); form dengan
  logika per-halaman kompleks belum dites di form nyata.
- Scale/date/time diterima sebagai teks berformat; belum ada validasi range.

## Test offline

```bash
python3 tests/test_filler.py     # parse + payload vs snapshot form asli
python3 gform_filler.py inspect tests/fixture_multi.html   # 8 tipe sekaligus
```
