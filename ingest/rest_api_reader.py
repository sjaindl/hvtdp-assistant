from dataclasses import dataclass, field
from typing import List, Dict, Any, Iterable
import requests
from llama_index.core import Document
import json
import re

@dataclass
class EndpointSpec:
    """Configuration for a single REST endpoint."""
    url: str
    exclude_fields: List[str] = field(default_factory=list)  # supports dot paths, e.g. "user.email", "items.price"
    description: str = ""

specs = [
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getChefs.php",
        exclude_fields= ["imagePath"],
        description= "Liste an Vereinsfunktionären"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getActiveMembership.php",
        exclude_fields= [""],
        description= "Liste an aktiven Vereinsmitgliedern zum Stichtag"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getSupportMembership.php",
        exclude_fields= [""],
        description= "Liste an fördernden Vereinsmitgliedern zum Stichtag"
    ),


    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getSquadPlayers.php",
        exclude_fields= ["imagePath"],
        description= "Übersicht aller Spieler im Meisterschaftskader: Gespielte Position, Beitrittsdatum und Namen"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getActivePlayers.php",
        exclude_fields= ["imagePath"],
        description= "Übersicht der weiteren aktiven Vereinsmitglieder, die nicht mehr im Meisterschaftskader sind: Gespielte Position, Beitrittsdatum und Namen"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getDonations.php",
        exclude_fields= ["imagePath, matchBallImagePath"],
        description= "Übersicht der Matchballspenden an den Verein inkl. Spender, das gesponserte Spiel und Datum"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getPhotos.php",
        exclude_fields= ["photos, albumId"],
        description= "Übersicht der Vereinsveranstaltungen mit Saison und Datum"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getGames.php",
        exclude_fields= ["links.goalOfSeasonCandidate"],
        description= "Übersicht aller Spiele des HV TDP pro Saison inkl. Ergebnisse und Torschützen mit Videolink"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getScorers.php",
        exclude_fields= [""],
        description= "Zusammengefasste Liste mit Summe der Tore pro Spieler und Saison"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getTicker.php",
        exclude_fields= [""],
        description= "Das nächste wichtige Event des HV TDP Stainz"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getGoalOfTheSeason.php",
        exclude_fields= [""],
        description= "Das Umfrageergebnis der Wahl zum Tor der Saison 2024 mit genauen Stimmanzahlen"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getPlayerOfTheSeason.php",
        exclude_fields= [""],
        description= "Das Umfrageergebnis der Wahl zum Spieler der Saison 2024 mit genauen Stimmanzahlen"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getItems.php",
        exclude_fields= ["imagePath"],
        description= "Das Sortiment aus dem Fanshop des HV TDP Stainz"
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getNews.php",
        exclude_fields= ["imagePath, imagePathHome"],
        description= "Alle News des HV TDP Stainz. Entweder als plain news oder htmlNews."
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getPappfans.php",
        exclude_fields= ["imagePath"],
        description= "Zur Zeit von COVID waren keine Fans im Stadion erlaubt, aber es war möglich Pappfiguren zu erwerben und als Fans auf der Tribüne zu platzieren. Hier ist die Liste der Käufer der Pappfans."
    ),
    EndpointSpec(
        url = "https://www.hvtdpstainz.at/api/getStandings.php",
        exclude_fields= [""],
        description= "Die Platzierungen aller Mannschaften mit Anzahl der Siege, Niederlagen, Unentschieden, Punkte, Anzahl der Spiele und der Tordifferenz pro Saison."
    ),
]

# -------- Helpers --------

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
    # quick check for direct match on current object path (rare; mainly for entire object removal)
    if path and path in exclude_set:
        return None  # parent should drop this

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

def _summarize_fields(data: Any, exclude_paths: Iterable[str]) -> List[str]:
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

def _format_record_to_text(rec: Any, exclude_paths: Iterable[str]) -> str:
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
        return str(rec_clean)

# -------- Main loaders --------

def load_api_data(spec: EndpointSpec) -> Document:
    """Load a single endpoint into a LlamaIndex Document with schema summary and readable content."""
    resp = requests.get(spec.url)
    resp.raise_for_status()
    data = resp.json()

    # Field summary (schema-ish)
    field_lines = _summarize_fields(data, spec.exclude_fields)

    # Human-readable body
    records_text: List[str] = []
    for rec in _record_iter(data):
        records_text.append(_format_record_to_text(rec, spec.exclude_fields))

    text = (
            f"Source: {spec.url}\n"
            f"Description: {spec.description}\n\n"
            f"Field Summary:\n" + "\n".join(field_lines) + "\n\n"
            f"Data:\n" + "\n\n---\n\n".join(records_text)
    )

    cleaned_json = _remove_excluded(data, spec.exclude_fields)
    metadata = {
        "source": spec.url,
        "endpoint_description": spec.description,
        #"excluded_fields": list(spec.exclude_fields),
        "record_count": len(cleaned_json) if isinstance(cleaned_json, list) else 1,
       # "schema_fields": field_lines,  # handy for filtering/inspection later
        #"raw_json": cleaned_json, # Keep raw JSON (pruned) in metadata for programmatic use
    }

    return Document(text=text, metadata=metadata)

def load_api_endpoints(specs: List[EndpointSpec]) -> List[Document]:
    """Load many endpoints and return a flat list of Documents."""
    docs: List[Document] = []
    for spec in specs:
        doc = load_api_data(spec)
        docs.append(doc)
    return docs
