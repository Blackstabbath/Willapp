# logic/beneficiaries.py
from helpers.formatters import format_date, title_case, safe_bool, safe_float

MAX_BENEFICIARIES = 50  # future-proof; UI caps at 10

def process_beneficiaries_data(form_data: dict) -> dict:
    """
    Normalizes all beneficiary inputs and prepares context
    expected by the Word template.
    """
    beneficiaries = []

    # --- Collect all ---
    for i in range(1, MAX_BENEFICIARIES + 1):
        name = form_data.get(f"beneficiary_{i}_name")
        relation = form_data.get(f"beneficiary_{i}_relation")
        dob = form_data.get(f"beneficiary_{i}_dob")
        share_raw = form_data.get(f"beneficiary_{i}_share")

        if name and relation and dob:
            beneficiaries.append({
                "relation": title_case(relation or ""),
                "name": title_case(name or ""),
                "dob": format_date(dob or ""),
                "share": safe_float(share_raw, 0.0)
            })

    has_beneficiaries = len(beneficiaries) > 0
    equal = safe_bool(form_data.get("equal_shares"))

    # --- Equal share logic ---
    if equal and has_beneficiaries:
        share_value = round(100.0 / len(beneficiaries), 2)
        for b in beneficiaries:
            b["share"] = share_value
    else:
        total = sum(b["share"] for b in beneficiaries)
        if total <= 0 and has_beneficiaries:
            share_value = round(100.0 / len(beneficiaries), 2)
            for b in beneficiaries:
                b["share"] = share_value

    # --- Convert shares to strings for template display ---
    for b in beneficiaries:
        b["share"] = f"{b['share']:.2f}"

    # --- Return full context including equal_shares flag ---
    return {
        "beneficiaries": beneficiaries,
        "has_beneficiaries": has_beneficiaries,
        "equal_shares": equal
    }
