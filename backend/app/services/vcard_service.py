"""
QRMaster Pro — RFC 6350 / v3.0 vCard Service.

Provides generation and parsing of vCard (.vcf) contacts conforming to RFC 2426 (v3.0)
and RFC 6350 (v4.0 compatibility) with support for names, organizations, phones,
emails, physical addresses, URLs, notes, and social media profiles.

Adheres strictly to the low-complexity standard (Cognitive Complexity <= 5 per function).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


def _escape_vcard_value(val: str) -> str:
    """Escape special characters per RFC standard."""
    if not val:
        return ""
    text = str(val)
    text = text.replace("\\", "\\\\")
    text = text.replace(";", r"\;")
    text = text.replace(",", r"\,")
    text = text.replace("\r\n", r"\n").replace("\r", r"\n").replace("\n", r"\n")
    return text


def _unescape_vcard_value(val: str) -> str:
    """Unescape special characters from raw vCard value."""
    if not val:
        return ""
    text = str(val)
    text = text.replace(r"\n", "\n").replace(r"\N", "\n")
    text = text.replace(r"\,", ",")
    text = text.replace(r"\;", ";")
    text = text.replace(r"\\", "\\")
    return text


def _fold_vcard_line(line: str, max_len: int = 75) -> str:
    """Fold line if longer than max_len according to RFC line folding specification."""
    if len(line) <= max_len:
        return line
    parts = []
    first_chunk = line[:max_len]
    parts.append(first_chunk)
    remaining = line[max_len:]
    while remaining:
        chunk = remaining[: max_len - 1]
        parts.append(" " + chunk)
        remaining = remaining[max_len - 1 :]
    return "\r\n".join(parts)


def _build_name_lines(data: Dict[str, Any]) -> List[str]:
    """Build N and FN lines for vCard."""
    first = _escape_vcard_value(data.get("first_name", "") or data.get("given_name", ""))
    last = _escape_vcard_value(data.get("last_name", "") or data.get("family_name", ""))
    middle = _escape_vcard_value(data.get("middle_name", "") or data.get("additional_name", ""))
    prefix = _escape_vcard_value(data.get("prefix", "") or data.get("name_prefix", ""))
    suffix = _escape_vcard_value(data.get("suffix", "") or data.get("name_suffix", ""))

    raw_fn = data.get("formatted_name") or data.get("full_name") or f"{first} {last}".strip()
    fn = _escape_vcard_value(raw_fn) if raw_fn else "Contact"

    n_val = f"{last};{first};{middle};{prefix};{suffix}"
    return [f"N:{n_val}", f"FN:{fn}"]


def _build_contact_lines(data: Dict[str, Any]) -> List[str]:
    """Build TEL, EMAIL, and URL lines."""
    lines: List[str] = []
    if data.get("cell_phone") or data.get("phone"):
        num = data.get("cell_phone") or data.get("phone")
        lines.append(f"TEL;TYPE=CELL,VOICE:{num}")
    if data.get("work_phone"):
        lines.append(f"TEL;TYPE=WORK,VOICE:{data['work_phone']}")
    if data.get("email"):
        lines.append(f"EMAIL;TYPE=INTERNET,PREF:{data['email']}")
    if data.get("work_email"):
        lines.append(f"EMAIL;TYPE=WORK:{data['work_email']}")
    if data.get("url"):
        lines.append(f"URL:{data['url']}")
    return lines


def _build_address_line(data: Dict[str, Any]) -> Optional[str]:
    """Build ADR line from component fields or generic address string."""
    street = _escape_vcard_value(data.get("street", ""))
    city = _escape_vcard_value(data.get("city", ""))
    state = _escape_vcard_value(data.get("state", ""))
    zip_code = _escape_vcard_value(data.get("postal_code", "") or data.get("zip_code", ""))
    country = _escape_vcard_value(data.get("country", ""))

    has_components = any([street, city, state, zip_code, country])
    if has_components:
        return f"ADR;TYPE=WORK:;;{street};{city};{state};{zip_code};{country}"

    if data.get("address"):
        addr = _escape_vcard_value(data["address"])
        return f"ADR;TYPE=WORK:;;{addr};;;;"
    return None


def _build_meta_lines(data: Dict[str, Any]) -> List[str]:
    """Build ORG, TITLE, ROLE, NOTE lines."""
    lines: List[str] = []
    if data.get("organization") or data.get("company"):
        org = _escape_vcard_value(data.get("organization") or data.get("company"))
        lines.append(f"ORG:{org}")
    if data.get("title") or data.get("job_title"):
        title = _escape_vcard_value(data.get("title") or data.get("job_title"))
        lines.append(f"TITLE:{title}")
    if data.get("role"):
        lines.append(f"ROLE:{_escape_vcard_value(data['role'])}")
    if data.get("note"):
        lines.append(f"NOTE:{_escape_vcard_value(data['note'])}")
    return lines


def _build_social_lines(data: Dict[str, Any]) -> List[str]:
    """Build social media profile lines."""
    lines: List[str] = []
    socials = data.get("social_links")
    if not isinstance(socials, dict):
        return lines
    for platform, url in socials.items():
        if url:
            lines.append(f"X-SOCIALPROFILE;TYPE={platform}:{url}")
    return lines


def _unfold_lines(text: str) -> List[str]:
    """Unfold wrapped lines starting with whitespace into their logical lines."""
    raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    unfolded: List[str] = []
    for line in raw_lines:
        if not line:
            continue
        if (line.startswith(" ") or line.startswith("\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
    return unfolded


def _parse_line(line: str) -> Optional[Tuple[str, Dict[str, str], str]]:
    """Parse a single logical vCard line into (prop_name, params_dict, value)."""
    if ":" not in line:
        return None
    header, value = line.split(":", 1)
    header_parts = header.split(";")
    prop_name = header_parts[0].upper().strip()
    params: Dict[str, str] = {}
    for param_token in header_parts[1:]:
        if "=" in param_token:
            k, v = param_token.split("=", 1)
            params[k.upper().strip()] = v.strip()
        else:
            params["TYPE"] = param_token.upper().strip()
    return prop_name, params, value


def _apply_name_field(result: Dict[str, Any], value: str) -> None:
    """Extract N components into first_name, last_name, etc."""
    parts = value.split(";")
    if len(parts) > 0 and parts[0]:
        result["last_name"] = _unescape_vcard_value(parts[0])
    if len(parts) > 1 and parts[1]:
        result["first_name"] = _unescape_vcard_value(parts[1])
    if len(parts) > 2 and parts[2]:
        result["middle_name"] = _unescape_vcard_value(parts[2])
    if len(parts) > 3 and parts[3]:
        result["prefix"] = _unescape_vcard_value(parts[3])
    if len(parts) > 4 and parts[4]:
        result["suffix"] = _unescape_vcard_value(parts[4])


def _apply_address_field(result: Dict[str, Any], value: str) -> None:
    """Extract ADR components."""
    parts = value.split(";")
    street = _unescape_vcard_value(parts[2]) if len(parts) > 2 else ""
    city = _unescape_vcard_value(parts[3]) if len(parts) > 3 else ""
    state = _unescape_vcard_value(parts[4]) if len(parts) > 4 else ""
    zip_code = _unescape_vcard_value(parts[5]) if len(parts) > 5 else ""
    country = _unescape_vcard_value(parts[6]) if len(parts) > 6 else ""

    result["street"] = street
    result["city"] = city
    result["state"] = state
    result["postal_code"] = zip_code
    result["country"] = country

    # Formatted address string
    addr_components = [c for c in [street, city, state, zip_code, country] if c]
    result["address"] = ", ".join(addr_components) if addr_components else street


def _assign_parsed_property(result: Dict[str, Any], prop: str, params: Dict[str, str], value: str) -> None:
    """Assign property to appropriate key in the result dictionary."""
    if prop == "FN":
        result["formatted_name"] = _unescape_vcard_value(value)
    elif prop == "N":
        _apply_name_field(result, value)
    elif prop == "ORG":
        result["organization"] = _unescape_vcard_value(value.split(";")[0])
    elif prop == "TITLE":
        result["title"] = _unescape_vcard_value(value)
    elif prop == "ROLE":
        result["role"] = _unescape_vcard_value(value)
    elif prop == "TEL":
        _assign_phone(result, params, value)
    elif prop == "EMAIL":
        _assign_email(result, params, value)
    elif prop == "URL":
        result["url"] = value.strip()
    elif prop == "ADR":
        _apply_address_field(result, value)
    elif prop == "NOTE":
        result["note"] = _unescape_vcard_value(value)
    elif prop == "X-SOCIALPROFILE":
        platform = params.get("TYPE", "other").lower()
        result.setdefault("social_links", {})[platform] = value.strip()


def _assign_phone(result: Dict[str, Any], params: Dict[str, str], value: str) -> None:
    """Assign phone with cellular/work awareness."""
    num = value.strip()
    ptype = params.get("TYPE", "").upper()
    if "WORK" in ptype:
        result["work_phone"] = num
    else:
        result["phone"] = num
    result.setdefault("phones", []).append({"type": ptype or "VOICE", "number": num})


def _assign_email(result: Dict[str, Any], params: Dict[str, str], value: str) -> None:
    """Assign email with work awareness."""
    mail = value.strip()
    etype = params.get("TYPE", "").upper()
    if "WORK" in etype:
        result["work_email"] = mail
    else:
        result["email"] = mail
    result.setdefault("emails", []).append({"type": etype or "INTERNET", "email": mail})


class VCardService:
    """Service for RFC 6350 / v3.0 VCF generation, parsing, and export."""

    def generate(self, data: Dict[str, Any]) -> str:
        """
        Generate standard RFC vCard 3.0 string.
        Folds long lines per specification.
        """
        raw_lines: List[str] = ["BEGIN:VCARD", "VERSION:3.0"]
        raw_lines.extend(_build_name_lines(data))
        raw_lines.extend(_build_meta_lines(data))
        raw_lines.extend(_build_contact_lines(data))

        adr_line = _build_address_line(data)
        if adr_line:
            raw_lines.append(adr_line)

        raw_lines.extend(_build_social_lines(data))
        raw_lines.append("END:VCARD")

        folded_lines = [_fold_vcard_line(line) for line in raw_lines]
        return "\r\n".join(folded_lines)

    def parse(self, vcf_text: str) -> Dict[str, Any]:
        """
        Parse a RFC 2426/6350 vCard text into a clean dictionary.
        Handles folded lines and character unescaping.
        """
        if not vcf_text or not isinstance(vcf_text, str):
            return {}

        result: Dict[str, Any] = {
            "first_name": "",
            "last_name": "",
            "formatted_name": "",
            "organization": "",
            "title": "",
            "phone": "",
            "email": "",
            "url": "",
            "address": "",
            "note": "",
            "social_links": {},
        }

        unfolded = _unfold_lines(vcf_text)
        for line in unfolded:
            parsed = _parse_line(line)
            if not parsed:
                continue
            prop, params, val = parsed
            _assign_parsed_property(result, prop, params, val)

        if not result["formatted_name"]:
            first = result.get("first_name", "")
            last = result.get("last_name", "")
            result["formatted_name"] = f"{first} {last}".strip()

        return result


# Singleton instance
vcard_service = VCardService()
