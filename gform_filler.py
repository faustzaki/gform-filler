#!/usr/bin/env python3
"""gform_filler.py — inspect and auto-fill public Google Forms.

Parses the form's internal structure (FB_PUBLIC_LOAD_DATA_) from the page
itself, maps question titles to entry IDs, and POSTs answers to formResponse.
Works with any public form: pass a URL or a saved HTML file.
"""
import json
import random
import re
import sys
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TYPE = {0: "short", 1: "paragraph", 2: "radio", 3: "dropdown", 4: "checkbox",
        5: "scale", 7: "section", 8: "page", 9: "date", 10: "time"}


def _load(source):
    """Return (parsed FB_PUBLIC_LOAD_DATA_, raw html) from URL or HTML file."""
    if re.match(r"https?://", source):
        req = urllib.request.Request(source, headers={"User-Agent": UA})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    else:
        html = open(source, encoding="utf-8").read()
    m = re.search(r"FB_PUBLIC_LOAD_DATA_\s*=\s*(.*?);\s*</script>", html, re.S)
    if not m:
        raise ValueError("FB_PUBLIC_LOAD_DATA_ not found — form not public or URL wrong")
    return json.loads(m.group(1)), html


def inspect(source):
    """Parse any public form -> dict with submit_url and question list.

    Each question: {id, type, title, entry, options, required}.
    supported types: short, paragraph, radio, dropdown, checkbox, scale, date, time
    """
    data, html = _load(source)
    fpath = re.search(r'action="([^"]*formResponse[^"]*)"', html)
    questions, used = [], set()

    def walk(node):
        if (isinstance(node, list) and node and isinstance(node[0], int)
                and len(node) > 4 and node[3] in TYPE
                and isinstance(node[1], str) and node[0] not in used):
            used.add(node[0])
            entry, options = None, []
            try:
                entry = node[4][0][0]
                options = [o[0] for o in (node[4][0][1] or []) if isinstance(o, list)]
            except Exception:
                pass
            if entry:
                questions.append({
                    "id": node[0], "type": TYPE[node[3]], "title": node[1],
                    "entry": str(entry), "options": options,
                    "required": bool(node[2]),
                })
            return
        for sub in (node if isinstance(node, list) else []):
            walk(sub)

    walk(data[1])
    form_id = (re.search(r"/d/e/([^/]+)/", source if re.match(r"https?://", source) else html)
               or [None, "unknown"])[1]
    return {
        "form_id": form_id,
        "title": data[3] if len(data) > 3 and isinstance(data[3], str) else "",
        "submit_url": fpath.group(1) if fpath else
                      f"https://docs.google.com/forms/d/e/{form_id}/formResponse",
        "questions": questions,
    }


def build_payload(questions, answers):
    """answers = {question title: value | [values]}. Returns form field pairs.

    Unmatched titles are ignored; missing required questions raise KeyError.
    """
    fields = []
    for q in questions:
        a = answers.get(q["title"])
        if a is None:
            if q["required"]:
                raise KeyError(f"required question not answered: {q['title']!r}")
            continue
        # checkbox: a list of option labels
        values = a if isinstance(a, list) else [a]
        for v in values:
            v = str(v)
            if q["type"] in ("radio", "dropdown") and q["options"] and v not in q["options"]:
                raise ValueError(f"{q['title']!r}: {v!r} not in options {q['options']}")
            fields.append((f"entry.{q['entry']}", v))
    return fields


def submit(inspected, answers, dry_run=False):
    """POST answers to the form. Returns (status, fields)."""
    fields = build_payload(inspected["questions"], answers)
    fields += [("fvv", "1"), ("pageHistory", "0"), ("submit", "Submit")]
    if dry_run:
        return 0, fields
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        inspected["submit_url"], data=data,
        headers={"User-Agent": UA,
                 "Content-Type": "application/x-www-form-urlencoded",
                 "Referer": f"https://docs.google.com/forms/d/e/{inspected['form_id']}/viewform"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, fields


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("inspect", "submit"):
        sys.exit("usage:\n  gform_filler.py inspect <url|file.html>\n"
                 "  gform_filler.py submit <url|file.html> answers.json [--dry-run]")
    form = inspect(sys.argv[2])
    if sys.argv[1] == "inspect":
        print(json.dumps(form, ensure_ascii=False, indent=2))
        return
    answers = json.load(open(sys.argv[3], encoding="utf-8"))
    dry = "--dry-run" in sys.argv
    status, fields = submit(form, answers, dry_run=dry)
    print(("DRY-RUN fields" if dry else f"HTTP {status}") + ": "
          + urllib.parse.urlencode(fields, safe=""))


if __name__ == "__main__":
    main()
