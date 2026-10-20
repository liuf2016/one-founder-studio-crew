"""Tools shared by the crew: Cognee memory, a sandboxed workspace, and Snyk."""
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import cognee
from langchain_core.tools import tool

DATASET = "studio_memory"
WORKSPACE = (Path(__file__).resolve().parent.parent / "workspace").resolve()


def _safe(path: str) -> Path:
    p = (WORKSPACE / path).resolve()
    if WORKSPACE not in p.parents and p != WORKSPACE:
        raise ValueError("path escapes workspace")
    return p


@tool
async def remember(note: str) -> str:
    """Store a durable fact in the team's shared Cognee memory: a decision, a review finding,
    a vulnerability pattern and its fix, or a codebase convention. Write full self-contained sentences."""
    await cognee.add(note, dataset_name=DATASET)
    await cognee.cognify([DATASET])
    return "Stored in shared memory."


@tool
async def recall(question: str) -> str:
    """Ask the team's shared Cognee memory what is known about a topic (past decisions,
    review findings, vulnerabilities and their fixes). Call this BEFORE planning or writing code."""
    try:
        results = await cognee.search(question, datasets=[DATASET])
    except Exception as e:  # empty memory raises before the first remember
        return f"No memory yet ({type(e).__name__})."
    return "\n".join(str(r) for r in results) or "Nothing relevant in memory."


@tool
def write_file(path: str, content: str) -> str:
    """Write a file in the project workspace (path relative to the workspace root)."""
    p = _safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {path} ({len(content)} bytes)"


@tool
def read_file(path: str) -> str:
    """Read a file from the project workspace. Use path '.' to list files."""
    p = _safe(path)
    if p.is_dir():
        return "\n".join(str(f.relative_to(WORKSPACE)) for f in sorted(p.rglob("*")) if f.is_file())
    return p.read_text()


@tool
def snyk_scan() -> str:
    """Run Snyk security scans over the project workspace: Snyk Code (source) and Snyk Open Source
    (dependencies in requirements.txt). Returns the findings."""
    out = []
    for label, cmd in (
        ("SNYK CODE", ["snyk", "code", "test", str(WORKSPACE)]),
        ("SNYK OPEN SOURCE", ["snyk", "test", f"--file={WORKSPACE / 'requirements.txt'}", "--package-manager=pip"]),
    ):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=170, cwd=WORKSPACE)
            out.append(f"== {label} ==\n" + (r.stdout + r.stderr)[-1800:])
        except Exception as e:
            out.append(f"== {label} == failed: {e}")
    return "\n".join(out)
