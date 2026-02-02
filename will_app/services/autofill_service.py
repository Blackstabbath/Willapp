class AutofillService:
    """Service for generating auto-fill suggestions based on existing form data"""
    
    @staticmethod
    def generate_suggestions(form_data):
        """Generate auto-fill suggestions from existing form data"""
        suggestions = {
            'personal': {},
            'executors': [],
            'beneficiaries': []
        }
        
        # Personal information suggestions
        if form_data.get('name'):
            suggestions['personal']['self'] = {
                'type': 'self',
                'name': form_data.get('name'),
                'dob': form_data.get('dob'),
                'address': AutofillService._format_address(form_data)
            }
        
        # Executor suggestions
        if form_data.get('exec1_name'):
            suggestions['executors'].append({
                'type': 'executor1',
                'name': form_data.get('exec1_name'),
                'relation': form_data.get('exec1_relation'),
                'dob': form_data.get('exec1_dob')
            })
        
        if form_data.get('exec2_name'):
            suggestions['executors'].append({
                'type': 'executor2', 
                'name': form_data.get('exec2_name'),
                'relation': form_data.get('exec2_relation'),
                'dob': form_data.get('exec2_dob')
            })
        
        return suggestions
    
    @staticmethod
    def autofill_beneficiary(form_data, source_type, index=1):
        """Auto-fill beneficiary from existing data"""
        if source_type == 'executor1':
            return {
                'name': form_data.get('exec1_name', ''),
                'relation': form_data.get('exec1_relation', ''),
                'dob': form_data.get('exec1_dob', '')
            }
        elif source_type == 'executor2':
            return {
                'name': form_data.get('exec2_name', ''),
                'relation': form_data.get('exec2_relation', ''),
                'dob': form_data.get('exec2_dob', '')
            }
        elif source_type == 'self':
            return {
                'name': form_data.get('name', ''),
                'relation': 'Self',
                'dob': form_data.get('dob', '')
            }
        return {}
    
    @staticmethod
    def autofill_poa(form_data, source_type, poa_type='general'):
        """Auto-fill POA from existing data"""
        if source_type == 'executor1':
            return {
                'name': form_data.get('exec1_name', ''),
                'relation': form_data.get('exec1_relation', ''),
                'dob': form_data.get('exec1_dob', ''),
                'address': AutofillService._format_address(form_data)
            }
        elif source_type == 'executor2':
            return {
                'name': form_data.get('exec2_name', ''),
                'relation': form_data.get('exec2_relation', ''),
                'dob': form_data.get('exec2_dob', ''),
                'address': AutofillService._format_address(form_data)
            }
        elif source_type == 'self':
            return {
                'name': form_data.get('name', ''),
                'relation': 'Self',
                'dob': form_data.get('dob', ''),
                'address': AutofillService._format_address(form_data)
            }
        return {}
    
    @staticmethod
    def _format_address(form_data):
        """Format address from form data"""
        parts = []
        if form_data.get('street_number') and form_data.get('street_name'):
            parts.append(f"{form_data.get('street_number')} {form_data.get('street_name')}")
        if form_data.get('city'):
            parts.append(form_data.get('city'))
        if form_data.get('regional_municipality'):
            parts.append(form_data.get('regional_municipality'))
        if form_data.get('province'):
            parts.append(form_data.get('province'))
        if form_data.get('postal_code'):
            parts.append(form_data.get('postal_code'))
        
        return ", ".join(parts) if parts else ""