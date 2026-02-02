# helpers/formatters.py
from datetime import datetime

def title_case(s: str) -> str:
    if not s:
        return ""
    return " ".join(part.capitalize() for part in str(s).strip().split())

def format_date(d: str) -> str:
    """
    Accepts 'YYYY-MM-DD' or anything truthy; returns readable '01 Feb 1990'.
    If invalid, returns as-is.
    """
    if not d:
        return ""
    try:
        # Accept 'YYYY-MM-DD' and 'YYYY-MM-DD 00:00:00'
        d = str(d).strip().split(" ")[0]
        dt = datetime.strptime(d, "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(d)

def format_address(parts: dict) -> str:
    """
    Expects keys: street_number, street_name, city, regional_municipality, province, postal_code
    Concise single-line address
    """
    if not parts:
        return ""
    items = []
    snum = parts.get("street_number")
    sname = parts.get("street_name")
    city = parts.get("city")
    rm = parts.get("regional_municipality")
    prov = parts.get("province")
    pc = parts.get("postal_code")

    # street number + name
    street = " ".join([str(snum or "").strip(), str(sname or "").strip()]).strip()
    if street:
        items.append(title_case(street))

    for x in [city, rm, prov]:
        if x:
            items.append(title_case(x))

    if pc:
        items.append(str(pc).upper())

    return ", ".join([i for i in items if i])

def safe_bool(v):
    if v in [True, "True", "true", "1", 1, "yes", "Yes", "on", "On"]:
        return True
    return False

def safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return float(default)
