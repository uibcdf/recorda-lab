"""Offline check for the component's minimal MOLI surface and local report metadata."""

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPEN = {"open", "active", "blocked", "partial"}
CLOSED = {"resolved", "withdrawn", "superseded"}
EVIDENCE = {"asserted", "inspected", "reproduced", "measured", "upstream"}


def validate(root=ROOT):
    errors = []
    for relative in (
        "AGENTS.md",
        "MOLI_GUIDE.md",
        "devguide/reporting_protocol.md",
        "devguide/pending_bugs/README.md",
        "devguide/pending_proposals/README.md",
        "devguide/archive/README.md",
        "devguide/templates/report.md",
    ):
        if not (root / relative).is_file():
            errors.append(f"{relative}: missing")
    if (root / "AGENTS.md").is_file() and "MOLI_GUIDE.md" not in (root / "AGENTS.md").read_text():
        errors.append("AGENTS.md: must require MOLI_GUIDE.md")
    for queue, archived in (
        ("pending_bugs", False),
        ("pending_proposals", False),
        ("archive", True),
    ):
        for path in (root / "devguide" / queue).glob("*.md"):
            if path.name == "README.md":
                continue
            text = path.read_text()
            if not text.startswith("---\n") or "\n---\n" not in text[4:]:
                errors.append(f"{path.name}: missing front matter")
                continue
            header = text[4:].split("\n---\n", 1)[0]
            data = dict(line.split(":", 1) for line in header.splitlines() if ":" in line)
            data = {key.strip(): value.strip() for key, value in data.items()}
            if not re.fullmatch(r"uibcdf/[\w.-]+#[1-9][0-9]*", data.get("issue", "")):
                errors.append(f"{path.name}: invalid issue")
            if data.get("status") not in (CLOSED if archived else OPEN):
                errors.append(f"{path.name}: invalid queue status")
            if data.get("verification") not in EVIDENCE:
                errors.append(f"{path.name}: invalid evidence state")
            if not data.get("summary"):
                errors.append(f"{path.name}: missing summary")
            for field in ("opened", "closed") if archived else ("opened",):
                try:
                    date.fromisoformat(data.get(field, ""))
                except ValueError:
                    errors.append(f"{path.name}: invalid {field} date")
    return errors


if __name__ == "__main__":
    findings = validate()
    print("\n".join(findings) if findings else "Local MOLI governance surface passes.")
    raise SystemExit(bool(findings))
