from flask import Blueprint, render_template, request, jsonify, session
import uuid
from services.step_service import StepService
from helpers.formatters import format_date, title_case, safe_bool
from logic.document import generate_word_document, generate_mirror_will  # ADDED IMPORT

form_steps_bp = Blueprint('form_steps', __name__)


@form_steps_bp.route('/')
def form_home():
    """Start new form session"""
    session.clear()
    session['form_id'] = str(uuid.uuid4())
    session['current_step'] = 1
    session['form_data'] = {}
    return render_template('form_steps/step1_personal.html')


@form_steps_bp.route('/step/<int:step_number>')
def show_step(step_number):
    """Show specific step"""
    if 'form_id' not in session:
        return form_home()

    if step_number < 1 or step_number > 5:
        step_number = 1

    session['current_step'] = step_number

    templates = {
        1: 'step1_personal.html',
        2: 'step2_executors.html',
        3: 'step3_beneficiaries.html',
        4: 'step4_poa.html',
        5: 'step5_review.html'
    }

    return render_template(f"form_steps/{templates.get(step_number)}")


@form_steps_bp.route('/save-step/<int:step_number>', methods=['POST'])
def save_step(step_number):
    """Save step data using StepService validation"""
    try:
        step_data = request.get_json()
        result = StepService.validate_step(step_number, step_data)
        if not result['success']:
            return jsonify({'success': False, 'error': result['error']}), 400

        StepService.save_step_data(step_number, step_data, session)
        return jsonify({'success': True, 'next_step': step_number + 1 if step_number < 5 else 'complete'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@form_steps_bp.route('/get-form-data')
def get_form_data():
    """Return session form data"""
    return jsonify({'success': True, 'form_data': session.get('form_data', {})})


@form_steps_bp.route('/submit-complete-form', methods=['POST'])
def submit_complete_form():
    """
    UPDATED: Final submission with PROPER mirror will generation
    - Uses the fixed generate_mirror_will function from document.py
    - Properly handles uppercase conversion and address formatting
    - Validates spouse relationship before mirror generation
    """
    try:
        form_data = session.get('form_data', {}) or {}
        final_data = request.get_json() or {}
        form_data.update(final_data)

        # Step 1: Validation
        from helpers.validators import validate_form_data
        validation = validate_form_data(form_data)
        if not validation["success"]:
            return jsonify({"success": False, "error": validation["error"]}), 400

        # Step 2: Import all logic handlers
        from logic.poa import process_poa_data
        from logic.executor import process_executor_data
        from logic.beneficiaries import process_beneficiaries_data
        from logic.excel_logger import log_to_excel

        # Step 3: Context assembly - UPDATED FOR UPPERCASE
        poa_context = process_poa_data(form_data)
        executor_context = process_executor_data(form_data)
        beneficiaries_context = process_beneficiaries_data(form_data)

        # FIXED: Use the SAME format_address function that document.py uses
        # Import the function from document.py to ensure consistency
        from logic.document import format_address as document_format_address
        
        # Personal address (fully formatted) - USING DOCUMENT.PY FUNCTION
        personal_address = document_format_address(
            form_data.get('street_number', ''),
            form_data.get('street_name', ''),
            form_data.get('city', ''),
            form_data.get('regional_municipality', ''),
            form_data.get('province', ''),
            form_data.get('postal_code', '')
        )

        # UPDATED: Base context with ALL necessary fields for template
        base_context = {
            **poa_context,
            **executor_context,
            **beneficiaries_context,
            # Personal Information
            "name": form_data.get("name", ""),
            "gender": form_data.get("gender", ""),
            "dob": format_date(form_data.get("dob", "")),
            "address": personal_address,  # Using 'address' for template compatibility
            "full_address": personal_address,  # Alias for template
            "city": form_data.get("city", ""),
            "regional_municipality": form_data.get("regional_municipality", ""),
            # Address components for mirror will swapping
            "street_number": form_data.get("street_number", ""),
            "street_name": form_data.get("street_name", ""),
            "province": form_data.get("province", ""),
            "postal_code": form_data.get("postal_code", ""),
            # Executor fields for mirror will
            "executor_name_one": form_data.get("exec1_name", ""),
            "relation_executor_one": form_data.get("exec1_relation", ""),
            "executor_dob_one": format_date(form_data.get("exec1_dob", "")),
            # Additional executor address fields if available
            "exec1_street_number": form_data.get("exec1_street_number", ""),
            "exec1_street_name": form_data.get("exec1_street_name", ""),
            "exec1_city": form_data.get("exec1_city", ""),
            "exec1_regional_municipality": form_data.get("exec1_regional_municipality", ""),
            "exec1_province": form_data.get("exec1_province", ""),
            "exec1_postal_code": form_data.get("exec1_postal_code", ""),
            # Pronouns
            "pronoun": "his" if form_data.get("gender", "").lower() == "male" else "her",
            # Mirror will options from form
            "mirror_will": form_data.get("mirror_will", False),
            "mirror_poa": form_data.get("mirror_poa", False),
            "mirror_notes": form_data.get("mirror_notes", ""),
        }

        # Step 4: Generate Main Will
        document_path = generate_word_document(base_context)
        log_to_excel({**form_data, "mirror_will": "No"}, document_path)

        # Step 5: UPDATED - Mirror Will Generation using PROPER function
        mirror_doc_path = None
        if safe_bool(form_data.get("mirror_will")):
            try:
                # Use the FIXED generate_mirror_will function from document.py
                mirror_doc_path = generate_mirror_will(base_context)
                
                # Log mirror will to Excel
                mirror_entry = form_data.copy()
                mirror_entry["mirror_will"] = "Yes"
                mirror_entry["mirror_type"] = "Mirror Will"
                log_to_excel(mirror_entry, mirror_doc_path)
                
            except Exception as mirror_error:
                # If mirror generation fails, continue with main will but log the error
                error_msg = f"Mirror will generation skipped: {str(mirror_error)}"
                print(f"⚠️ {error_msg}")
                # Don't fail the entire submission, just skip mirror will
                mirror_doc_path = None

        # Step 6: Success response
        session.clear()
        
        # Build success message
        message = "✅ Will generated successfully!"
        if mirror_doc_path:
            message += " ✅ Mirror Will created successfully."
        else:
            # Check if mirror was requested but failed
            if safe_bool(form_data.get("mirror_will")):
                message += " ⚠️ Mirror Will was not created (spouse must be primary executor)."

        return jsonify({
            "success": True,
            "message": message,
            "document_path": document_path,
            "mirror_path": mirror_doc_path
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"System error: {str(e)}"
        }), 500