class QuMailComposeManager {
    constructor() {
        this.sendBtn = null;
        this.recipientInput = null;
        this.subjectInput = null;
        this.messageTextarea = null;
        this.encryptionLevelSelect = null;
        this.isSending = false;
        
        console.log('✉️ QuMail Compose Manager initialized');
    }

    /**
     * Initialize the compose manager
     */
    initialize() {
        console.log('🔄 Initializing Compose Manager...');
        
        // Get UI elements
        this.getUIElements();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ Compose Manager ready');
    }

    /**
     * Get UI elements
     */
    getUIElements() {
        this.sendBtn = document.getElementById('send-secure-btn');
        this.recipientInput = document.getElementById('recipient');
        this.subjectInput = document.getElementById('subject');
        this.messageTextarea = document.getElementById('message');
        this.encryptionLevelSelect = document.getElementById('encryption-level');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Send button click
        if (this.sendBtn) {
            // Remove any existing listeners and replace with real email sending
            const newSendBtn = this.sendBtn.cloneNode(true);
            this.sendBtn.parentNode.replaceChild(newSendBtn, this.sendBtn);
            this.sendBtn = newSendBtn;
            
            this.sendBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleSendEmail();
            });
            
            console.log('✅ Real email send handler attached');
        }

        // Enter key in message textarea for quick send
        if (this.messageTextarea) {
            this.messageTextarea.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    this.handleSendEmail();
                }
            });
        }
    }

    /**
     * Handle email sending
     */
    async handleSendEmail() {
        if (this.isSending) return;

        try {
            // Validate form
            const formData = this.validateAndGetFormData();
            if (!formData) return;

            // Check if user is logged in
            if (!window.emailIntegration || !window.emailIntegration.isReady()) {
                this.showError('Please sign in to send emails');
                if (window.quMailProfileManager) {
                    window.quMailProfileManager.showCenterModal();
                }
                return;
            }

            // Show sending state
            this.setSendingState(true);

            // Show hybrid key animation based on security level
            this.showHybridKeyAnimation(formData.securityLevel);

            // Small delay to let animation start before sending
            await new Promise(resolve => setTimeout(resolve, 500));

            // Send email via email integration
            console.log('📧 Sending real encrypted email...');
            const result = await window.emailIntegration.sendEncryptedEmail(formData);

            if (result && result.success) {
                this.showSuccess(`Email sent successfully! Message ID: ${result.message_id}`);
                this.clearForm();
            } else {
                throw new Error(result?.error || 'Failed to send email');
            }

        } catch (error) {
            console.error('❌ Email send failed:', error);
            this.showError(`Failed to send email: ${error.message}`);
        } finally {
            this.setSendingState(false);
        }
    }

    /**
     * Validate form and get data
     */
    validateAndGetFormData() {
        const recipient = this.recipientInput?.value?.trim();
        const subject = this.subjectInput?.value?.trim();
        const message = this.messageTextarea?.value?.trim();
        const securityLevel = parseInt(this.encryptionLevelSelect?.value || 2);

        // Validation
        if (!recipient) {
            this.showError('Please enter a recipient email address');
            this.recipientInput?.focus();
            return null;
        }

        if (!this.isValidEmail(recipient)) {
            this.showError('Please enter a valid email address');
            this.recipientInput?.focus();
            return null;
        }

        if (!subject) {
            this.showError('Please enter a subject');
            this.subjectInput?.focus();
            return null;
        }

        if (!message) {
            this.showError('Please enter a message');
            this.messageTextarea?.focus();
            return null;
        }

        return {
            to: recipient,
            recipient: recipient,
            subject: subject,
            message: message,
            securityLevel: securityLevel,
            attachments: []
        };
    }

    /**
     * Validate email address
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Show hybrid key animation based on security level
     */
    showHybridKeyAnimation(securityLevel) {
        if (!window.showHybridKeyAnimation) {
            console.log('⚠️ Hybrid key animation not available');
            return;
        }

        // Determine which key types to show based on security level
        let keyTypes = [];
        
        switch(parseInt(securityLevel)) {
            case 1: // Quantum Secure - QKD only
                keyTypes = ['qkd'];
                break;
            case 2: // Quantum-aided AES - QKD + ECDH
                keyTypes = ['qkd', 'ecdh'];
                break;
            case 3: // Hybrid PQC - ML-KEM + ECDH
                keyTypes = ['mlkem', 'ecdh'];
                break;
            case 4: // No Quantum - Classical encryption
                keyTypes = ['ecdh']; // Just show ECDH for classical
                break;
            default:
                keyTypes = ['qkd', 'mlkem', 'ecdh']; // Full hybrid
        }

        console.log(`🎭 Triggering hybrid key animation for Level ${securityLevel} with keys:`, keyTypes);
        window.showHybridKeyAnimation(keyTypes);

        // Listen for animation completion to hide loading state properly
        const handleAnimationComplete = () => {
            console.log('✅ Hybrid animation completed');
            document.removeEventListener('animationComplete', handleAnimationComplete);
        };
        
        document.addEventListener('animationComplete', handleAnimationComplete);
    }

    /**
     * Set sending state
     */
    setSendingState(sending) {
        this.isSending = sending;
        
        if (this.sendBtn) {
            if (sending) {
                this.sendBtn.disabled = true;
                this.sendBtn.innerHTML = `
                    <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>Sending...</span>
                `;
                this.sendBtn.classList.add('opacity-75');
            } else {
                this.sendBtn.disabled = false;
                this.sendBtn.innerHTML = `
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                    </svg>
                    <span>Send Secure</span>
                `;
                this.sendBtn.classList.remove('opacity-75');
            }
        }
    }

    /**
     * Clear the form
     */
    clearForm() {
        if (this.recipientInput) this.recipientInput.value = '';
        if (this.subjectInput) this.subjectInput.value = '';
        if (this.messageTextarea) this.messageTextarea.value = '';
        
        // Reset to default security level
        if (this.encryptionLevelSelect) {
            this.encryptionLevelSelect.value = '2';
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-6 right-6 z-[99999] max-w-md p-4 rounded-lg shadow-xl transition-all duration-300 transform translate-x-full ${
            type === 'success' ? 'bg-green-500/90 text-white border border-green-400' :
            type === 'error' ? 'bg-red-500/90 text-white border border-red-400' :
            'bg-violet-500/90 text-white border border-violet-400'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                    ${type === 'success' ? 
                        '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>' :
                        type === 'error' ?
                        '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>' :
                        '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                    }
                </div>
                <div class="flex-1">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="flex-shrink-0 opacity-70 hover:opacity-100">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    }
}

// Initialize Compose Manager when DOM is ready
let quMailComposeManager = null;

document.addEventListener('DOMContentLoaded', () => {
    // Wait for other components to initialize first
    setTimeout(() => {
        quMailComposeManager = new QuMailComposeManager();
        quMailComposeManager.initialize();
        
        // Make it globally available
        window.quMailComposeManager = quMailComposeManager;
        
        console.log('🚀 Compose Manager fully initialized');
    }, 1000);
});
