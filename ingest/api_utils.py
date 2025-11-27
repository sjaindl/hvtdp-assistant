from typing import List, Dict, Any, Iterable
import json
import re

from utils.summarizer import summarize_text


def _is_primitive(x: Any) -> bool:
    return isinstance(x, (str, int, float, bool, type(None)))

def _flatten(obj: Any, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """
    Flatten dicts/lists into a {dot.path: value} mapping for summarization.
    Lists are represented as path[index]. For schema, we don't use indices later.
    """
    items: Dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(_flatten(v, new_key, sep=sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}[{i}]"
            items.update(_flatten(v, new_key, sep=sep))
    else:
        items[parent_key] = obj
    return items

def _remove_excluded(obj: Any, exclude_paths: Iterable[str], path: str = "") -> Any:
    """
    Return a deep-copied version of obj with any dict keys removed whose full dot-path matches
    an exclude in exclude_paths. Excludes can be top-level ("email") or dot paths ("user.email").
    """
    exclude_set = set(exclude_paths or [])
    # quick check for direct match on current object path (mainly for entire object removal)
    if path and path in exclude_set:
        return None

    if isinstance(obj, dict):
        new_d = {}
        for k, v in obj.items():
            child_path = f"{path}.{k}" if path else k
            if k in exclude_set or child_path in exclude_set:
                continue
            cleaned = _remove_excluded(v, exclude_set, child_path)
            if cleaned is not None:
                new_d[k] = cleaned
        return new_d
    elif isinstance(obj, list):
        new_l = []
        for i, v in enumerate(obj):
            child_path = f"{path}[{i}]" if path else f"[{i}]"
            cleaned = _remove_excluded(v, exclude_set, child_path)
            if cleaned is not None:
                new_l.append(cleaned)
        return new_l
    else:
        return obj

def _infer_type(value: Any) -> str:
    if isinstance(value, bool): return "bool"
    if isinstance(value, int): return "int"
    if isinstance(value, float): return "float"
    if isinstance(value, str): return "str"
    if value is None: return "null"
    if isinstance(value, list): return f"list[{_infer_type(value[0])}]" if value else "list"
    if isinstance(value, dict): return "object"
    return type(value).__name__

def _build_description(data: Any, exclude_paths: Iterable[str]) -> List[str]:
    """
    Build a textual field description by sampling keys/types across records.
    For lists of objects, we aggregate across items. For dicts, we inspect keys.
    Excluded paths are ignored.
    """
    cleaned = _remove_excluded(data, exclude_paths)
    samples: Dict[str, List[Any]] = {}

    _BRACKET_INDEX_RE = re.compile(r"\[\d+]")

    def _normalize_bracket_indices(key: str) -> str:
        """Turn any numeric bracket index like [0], [12] into [] once."""
        return _BRACKET_INDEX_RE.sub("[]", key)

    def add_sample(obj: Any):
        flat = _flatten(obj)
        for k, v in flat.items():
            norm_k = _normalize_bracket_indices(k)
            samples.setdefault(norm_k, []).append(v)

    if isinstance(cleaned, list):
        for item in cleaned[:200]:  # cap sampling
            add_sample(item)
    else:
        add_sample(cleaned)

    lines = []
    for k in sorted(samples.keys()):
        vals = samples[k]
        # infer dominant type
        type_counts: Dict[str, int] = {}
        for v in vals:
            t = _infer_type(v)
            type_counts[t] = type_counts.get(t, 0) + 1
        dominant_type = max(type_counts.items(), key=lambda kv: kv[1])[0]
        # example
        example = None
        for v in vals:
            if _is_primitive(v) and v not in (None, "", []):
                example = v
                break
        ex_str = f' (e.g., "{example}")' if isinstance(example, str) else (f" (e.g., {example})" if example is not None else "")
        lines.append(f"- {k}: {dominant_type}{ex_str}")
    return lines

def _record_iter(data: Any) -> Iterable[Any]:
    """Yield 'records' for rendering. If list -> each element; else -> the dict/primitive itself."""
    if isinstance(data, list):
        return data
    return [data]

def _format_record_to_text(rec: Any, summarize: bool, exclude_paths: Iterable[str]) -> str:
    """
    Turn a record (usually dict) into human-readable text lines, honoring excluded fields.
    - Top-level dict => key: value lines (with shallow dot paths for nested dicts).
    - Non-dict => str(rec).
    """
    rec_clean = _remove_excluded(rec, exclude_paths)
    if isinstance(rec_clean, dict):
        # show top-level fields; for nested dicts/lists, show a compact JSON string
        lines: List[str] = []
        for k in sorted(rec_clean.keys()):
            v = rec_clean[k]
            if isinstance(v, (dict, list)):
                # compact one-line JSON for nested structures
                compact = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
                lines.append(f"{k}: {compact}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)
    else:
        return summarize_text(str(rec_clean)) if summarize else str(rec_clean)
