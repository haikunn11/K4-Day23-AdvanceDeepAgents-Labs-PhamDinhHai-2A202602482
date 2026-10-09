"""research.py - STUDENT IMPLEMENTS.  The main script.   Guide: GUIDE.md, part 3.

Usage:  python research.py "survey about world model"
Result: reports/<slug>.md   reports/<slug>.sources.json   reports/<slug>.meta.json
"""
import json  # noqa: F401
import os  # noqa: F401
import re  # noqa: F401
import sys
import time  # noqa: F401
from collections import Counter  # noqa: F401
from pathlib import Path

from agents import FINALIZER_PATH, NORMALIZER_PATH, REPORT_PATH, SOURCES_PATH, VALIDATOR_PATH, WORKDIR, build_lead_agent
from model import make_model  # noqa: F401
from sandbox import download, open_sandbox, upload  # noqa: F401

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
VALIDATOR_SOURCE = ROOT / "check_citations.py"
FINALIZER_SOURCE = ROOT / "finalize_citations.py"   # provided: uploaded next to your validator
NORMALIZER_SOURCE = ROOT / "normalize_sources.py"


def slugify(topic):
    """Turn a topic into a safe file name: lower case, runs of non-word characters become one "-", max 60 chars,
    never empty (fall back to "topic"). The topic is user input: "../../x" must not escape reports/."""
    value = re.sub(r"[^\w]+", "-", str(topic or "").lower(), flags=re.UNICODE).strip("-_")
    value = value[:60].rstrip("-_")
    return value or "topic"


def build_prompt(topic):
    """The user message sent to the lead agent."""
    return (f"Produce a rigorous deep-research survey about: {topic.strip()}\n"
            "Follow your full workflow, use at least three researcher tasks and at least three source families, "
            "validate citations, and leave the final artifacts at the required sandbox paths.")


def summarize(messages, elapsed, model_name):
    """Return {"model", "elapsed_s", "subagent_calls", "tool_calls": {name: count}, "tokens": {"input", "output"}}.

    PSEUDO-CODE: walk the lead's messages; for every message with tool_calls count call["name"] (subagent_calls = the
    count of "task"); add the input/output token counts from each message's usage_metadata when present.
    (Lead messages only: subagent tokens are not included, so this undercounts the real cost.)
    elapsed_s rounded to 0.1.
    """
    counts = Counter()
    input_tokens = output_tokens = 0
    for message in messages or []:
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls is None and isinstance(message, dict):
            tool_calls = message.get("tool_calls") or message.get("additional_kwargs", {}).get("tool_calls")
        for call in tool_calls or []:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
            if name:
                counts[name] += 1
        usage = getattr(message, "usage_metadata", None)
        if usage is None and isinstance(message, dict):
            usage = message.get("usage_metadata")
        usage = usage or {}
        input_tokens += int(usage.get("input_tokens", usage.get("prompt_tokens", 0)) or 0)
        output_tokens += int(usage.get("output_tokens", usage.get("completion_tokens", 0)) or 0)
    return {"model": model_name, "elapsed_s": round(elapsed, 1), "subagent_calls": counts.get("task", 0),
            "tool_calls": dict(sorted(counts.items())),
            "tokens": {"input": input_tokens, "output": output_tokens}}


def save_outputs(backend, topic, messages, elapsed, model_name, reports_dir=REPORTS):
    """Download the report from the sandbox and write the three files into reports_dir. Return the report path.

    PSEUDO-CODE:
      files = download(backend, [REPORT_PATH, SOURCES_PATH])
      if the report is missing/empty or sources.json is missing/invalid JSON: raise RuntimeError and WRITE NOTHING
          (a failed run must never leave an empty or half-written report behind)
      write <slug>.sources.json, <slug>.meta.json (topic + summarize(...) + n_sources + source_families: the sorted
      distinct "source" values of sources.json) and <slug>.md
    """
    files = download(backend, [REPORT_PATH, SOURCES_PATH])
    report_data, sources_data = files.get(REPORT_PATH), files.get(SOURCES_PATH)
    if not report_data or not report_data.strip():
        raise RuntimeError("sandbox did not produce a non-empty report")
    if not sources_data:
        raise RuntimeError("sandbox did not produce sources.json")
    try:
        sources = json.loads(sources_data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RuntimeError(f"invalid sources.json: {exc}") from exc
    if not isinstance(sources, list) or not sources:
        raise RuntimeError("sources.json must be a non-empty JSON list")
    if not all(isinstance(source, dict) for source in sources):
        raise RuntimeError("sources.json contains a non-object entry")

    reports_dir.mkdir(parents=True, exist_ok=True)
    stem = slugify(topic)
    report_path = reports_dir / f"{stem}.md"
    sources_path = reports_dir / f"{stem}.sources.json"
    meta_path = reports_dir / f"{stem}.meta.json"
    meta = {"topic": topic, **summarize(messages, elapsed, model_name), "n_sources": len(sources),
            "source_families": sorted({str(s.get("source")) for s in sources if s.get("source")})}
    payloads = {
        report_path: report_data,
        sources_path: (json.dumps(sources, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        meta_path: (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    }
    temporary = []
    try:
        for path, data in payloads.items():
            temp = path.with_name(path.name + ".tmp")
            temp.write_bytes(data)
            temporary.append((temp, path))
        for temp, path in temporary:
            temp.replace(path)
    finally:
        for temp, _ in temporary:
            if temp.exists():
                temp.unlink()
    return report_path


def main(topic):
    """Return the process exit code (0 ok, 1 failed run, 2 no topic).

    PSEUDO-CODE:
      empty topic -> print usage to stderr, return 2
      model = make_model(); start = time.monotonic()
      with open_sandbox() as backend:                # the sandbox is always cleaned up, even on errors
          backend.execute("mkdir -p <WORKDIR>/research/notes <WORKDIR>/report")
          upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(), FINALIZER_PATH: FINALIZER_SOURCE.read_bytes()})
          agent = build_lead_agent(backend, model)
          result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                config={"recursion_limit": 1000})
          save_outputs(...); on RuntimeError print "FAILED: ..." to stderr and return 1
      print where the report was saved; return 0
    """
    topic = str(topic or "").strip()
    if not topic:
        print('Usage: python research.py "<topic>"', file=sys.stderr)
        return 2
    try:
        model = make_model()
        model_name = (getattr(model, "model_name", None) or getattr(model, "model", None)
                      or os.getenv("LAB_MODEL") or type(model).__name__)
        started = time.monotonic()
        with open_sandbox() as backend:
            setup = backend.execute(f"mkdir -p {WORKDIR}/research/notes {WORKDIR}/report")
            if getattr(setup, "exit_code", 1) != 0:
                raise RuntimeError(f"cannot prepare sandbox: {getattr(setup, 'output', '')}")
            upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(),
                             FINALIZER_PATH: FINALIZER_SOURCE.read_bytes(),
                             NORMALIZER_PATH: NORMALIZER_SOURCE.read_bytes()})
            agent = build_lead_agent(backend, model)
            result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                  config={"recursion_limit": 1000})
            messages = result.get("messages", []) if isinstance(result, dict) else []
            path = save_outputs(backend, topic, messages, time.monotonic() - started, str(model_name))
        print(f"Saved report: {path}")
        return 0
    except Exception as exc:  # failed runs must be explicit and leave no empty output
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(" ".join(sys.argv[1:])))
