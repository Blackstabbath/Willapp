""" helpers/validators.py Centralized validation logic for Absolute Wills application """

def validate_beneficiaries_shares(form_data):
    """ Validate that beneficiary shares add to exactly 100% Allows for equal shares toggle """
    try:
        # If equal shares are enabled, skip numeric validation
        if form_data.get('equal_shares') in ['true', 'True', '1', True]:
            return {"success": True}
        
        total_share = 0
        i = 1
        
        # Iterate through beneficiaries
        while f'beneficiary_relation_{i}' in form_data or f'beneficiary_{i}_relation' in form_data:
            # Handle both naming patterns (beneficiary_relation_1 or beneficiary_1_relation)
            relation_key = f'beneficiary_relation_{i}' if f'beneficiary_relation_{i}' in form_data else f'beneficiary_{i}_relation'
            share_key = f'beneficiary_share_{i}' if f'beneficiary_share_{i}' in form_data else f'beneficiary_{i}_share'
            
            if form_data.get(relation_key):
                share_str = form_data.get(share_key, '0')
                try:
                    share = float(share_str)
                    total_share += share
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid share value for beneficiary {i}"
                    }
            i += 1
        
        # Allow tiny rounding difference
        if abs(total_share - 100) > 0.01:
            return {
                "success": False,
                "error": f"Total beneficiary shares are {total_share}%, must be exactly 100%"
            }
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": f"Error validating beneficiaries: {str(e)}"}


def validate_form_data(form_data):
    """ Main validation function - checks ALL form data """
    errors = []
    
    # --- Personal fields ---
    required_personal_fields = ['name', 'gender', 'dob', 'phone', 'email']
    for field in required_personal_fields:
        if not form_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # --- Address fields ---
    address_fields = [
        'street_number', 'street_name', 'city', 'regional_municipality', 'province', 'postal_code'
    ]
    for field in address_fields:
        if not form_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # --- Beneficiaries validation ---
    beneficiaries_valid = validate_beneficiaries_shares(form_data)
    if not beneficiaries_valid["success"]:
        errors.append(beneficiaries_valid["error"])
    
    # --- Date formats ---
    date_fields = ['dob', 'exec1_dob', 'exec2_dob']
    for field in date_fields:
        if form_data.get(field) and not validate_date(form_data[field]):
            errors.append(f"Invalid date format for {field}")
    
    # --- Final decision ---
    if errors:
        return {"success": False, "error": " | ".join(errors)}
    
    return {"success": True}


def validate_date(date_string):
    """ Simple date validation (YYYY-MM-DD expected) """
    if not date_string:
        return False
    import re
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return bool(re.match(pattern, str(date_string)))


def validate_percentage(value):
    """ Validate that a value is a valid percentage between 0 and 100 """
    try:
        percentage = float(value)
        return 0 <= percentage <= 100
    except (ValueError, TypeError):
        return False