"""Canonicalize source URLs inside the sandbox before citation finalization."""
import json
import re
import sys

SOURCES = "/tmp/work/research/sources.json"


def normalize(sources):
    if not isinstance(sources, list):
        raise ValueError("sources.json must be a list")
    result = []
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("every source must be an object")
        item = dict(source)
        family = item.get("source")
        paper_id = str(item.get("id") or "").strip()
        paper_id = re.sub(r"v\d+$", "", paper_id.split("/")[-1])
        if family == "arxiv" and paper_id:
            item["id"] = paper_id
            item["url"] = f"https://arxiv.org/abs/{paper_id}"
        elif family in {"hf-daily", "hf-search"} and paper_id:
            item["id"] = paper_id
            item["url"] = f"https://huggingface.co/papers/{paper_id}"
        result.append(item)
    return result


def main(argv):
    path = argv[1] if len(argv) > 1 else SOURCES
    try:
        with open(path, encoding="utf-8") as handle:
            sources = json.load(handle)
        normalized = normalize(sources)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(normalized, handle, ensure_ascii=False, indent=2)
        print(f"NORMALIZED: {len(normalized)} sources")
        return 0
    except (OSError, ValueError) as exc:
        print(f"cannot normalize sources: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
