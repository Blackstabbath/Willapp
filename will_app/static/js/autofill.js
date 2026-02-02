// Enhanced Auto-fill functionality
console.log('Auto-fill module loaded - FIXED VERSION');

class AutoFill {
    constructor() {
        this.availableData = {};
        this.initializeAutofill();
    }

    initializeAutofill() {
        console.log('Auto-fill initialized');

        // Detect current step by dataset attribute if available
        const currentStep = document.querySelector('[data-step]');
        const stepNum = currentStep ? parseInt(currentStep.dataset.step) : null;

        // Hide or disable “Use Myself” button in Step 3 (Beneficiaries)
        if (stepNum === 3) {
            const btn = document.querySelector('#btnUseMyself');
            if (btn) {
                btn.style.display = 'none';
                btn.disabled = true;
                btn.onclick = (e) => {
                    e.preventDefault();
                    console.warn('“Use Myself” button is disabled on Beneficiaries step.');
                    return false;
                };
            }
        }

        // Add any other per-step initialization here later
    }

    // Update available data from previous steps
    updateAvailableData(formData) {
        this.availableData = formData;
        console.log('Auto-fill data updated:', this.availableData);
    }

    // Generic method for suggesting or mapping data
    suggestFromExisting(data) {
        console.log('Auto-fill suggestions:', data);
        return [];
    }
}

// Create global instance
window.autoFill = new AutoFill();

// Basic ready hook
document.addEventListener('DOMContentLoaded', () => {
    console.log('Auto-fill system ready');
});
