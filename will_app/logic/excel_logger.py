import os
import openpyxl
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def log_to_excel(form_data, document_path=None):
    """
    Logs full will form data in flattened structure to Excel.
    Matches your old Google Sheets format exactly.
    """
    excel_file = "will_data_log.xlsx"

    # Full header layout (matches your old Google Sheets exactly)
    headers = [
        # Personal Information
        "name", "phone", "email", "gender", "dob",
        "street_number", "street_name", "city", "regional_municipality", "province", "postal_code",
        
        # Executors
        "exec1_name", "exec1_relation", "exec1_dob",
        "include_exec2", "exec2_name", "exec2_relation", "exec2_dob",
        
        # Wassiyat & Gifts
        "wassiyat_include", "wassiyat_percentage",
        "specific_gift_include", "specific_gift_text",
        "equal_shares"
    ]

    # Beneficiaries (1–50) - matches your old format
    for i in range(1, 51):
        headers += [f"relation{i}", f"name{i}", f"dob{i}", f"share{i}"]

    # POA & Mirror - matches your old format
    headers += [
        # General POA
        "include_poa",
        "poa_name_one", "poa_relation_one", "poa_dob_one",
        "poa_street_number_one", "poa_street_name_one", "poa_city_one",
        "poa_regional_municipality_one", "poa_province_one", "poa_postal_code_one",
        
        # Alternate POA
        "second_poa", "poa_name_two", "poa_relation_two", "poa_dob_two",
        "poa_street_number_two", "poa_street_name_two", "poa_city_two",
        "poa_regional_municipality_two", "poa_province_two", "poa_postal_code_two",
        
        # Personal Care POA
        "include_poa_personal_care", "poa_name_three", "poa_relation_three", "poa_dob_three",
        "poa_street_number_three", "poa_street_name_three", "poa_city_three",
        "poa_regional_municipality_three", "poa_province_three", "poa_postal_code_three",
        
        # Alternate Personal Care POA
        "second_poa_personal_care", "poa_name_four", "poa_relation_four", "poa_dob_four",
        "poa_street_number_four", "poa_street_name_four", "poa_city_four",
        "poa_regional_municipality_four", "poa_province_four", "poa_postal_code_four",
        
        # Mirror Will
        "mirror_will", "mirror_will_notes", "mirror_poa", "mirror_poa_care"
    ]

    # Create or open workbook
    if os.path.exists(excel_file):
        wb = openpyxl.load_workbook(excel_file)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(headers)

    # FIXED: Process beneficiaries from individual fields instead of list
    flat_beneficiaries = {}
    for i in range(1, 51):
        # Check if beneficiary exists (has at least name and relation)
        name = form_data.get(f"beneficiary_{i}_name")
        relation = form_data.get(f"beneficiary_{i}_relation")
        
        if name or relation:  # If either exists, include the beneficiary
            flat_beneficiaries[f"relation{i}"] = relation or ""
            flat_beneficiaries[f"name{i}"] = name or ""
            flat_beneficiaries[f"dob{i}"] = form_data.get(f"beneficiary_{i}_dob", "")
            flat_beneficiaries[f"share{i}"] = form_data.get(f"beneficiary_{i}_share", "")
        else:
            # Clear any previous data for this beneficiary slot
            flat_beneficiaries[f"relation{i}"] = ""
            flat_beneficiaries[f"name{i}"] = ""
            flat_beneficiaries[f"dob{i}"] = ""
            flat_beneficiaries[f"share{i}"] = ""

    # FIXED: Convert boolean values to "yes"/"no" like your old app
    processed_data = {}
    for key, value in form_data.items():
        if isinstance(value, bool):
            processed_data[key] = "yes" if value else "no"
        elif value is None:
            processed_data[key] = ""
        else:
            processed_data[key] = value

    # FIXED: Handle checkbox fields that might be missing
    checkbox_fields = [
        "include_exec2", "wassiyat_include", "specific_gift_include", "equal_shares",
        "include_poa", "second_poa", "include_poa_personal_care", "second_poa_personal_care",
        "mirror_will", "mirror_poa", "mirror_poa_care"
    ]
    
    for field in checkbox_fields:
        if field not in processed_data:
            processed_data[field] = "no"

    # Combine everything into one flat record
    flat_data = {**processed_data, **flat_beneficiaries}

    # Write row in header order
    row = []
    for h in headers:
        val = flat_data.get(h, "")
        # Ensure empty values are properly handled
        if val is None:
            val = ""
        row.append(str(val))

    ws.append(row)
    wb.save(excel_file)
    logger.info("✅ Logged structured data to Excel successfully")
    return True