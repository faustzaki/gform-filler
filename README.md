# gform-filler

Inspect & auto-fill public Google Forms from Python. No API key, no login —
parses the form's own structure (`FB_PUBLIC_LOAD_DATA_`) and POSTs to
`formResponse`.

Works with **any public form**: short text, paragraph, radio, dropdown,
checkbox, scale, date, time.

## Usage

```bash
# see questions + entry IDs of any form
python3 gform_filler.py inspect https://docs.google.com/forms/d/e/<ID>/viewform

# submit answers (titles must match exactly)
python3 gform_filler.py submit https://docs.google.com/forms/d/e/<ID>/viewform answers.json

# preview the fields without sending
python3 gform_filler.py submit <url> answers.json --dry-run
```

`answers.json` maps question titles to values; checkboxes take lists:

```json
{"Nama": "Budi Santoso",
 "Pernah beli via keranjang kuning?": "Ya",
 "Platform yang dipakai": ["TikTok", "Instagram"]}
```

Python API:

```python
from gform_filler import inspect, submit
form = inspect("https://docs.google.com/forms/d/e/<ID>/viewform")
submit(form, {"Nama": "Budi Santoso", ...})
```

## Notes

- Only works on forms that don't require sign-in.
- Question titles are the keys — copy them exactly from `inspect` output.
- Limit per submit: no bulk guard built in; pace your own requests.

## Test

```bash
python3 tests/test_filler.py   # offline self-check against tests/fixture_form.html
```
