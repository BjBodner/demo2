"""Parse '## Idea atoms' and '## Open problems / gaps' sections of the corpus markdown into JSON."""
import json, re, sys
from pathlib import Path

corpus = Path(sys.argv[1]); out = Path(sys.argv[2])
atoms, gaps = [], []
for f in sorted(corpus.glob("*.md")):
    text = f.read_text()
    sec = re.split(r"^## ", text, flags=re.M)
    for s in sec:
        head = s.split("\n", 1)[0].lower()
        body = s.split("\n", 1)[1] if "\n" in s else ""
        if head.startswith("idea atoms"):
            for m in re.finditer(r"^\d+\.\s+(.*?)(?=^\d+\.\s|\Z)", body, flags=re.M | re.S):
                t = " ".join(m.group(1).split())
                t = re.sub(r"\s*\[[^\]]*\]\s*$", "", t)            # drop trailing source tag
                t = re.sub(r"\*\*(.*?)\*\*", r"\1", t)
                atoms.append({"source_file": f.name, "text": t})
        elif head.startswith("open problems"):
            for m in re.finditer(r"^- (.*?)(?=^- |^\*\*|\Z)", body, flags=re.M | re.S):
                t = " ".join(m.group(1).split()); t = re.sub(r"\*\*(.*?)\*\*", r"\1", t)
                if len(t) > 40:
                    gaps.append({"source_file": f.name, "text": t})
out.write_text(json.dumps({"atoms": atoms, "gaps": gaps}, indent=1))
print(len(atoms), "atoms,", len(gaps), "gaps")
