"""Make inputs.py the single source of truth for the app's starting values.

index.html keeps its own DEFAULTS (it must run standalone, with no Python). This
script reads inputs.py and rewrites that DEFAULTS block so the widget opens with
the same numbers the Python model uses.

Run after editing inputs.py:   python3 sync_defaults.py
Then hard-refresh index.html (and click "Reset to defaults" if you'd previously
changed values in that browser — saved session values take priority over DEFAULTS).
"""
import importlib.util
import json
import pathlib
import re

ROUTABLE = ["A", "B", "C", "D", "F"]
OTHER_Q = ["E", "G", "H", "I", "J", "K", "L"]


def load_inputs():
    spec = importlib.util.spec_from_file_location("inputs", "inputs.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def js(obj):
    return json.dumps(obj, ensure_ascii=False)


def main():
    inp = load_inputs()
    pe = [[k, v] for k, v in inp.p_E_win.items()]
    tq = {g: [[k, v] for k, v in inp.third_and_qualify[g].items()] for g in ROUTABLE}
    q = {g: inp.q_group[g] for g in OTHER_Q}

    block = (
        "const DEFAULTS = {\n"
        f"  pEWin: {js(pe)},\n"
        "  tq: {\n"
        + "".join(f"    {g}: {js(tq[g])},\n" for g in ROUTABLE)
        + "  },\n"
        f"  q: {js(q)},\n"
        "};"
    )

    html_path = pathlib.Path("index.html")
    html = html_path.read_text(encoding="utf-8")
    new, n = re.subn(r"const DEFAULTS = \{[\s\S]*?\n\};", block, html, count=1)
    if n != 1:
        raise SystemExit("Could not find the DEFAULTS block in index.html")
    html_path.write_text(new, encoding="utf-8")
    print("Synced index.html DEFAULTS from inputs.py:")
    print(f"  Group E winner: {', '.join(f'{k} {v}' for k, v in inp.p_E_win.items())}")


if __name__ == "__main__":
    main()
