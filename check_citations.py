"""check_citations.py - STUDENT IMPLEMENTS `check`.   Runs INSIDE the sandbox (standard library only).

research.py uploads this file to the sandbox and the lead agent runs it with the `execute` tool:
    python3 /tmp/work/research/check_citations.py [report.md] [sources.json]
It must exit 0 and print "OK: ..." when the report is consistent, else print each problem and exit 1.
"""
import json
import re
import sys

REPORT = "/tmp/work/report/report.md"
SOURCES = "/tmp/work/research/sources.json"


def check(report_text, sources):
    """Return a list of problem strings (empty list = OK).

    PSEUDO-CODE:
      problems = []
      if sources is empty: return ["no sources in sources.json"]
      for each source entry:
          n must be an int                       -> problem if not
          url must start with http:// or https://-> problem if not
          the same url must not appear twice     -> problem if duplicated
      split report_text at the heading "## References":
          body = text before it; if the heading is missing -> problem
      cited = set of numbers found as [n] in the BODY only (not in the reference list; use a regex)
      every number in `cited` must exist in sources -> problem "[n] cited but missing from sources.json"
      every source number must be in `cited`        -> problem "source [n] never cited"
      the lines of the References section that start with "[n]" (regex) are the reference lines:
          every source needs exactly ONE reference line (none missing, no number twice, no number that is not a source)
          each reference line holds exactly ONE http(s) URL and it must equal that source's url
          (a line bundling several sources under one number is a problem)
      return problems
    """
    problems = []
    if not isinstance(sources, list) or not sources:
        return ["no sources in sources.json"]
    by_n, seen_urls = {}, {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            problems.append(f"source at index {index} is not an object")
            continue
        n, url = source.get("n"), source.get("url")
        if not isinstance(n, int) or isinstance(n, bool):
            problems.append(f"source at index {index} has non-integer n")
        elif n in by_n:
            problems.append(f"source number [{n}] is duplicated")
        else:
            by_n[n] = source
        if not isinstance(url, str) or not re.match(r"^https?://", url):
            problems.append(f"source [{n}] has invalid url")
        elif url in seen_urls:
            problems.append(f"url duplicated in sources [{seen_urls[url]}] and [{n}]")
        else:
            seen_urls[url] = n
        family = source.get("source")
        if family not in {"arxiv", "hf-daily", "hf-search", "web"}:
            problems.append(f"source [{n}] has invalid source family")
        elif family == "arxiv" and not str(url).startswith("https://arxiv.org/abs/"):
            problems.append(f"source [{n}] labeled arxiv must use an https://arxiv.org/abs/ URL")
        elif family in {"hf-daily", "hf-search"} and not str(url).startswith("https://huggingface.co/papers/"):
            problems.append(f"source [{n}] labeled {family} must use a Hugging Face papers URL")

    headings = list(re.finditer(r"(?m)^##[ \t]+References[ \t]*$", report_text))
    if not headings:
        problems.append("missing ## References heading")
        body, references = report_text, ""
    else:
        body = report_text[:headings[-1].start()]
        references = report_text[headings[-1].end():]
    body = re.sub(r"```.*?```|`[^`\n]*`", "", body, flags=re.S)
    body = re.sub(r"\[[^\]\n]+\]\([^\n)]*\)", "", body)
    cited = set()
    for match in re.finditer(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\](?!\()", body):
        for part in re.split(r"\s*,\s*", match.group(1)):
            span = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
            if span:
                start, end = map(int, span.groups())
                cited.update(range(start, end + 1) if 0 <= end - start <= 200 else (start, end))
            else:
                cited.add(int(part))
    for n in sorted(cited - set(by_n)):
        problems.append(f"[{n}] cited but missing from sources.json")
    for n in sorted(set(by_n) - cited):
        problems.append(f"source [{n}] never cited")

    ref_lines = {}
    for line in references.splitlines():
        match = re.match(r"^\[(\d+)\]\s+", line.strip())
        if match:
            ref_lines.setdefault(int(match.group(1)), []).append(line.strip())
    for n in sorted(set(ref_lines) - set(by_n)):
        problems.append(f"reference [{n}] has no source")
    for n, source in sorted(by_n.items()):
        lines = ref_lines.get(n, [])
        if not lines:
            problems.append(f"source [{n}] has no reference line")
            continue
        if len(lines) != 1:
            problems.append(f"source [{n}] has {len(lines)} reference lines")
            continue
        urls = re.findall(r"https?://[^\s)>]+", lines[0])
        if len(urls) != 1:
            problems.append(f"reference [{n}] must contain exactly one URL")
        elif urls[0] != source.get("url"):
            problems.append(f"reference [{n}] URL does not match sources.json")
    return problems


def main(argv):
    report_path = argv[1] if len(argv) > 1 else REPORT
    sources_path = argv[2] if len(argv) > 2 else SOURCES
    try:
        with open(report_path, encoding="utf-8") as f:
            report = f.read()
        with open(sources_path, encoding="utf-8") as f:
            sources = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"cannot read inputs: {exc}")
        return 1
    problems = check(report, sources)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(sources)} sources, all citations resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
