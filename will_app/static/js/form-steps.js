// Form step navigation and progress tracking
class FormSteps {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 5;
        this.init();
    }

    init() {
        this.updateProgressBar();
        this.setupStepNavigation();
    }

    updateProgressBar() {
        // Highlight current step in progress bar
        const steps = document.querySelectorAll('.progress-step');
        steps.forEach((step, index) => {
            const stepNumber = index + 1;
            if (stepNumber === this.currentStep) {
                step.classList.add('current');
            } else {
                step.classList.remove('current');
            }
        });
    }

    setupStepNavigation() {
        // Handle back button if present
        const backButton = document.querySelector('.btn-secondary');
        if (backButton) {
            backButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.goToPreviousStep();
            });
        }

        // Add step number to form for tracking
        const forms = document.querySelectorAll('.step-form');
        forms.forEach(form => {
            form.setAttribute('data-step', this.currentStep);
        });
    }

    goToPreviousStep() {
        if (this.currentStep > 1) {
            window.location.href = `/step/${this.currentStep - 1}`;
        }
    }

    goToNextStep() {
        if (this.currentStep < this.totalSteps) {
            window.location.href = `/step/${this.currentStep + 1}`;
        }
    }

    // Validate step before proceeding
    validateStep(stepNumber, formData) {
        switch(stepNumber) {
            case 1:
                return this.validateStep1(formData);
            case 2:
                return this.validateStep2(formData);
            // Add validation for other steps
            default:
                return { valid: true };
        }
    }

    validateStep1(formData) {
        const errors = [];
        
        if (!formData.name) {
            errors.push('Full name is required');
        }
        
        if (!formData.gender) {
            errors.push('Gender is required');
        }
        
        if (!formData.dob) {
            errors.push('Date of birth is required');
        }
        
        if (!formData.phone) {
            errors.push('Phone number is required');
        }
        
        if (!formData.email) {
            errors.push('Email is required');
        }
        
        if (formData.phone && !/^\d{10}$/.test(formData.phone.replace(/\D/g, ''))) {
            errors.push('Phone number must be 10 digits');
        }
        
        if (formData.email && !formData.email.includes('@')) {
            errors.push('Valid email is required');
        }

        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    validateStep2(formData) {
        const errors = [];
        
        if (!formData.exec1_name || !formData.exec1_relation) {
            errors.push('First executor name and relation are required');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.formSteps = new FormSteps();
    
    // Add real-time validation for step 1
    const step1Form = document.getElementById('step1-form');
    if (step1Form) {
        setupStep1Validation();
    }
});

function setupStep1Validation() {
    const phoneInput = document.getElementById('phone');
    const emailInput = document.getElementById('email');
    const postalInput = document.getElementById('postal_code');

    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // Keep only numbers
            this.value = this.value.replace(/\D/g, '');
            
            // Validate length
            if (this.value.length > 10) {
                this.value = this.value.slice(0, 10);
            }
        });
    }

    if (postalInput) {
        postalInput.addEventListener('input', function(e) {
            // Format as A1A 1A1
            let value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            if (value.length > 3) {
                value = value.slice(0, 3) + ' ' + value.slice(3, 6);
            }
            this.value = value;
        });
    }
}