from helpers.formatters import format_date, format_address
from copy import deepcopy

def process_poa_data(form_data):
    """
    Process Power of Attorney data - both general and personal care
    """
    context = {}

    # General POA
    if form_data.get('include_poa') in ['true', 'True', '1', True]:
        context.update({
            "include_poa": True,
            "poa_name_one": form_data.get('poa_name_one', ''),
            "poa_relation_one": form_data.get('poa_relation_one', ''),
            "poa_dob_one": format_date(form_data.get('poa_dob_one', '')),
            "poa_address_one": format_address({
                'street_number': form_data.get('poa_street_number_one', ''),
                'street_name': form_data.get('poa_street_name_one', ''),
                'city': form_data.get('poa_city_one', ''),
                'province': form_data.get('poa_province_one', ''),
                'postal_code': form_data.get('poa_postal_code_one', '')
            })
        })

        if form_data.get('second_poa') in ['true', 'True', '1', True]:
            context.update({
                "poa_name_two": form_data.get('poa_name_two', ''),
                "poa_relation_two": form_data.get('poa_relation_two', ''),
                "poa_dob_two": format_date(form_data.get('poa_dob_two', '')),
                "poa_address_two": format_address({
                    'street_number': form_data.get('poa_street_number_two', ''),
                    'street_name': form_data.get('poa_street_name_two', ''),
                    'city': form_data.get('poa_city_two', ''),
                    'province': form_data.get('poa_province_two', ''),
                    'postal_code': form_data.get('poa_postal_code_two', '')
                })
            })

    # Personal Care POA
    if form_data.get('include_poa_personal_care') in ['true', 'True', '1', True]:
        context.update({
            "include_poa_personal_care": True,
            "poa_name_three": form_data.get('poa_name_three', ''),
            "poa_relation_three": form_data.get('poa_relation_three', ''),
            "poa_dob_three": format_date(form_data.get('poa_dob_three', '')),
            "poa_address_three": format_address({
                'street_number': form_data.get('poa_street_number_three', ''),
                'street_name': form_data.get('poa_street_name_three', ''),
                'city': form_data.get('poa_city_three', ''),
                'province': form_data.get('poa_province_three', ''),
                'postal_code': form_data.get('poa_postal_code_three', '')
            })
        })

        if form_data.get('second_poa_personal_care') in ['true', 'True', '1', True]:
            context.update({
                "poa_name_four": form_data.get('poa_name_four', ''),
                "poa_relation_four": form_data.get('poa_relation_four', ''),
                "poa_dob_four": format_date(form_data.get('poa_dob_four', '')),
                "poa_address_four": format_address({
                    'street_number': form_data.get('poa_street_number_four', ''),
                    'street_name': form_data.get('poa_street_name_four', ''),
                    'city': form_data.get('poa_city_four', ''),
                    'province': form_data.get('poa_province_four', ''),
                    'postal_code': form_data.get('poa_postal_code_four', '')
                })
            })

    return context


def generate_mirrored_poa(original_poa_context):
    """
    Creates a mirrored Power of Attorney context by swapping the first and second attorneys.
    """
    poa = deepcopy(original_poa_context)
    if "poa_name_one" in poa and "poa_name_two" in poa:
        poa["poa_name_one"], poa["poa_name_two"] = poa["poa_name_two"], poa["poa_name_one"]
        poa["poa_relation_one"], poa["poa_relation_two"] = poa["poa_relation_two"], poa["poa_relation_one"]
    return poa
