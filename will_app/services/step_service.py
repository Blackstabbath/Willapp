class StepService:
    """Service for handling form step progression and validation"""
    
    @staticmethod
    def validate_step(step_number, data):
        """Validate data for each step"""
        if step_number == 1:  # Personal Information
            return StepService._validate_personal_info(data)
        elif step_number == 2:  # Executors
            return StepService._validate_executors(data)
        elif step_number == 3:  # Beneficiaries
            return StepService._validate_beneficiaries(data)
        elif step_number == 4:  # POA
            return StepService._validate_poa(data)
        elif step_number == 5:  # Review
            return StepService._validate_review(data)
        else:
            return {'success': False, 'error': 'Invalid step number'}
    
    @staticmethod
    def save_step_data(step_number, data, session):
        """Save step data to session - FIXED for beneficiary data structure"""
        if 'form_data' not in session:
            session['form_data'] = {}
        
        # Step-specific data saving
        if step_number == 1:
            session['form_data']['personal'] = data
        elif step_number == 2:
            session['form_data']['executors'] = data
        elif step_number == 3:
            session['form_data']['beneficiaries'] = data
        elif step_number == 4:
            session['form_data']['poa'] = data
        elif step_number == 5:
            session['form_data']['review'] = data
        
        # FIXED: Merge ALL data to top level for document generation
        # This ensures beneficiary fields are available at top level for process_beneficiaries_data()
        for key, value in data.items():
            session['form_data'][key] = value
        
        # UPDATED: Ensure mirror will options are preserved
        if step_number == 5 and data.get('mirror_will'):
            session['form_data']['mirror_will'] = data.get('mirror_will')
            session['form_data']['mirror_poa'] = data.get('mirror_poa', False)
            session['form_data']['mirror_notes'] = data.get('mirror_notes', '')
        
        session.modified = True
    
    @staticmethod
    def _validate_personal_info(data):
        """Validate personal information step - UPDATED for address fields"""
        required_fields = ['name', 'gender', 'dob', 'phone', 'email']
        for field in required_fields:
            if not data.get(field):
                return {'success': False, 'error': f'Missing required field: {field}'}
        
        # UPDATED: Address field validation
        address_fields = ['street_number', 'street_name', 'city', 'regional_municipality', 'province', 'postal_code']
        for field in address_fields:
            if not data.get(field):
                return {'success': False, 'error': f'Missing required address field: {field}'}
        
        # Email validation
        email = data.get('email', '')
        if email and '@' not in email:
            return {'success': False, 'error': 'Invalid email format'}
        
        # Phone validation
        phone = data.get('phone', '')
        if phone and len(phone.replace('-', '')) < 10:
            return {'success': False, 'error': 'Phone number must be at least 10 digits'}
        
        # Postal code validation (basic)
        postal_code = data.get('postal_code', '')
        if postal_code and len(postal_code.replace(' ', '')) < 6:
            return {'success': False, 'error': 'Postal code must be at least 6 characters'}
        
        return {'success': True}
    
    @staticmethod
    def _validate_executors(data):
        """Validate executor information - UPDATED for mirror will compatibility"""
        if not data.get('exec1_name') or not data.get('exec1_relation'):
            return {'success': False, 'error': 'First executor name and relation are required'}
        
        # UPDATED: Validate date of birth for executors
        if not data.get('exec1_dob'):
            return {'success': False, 'error': 'First executor date of birth is required'}
        
        # If second executor is included, validate their data
        if data.get('include_second_executor'):
            if not data.get('exec2_name') or not data.get('exec2_relation'):
                return {'success': False, 'error': 'Second executor name and relation are required when included'}
            if not data.get('exec2_dob'):
                return {'success': False, 'error': 'Second executor date of birth is required when included'}
        
        return {'success': True}
    
    @staticmethod
    def _validate_beneficiaries(data):
        """Validate beneficiaries information - FIXED for field-based structure"""
        
        # Check for at least one complete beneficiary
        has_beneficiaries = False
        
        # Check for field-based structure (beneficiary_1_name, beneficiary_1_relation, etc.)
        for i in range(1, 11):  # Check up to 10 beneficiaries
            name = data.get(f'beneficiary_{i}_name')
            relation = data.get(f'beneficiary_{i}_relation')
            dob = data.get(f'beneficiary_{i}_dob')
            
            # If we have at least name and relation, consider it a valid beneficiary
            if name and relation:
                has_beneficiaries = True
                break
        
        if not has_beneficiaries:
            return {'success': False, 'error': 'At least one beneficiary is required'}
        
        # Validate shares if not equal shares
        if not data.get('equal_shares'):
            total_share = 0
            
            for i in range(1, 11):
                name = data.get(f'beneficiary_{i}_name')
                relation = data.get(f'beneficiary_{i}_relation')
                
                # Only validate shares for beneficiaries that have name and relation
                if name and relation:
                    share_str = data.get(f'beneficiary_{i}_share', '0')
                    try:
                        share = float(share_str) if share_str else 0
                        total_share += share
                    except ValueError:
                        return {'success': False, 'error': f'Beneficiary {i}: invalid share value'}
            
            if abs(total_share - 100) > 0.01:
                return {'success': False, 'error': f'Beneficiary shares must total 100% (currently {total_share:.2f}%)'}
        
        return {'success': True}
    
    @staticmethod
    def _validate_poa(data):
        """Validate POA information - UPDATED for complete address validation"""
        # If general POA is included, validate required fields
        if data.get('include_poa'):
            if not data.get('poa_name_one') or not data.get('poa_relation_one'):
                return {'success': False, 'error': 'General POA attorney name and relation are required'}
            if not data.get('poa_dob_one'):
                return {'success': False, 'error': 'General POA attorney date of birth is required'}
            
            # UPDATED: Validate POA address fields
            poa_address_fields = ['poa_street_number_one', 'poa_street_name_one', 'poa_city_one', 'poa_province_one', 'poa_postal_code_one']
            for field in poa_address_fields:
                if not data.get(field):
                    return {'success': False, 'error': f'General POA attorney {field.replace("_one", "").replace("_", " ")} is required'}
        
        # If personal care POA is included, validate required fields
        if data.get('include_poa_personal_care'):
            if not data.get('poa_name_three') or not data.get('poa_relation_three'):
                return {'success': False, 'error': 'Personal care POA attorney name and relation are required'}
            if not data.get('poa_dob_three'):
                return {'success': False, 'error': 'Personal care POA attorney date of birth is required'}
            
            # UPDATED: Validate Personal Care POA address fields
            poa_pc_address_fields = ['poa_street_number_three', 'poa_street_name_three', 'poa_city_three', 'poa_province_three', 'poa_postal_code_three']
            for field in poa_pc_address_fields:
                if not data.get(field):
                    return {'success': False, 'error': f'Personal care POA attorney {field.replace("_three", "").replace("_", " ")} is required'}
        
        return {'success': True}
    
    @staticmethod
    def _validate_review(data):
        """Validate review step (terms acceptance) - UPDATED for mirror will options"""
        if not data.get('terms_agreement'):
            return {'success': False, 'error': 'You must accept the terms and conditions'}
        
        # UPDATED: Validate mirror will conditions if selected
        if data.get('mirror_will'):
            # Check if primary executor is spouse (required for mirror will)
            exec_relation = data.get('exec1_relation', '').lower()
            is_spouse = any(term in exec_relation for term in ['wife', 'husband', 'spouse'])
            
            if not is_spouse:
                return {'success': False, 'error': 'Mirror will requires spouse to be primary executor'}
        
        return {'success': True}