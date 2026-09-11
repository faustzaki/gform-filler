#!/usr/bin/env python3
"""Self-check: parse fixture form, build payload, validate mapping. No network."""
import sys
sys.path.insert(0, ".")
from gform_filler import inspect, build_payload

form = inspect("tests/fixture_form.html")
assert form["form_id"].startswith("1FAIpQLS"), form["form_id"]
assert len(form["questions"]) == 3, form["questions"]
q = {x["title"].split()[0]: x for x in form["questions"]}
assert q["Nama"]["type"] == "short" and q["Nama"]["entry"] == "1807376276"
assert q["Dalam"]["type"] == "radio" and q["Dalam"]["options"] == ["Ya", "Tidak"]

# payload: title -> value mapping
fields = build_payload(form["questions"], {
    "Nama": "Budi Santoso",
    "Dalam 1 bulan terakhir ketika menggunakan TikTok, apakah Anda pernah tertarik pada suatu produk setelah melihat konten tentang produk tersebut?": "Ya",
    "Dalam 1 bulan terakhir, apakah Anda pernah membeli produk melalui keranjang kuning karena tertarik setelah melihat kontennya di TikTok?": "Tidak",
})
assert ("entry.1807376276", "Budi Santoso") in fields, fields
assert ("entry.1226223872", "Ya") in fields, fields
assert ("entry.1029731324", "Tidak") in fields, fields
assert len(fields) == 3, fields

# invalid radio option must raise
try:
    build_payload(form["questions"], {form["questions"][1]["title"]: "Mungkin"})
    raise SystemExit("FAIL: invalid option accepted")
except ValueError:
    pass

# missing required answer must raise
form2 = dict(form)
form2["questions"] = [dict(form["questions"][0], required=True)]
try:
    build_payload(form2["questions"], {})
    raise SystemExit("FAIL: missing required accepted")
except KeyError:
    pass

print("all checks passed")
