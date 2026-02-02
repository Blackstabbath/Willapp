import logging
import os
import datetime
from copy import deepcopy
from docxtpl import DocxTemplate

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# UPDATED: Address formatting - EXCLUDES regional_municipality
# ------------------------------------------------------------
def format_address(street_number, street_name, city, regional_municipality, province, postal_code):
    """Combine address parts into the same style as old app - NOW WITH UPPERCASE"""
    parts = []
    
    # Street part
    street = f"{street_number} {street_name}".strip()
    if street:
        parts.append(street)
    
    # City only (EXCLUDING regional_municipality)
    if city:
        parts.append(city)
    
    # Province and postal code
    province_postal = f"{province} {postal_code}".strip()
    if province_postal:
        parts.append(province_postal)
    
    address = ", ".join(parts)
    return address.upper()  # Convert to UPPERCASE

def convert_all_to_uppercase(data_dict):
    """Convert ALL string values in dictionary to UPPERCASE - LIKE YOUR OLD APP"""
    result = {}
    for key, value in data_dict.items():
        if isinstance(value, str):
            result[key] = value.upper()
        elif isinstance(value, list):
            # Handle beneficiary lists
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    # Convert each beneficiary dict to uppercase
                    upper_item = {}
                    for k, v in item.items():
                        if isinstance(v, str):
                            upper_item[k] = v.upper()
                        else:
                            upper_item[k] = v
                    new_list.append(upper_item)
                else:
                    new_list.append(item.upper() if isinstance(item, str) else item)
            result[key] = new_list
        elif isinstance(value, dict):
            result[key] = convert_all_to_uppercase(value)
        else:
            result[key] = value
    return result

def generate_word_document(context, is_mirror=False):
    """Generate the will Word document with docxtpl - NOW WITH UPPERCASE"""
    try:
        logger.info("Starting Word document generation...")

        # --- locate template ---
        template_name = "universal_will_template.docx"
        possible_paths = [
            template_name,
            f"templates/{template_name}",
            os.path.join(os.path.dirname(__file__), f"../{template_name}"),
            os.path.join(os.path.dirname(__file__), f"../templates/{template_name}")
        ]
        template_path = next((p for p in possible_paths if os.path.exists(p)), None)
        if not template_path:
            raise FileNotFoundError(f"Template file not found. Checked: {possible_paths}")

        # ------------------------------------------------------------
        # UPDATED: CONVERT EVERYTHING TO UPPERCASE FIRST
        # ------------------------------------------------------------
        context = convert_all_to_uppercase(context)

        # ------------------------------------------------------------
        # UPDATED: ADDRESS HANDLING (now EXCLUDES regional_municipality)
        # ------------------------------------------------------------
        address = format_address(
            context.get("street_number", ""),
            context.get("street_name", ""),
            context.get("city", ""),
            context.get("regional_municipality", ""),  # Still passed but not used in formatting
            context.get("province", ""),
            context.get("postal_code", "")
        )
        context["address"] = address
        context["full_address"] = address  # optional alias

        # ------------------------------------------------------------
        # DATE NORMALIZATION
        # ------------------------------------------------------------
        for key, value in list(context.items()):
            # Convert date objects
            if isinstance(value, (datetime.date, datetime.datetime)):
                context[key] = value.strftime("%Y-%m-%d")
            # Convert strings like "01 Oct 2025"
            elif isinstance(value, str):
                try:
                    parsed = datetime.datetime.strptime(value, "%d %b %Y")
                    context[key] = parsed.strftime("%Y-%m-%d")
                except Exception:
                    pass

        # ------------------------------------------------------------
        # FIXED: BENEFICIARIES - REMOVED THE CODE THAT WAS OVERWRITING DATA
        # ------------------------------------------------------------
        # The beneficiaries data from process_beneficiaries_data() is already correct
        # Don't overwrite it - just ensure it exists
        if "beneficiaries" not in context:
            context["beneficiaries"] = []
        


        # Ensure equal_shares flag and computed share percentage
        equal_flag = context.get("equal_shares")
        if equal_flag in ("True", "true", "1", 1, True):
            context["equal_shares"] = True
        else:
            context["equal_shares"] = False

        if context["equal_shares"] and context["beneficiaries"]:
            context["equal_share_percentage"] = f"{100.0 / len(context['beneficiaries']):.2f}"


        # ------------------------------------------------------------
        # Render and save
        # ------------------------------------------------------------
        doc = DocxTemplate(template_path)
        doc.render(context)

        os.makedirs("generated_wills", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_name = context.get("name", "Unknown")
        safe_name = "".join(c for c in raw_name if c.isalnum() or c in (" ", "-", "_")).strip()
        prefix = "Mirror_" if is_mirror or context.get("is_mirror") else ""
        filename = f"{prefix}Will_{safe_name or 'Unknown'}_{timestamp}.docx"
        output_path = os.path.join("generated_wills", filename)
        doc.save(output_path)

        logger.info(f"✅ Document saved successfully: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"❌ Document generation failed: {str(e)}", exc_info=True)
        raise Exception(f"Document generation failed: {str(e)}") from e


def generate_mirror_will(original_context):
    """
    UPDATED: Create a PROPER 'mirror' will by COMPLETELY flipping applicant <-> spouse
    This now works EXACTLY like your old desktop app
    """
    try:
        ctx = deepcopy(original_context)
        
        # Check if we can create a mirror will (spouse must be executor)
        spouse_relation = ctx.get("relation_executor_one", "").lower()
        is_spouse_executor = any(term in spouse_relation for term in ["wife", "husband", "spouse"])
        
        if not is_spouse_executor:
            raise Exception("Cannot create mirror will - spouse must be primary executor")

        # ------------------------------------------------------------
        # COMPLETE ROLE SWAP: Applicant becomes Executor, Executor becomes Applicant
        # ------------------------------------------------------------
        
        # Store original values before swap
        original_applicant = {
            "name": ctx.get("name", ""),
            "gender": ctx.get("gender", ""),
            "dob": ctx.get("dob", ""),
            "address": ctx.get("address", ""),
            "street_number": ctx.get("street_number", ""),
            "street_name": ctx.get("street_name", ""),
            "city": ctx.get("city", ""),
            "regional_municipality": ctx.get("regional_municipality", ""),
            "province": ctx.get("province", ""),
            "postal_code": ctx.get("postal_code", "")
        }
        
        original_executor = {
            "name": ctx.get("executor_name_one", ""),
            "relation": ctx.get("relation_executor_one", ""),
            "dob": ctx.get("executor_dob_one", ""),
            "street_number": ctx.get("exec1_street_number", ""),
            "street_name": ctx.get("exec1_street_name", ""),
            "city": ctx.get("exec1_city", ""),
            "regional_municipality": ctx.get("exec1_regional_municipality", ""),
            "province": ctx.get("exec1_province", ""),
            "postal_code": ctx.get("exec1_postal_code", "")
        }

        # SWAP: Executor becomes new Applicant
        ctx["name"] = original_executor["name"]
        ctx["dob"] = original_executor["dob"]
        
        # SWAP: Applicant becomes new Executor
        ctx["executor_name_one"] = original_applicant["name"]
        ctx["relation_executor_one"] = "SPOUSE"  # Always set to spouse in mirror
        ctx["executor_dob_one"] = original_applicant["dob"]

        # ------------------------------------------------------------
        # SWAP ADDRESSES if executor address exists
        # ------------------------------------------------------------
        if original_executor["street_number"]:
            # Use executor's address for new applicant
            ctx["street_number"] = original_executor["street_number"]
            ctx["street_name"] = original_executor["street_name"]
            ctx["city"] = original_executor["city"]
            ctx["regional_municipality"] = original_executor["regional_municipality"]
            ctx["province"] = original_executor["province"]
            ctx["postal_code"] = original_executor["postal_code"]
            
            # Use applicant's address for new executor
            ctx["exec1_street_number"] = original_applicant["street_number"]
            ctx["exec1_street_name"] = original_applicant["street_name"]
            ctx["exec1_city"] = original_applicant["city"]
            ctx["exec1_regional_municipality"] = original_applicant["regional_municipality"]
            ctx["exec1_province"] = original_applicant["province"]
            ctx["exec1_postal_code"] = original_applicant["postal_code"]

        # ------------------------------------------------------------
        # GENDER & PRONOUN SWAP
        # ------------------------------------------------------------
        original_gender = original_applicant["gender"].lower()
        if original_gender == "male":
            ctx["gender"] = "FEMALE"
            ctx["pronoun"] = "HER"
        elif original_gender == "female":
            ctx["gender"] = "MALE" 
            ctx["pronoun"] = "HIS"
        else:
            ctx["gender"] = original_applicant["gender"]
            ctx["pronoun"] = "THEIR"

        # ------------------------------------------------------------
        # MIRROR POA: If POA attorney is spouse, swap roles
        # ------------------------------------------------------------
        if ctx.get("include_poa"):
            poa_relation = ctx.get("poa_relation_one", "").lower()
            if any(term in poa_relation for term in ["wife", "husband", "spouse"]):
                # Swap POA attorney with applicant
                ctx["poa_name_one"] = original_applicant["name"]
                ctx["poa_relation_one"] = "SPOUSE"
                ctx["poa_dob_one"] = original_applicant["dob"]
                
                # Update POA address to match new applicant's address
                ctx["poa_address_one"] = format_address(
                    ctx.get("street_number", ""),
                    ctx.get("street_name", ""),
                    ctx.get("city", ""),
                    ctx.get("regional_municipality", ""),
                    ctx.get("province", ""),
                    ctx.get("postal_code", "")
                )

        # ------------------------------------------------------------
        # MIRROR PERSONAL CARE POA: If attorney is spouse, swap roles
        # ------------------------------------------------------------
        if ctx.get("include_poa_personal_care"):
            poa_pc_relation = ctx.get("poa_relation_three", "").lower()
            if any(term in poa_pc_relation for term in ["wife", "husband", "spouse"]):
                # Swap Personal Care POA attorney with applicant
                ctx["poa_name_three"] = original_applicant["name"]
                ctx["poa_relation_three"] = "SPOUSE"
                ctx["poa_dob_three"] = original_applicant["dob"]
                
                # Update POA address to match new applicant's address
                ctx["poa_address_three"] = format_address(
                    ctx.get("street_number", ""),
                    ctx.get("street_name", ""),
                    ctx.get("city", ""),
                    ctx.get("regional_municipality", ""),
                    ctx.get("province", ""),
                    ctx.get("postal_code", "")
                )

        # ------------------------------------------------------------
        # REBUILD ADDRESS FOR CONSISTENCY
        # ------------------------------------------------------------
        ctx["address"] = format_address(
            ctx.get("street_number", ""),
            ctx.get("street_name", ""),
            ctx.get("city", ""),
            ctx.get("regional_municipality", ""),
            ctx.get("province", ""),
            ctx.get("postal_code", "")
        )

        ctx["is_mirror"] = True
        ctx["name_display"] = f"{ctx.get('name', '')} (MIRROR WILL)"

        # ------------------------------------------------------------
        # CONVERT EVERYTHING TO UPPERCASE BEFORE GENERATING
        # ------------------------------------------------------------
        ctx = convert_all_to_uppercase(ctx)

        # --- generate mirrored document ---
        return generate_word_document(ctx, is_mirror=True)

    except Exception as e:
        logger.error(f"Mirror document generation failed: {str(e)}", exc_info=True)
        raise