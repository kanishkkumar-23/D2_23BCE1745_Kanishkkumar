class QuMailEmailIntegration {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.isConnected = false;
        this.credentials = null;
        this.initializeConnection();
    }

    // Initialize connection and check email status
    async initializeConnection() {
        try {
            console.log('🔄 Connecting to QuMail Email Integration API...');
            
            const response = await fetch(`${this.apiBaseUrl}/email/status`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.isConnected = true;
            
            console.log('✅ Connected to QuMail Email Integration API');
            console.log('📧 Supported providers:', data.supported_providers);
            console.log('🔒 Security levels:', Object.keys(data.supported_security_levels));
            
            return data;
            
        } catch (error) {
            console.error('❌ Failed to connect to email integration API:', error);
            this.isConnected = false;
            return null;
        }
    }

    // Set email credentials (Gmail App Password)
    setCredentials(email, appPassword) {
        this.credentials = {
            email: email,
            password: appPassword
        };
        console.log(`🔐 Email credentials set for: ${email}`);
    }

    // Send encrypted email via backend API
    async sendEncryptedEmail(formData) {
        try {
            if (!this.credentials) {
                throw new Error('Email credentials not set. Please configure Gmail App Password.');
            }

            // Handle both camelCase and snake_case parameter formats
            const securityLevel = formData.securityLevel || formData.security_level;
            
            // Validate security level
            if (!securityLevel || ![1, 2, 3, 4, '1', '2', '3', '4'].includes(securityLevel)) {
                throw new Error(`Invalid security level: ${securityLevel}. Must be 1, 2, 3, or 4.`);
            }
            
            console.log(`📧 Sending encrypted email with Level ${securityLevel}...`);
            
            // Prepare request data for email API
            const requestData = {
                sender_email: this.credentials.email,
                sender_password: this.credentials.password,
                recipient: formData.recipient || formData.to,
                subject: formData.subject,
                content: formData.message,
                security_level: parseInt(securityLevel),
                attachments: formData.attachments || []
            };
            
            // Call backend email send API
            const response = await fetch(`${this.apiBaseUrl}/email/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Email sending failed');
            }
            
            console.log(`✅ Email sent successfully: ${result.message_id}`);
            console.log(`🔐 Algorithm: ${result.encryption_metadata.algorithm}`);
            console.log(`⏰ Sent at: ${result.sent_at}`);
            
            // Format result for frontend compatibility
            return {
                success: true,
                algorithm: result.encryption_metadata.algorithm,
                keyId: result.message_id,
                encryptedMessage: 'Email sent via SMTP',
                integrity: result.encryption_metadata.integrity_hash || 'verified',
                timestamp: result.sent_at,
                quantum_resistant: result.encryption_metadata.quantum_resistant,
                etsi_compliant: result.encryption_metadata.etsi_compliant,
                email_sent: true,
                message_id: result.message_id
            };
            
        } catch (error) {
            console.error('❌ Email sending failed:', error);
            
            // Return error in expected format
            return {
                success: false,
                error: error.message,
                email_sent: false
            };
        }
    }

    // Send test email
    async sendTestEmail(recipient, securityLevel = 2) {
        try {
            if (!this.credentials) {
                throw new Error('Email credentials not set. Please configure Gmail App Password.');
            }

            console.log(`🧪 Sending test email with Level ${securityLevel}...`);
            
            const requestData = {
                sender_email: this.credentials.email,
                sender_password: this.credentials.password,
                recipient: recipient,
                security_level: securityLevel
            };
            
            const response = await fetch(`${this.apiBaseUrl}/email/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log(`✅ Test email sent: ${result.message_id}`);
            return result;
            
        } catch (error) {
            console.error('❌ Test email failed:', error);
            throw error;
        }
    }

    // Receive emails from Gmail IMAP
    async receiveEmails(limit = 10, folder = 'INBOX') {
        try {
            if (!this.credentials) {
                throw new Error('Email credentials not set. Please configure Gmail App Password.');
            }

            console.log(`📬 Receiving emails from ${folder}...`);
            
            const requestData = {
                email: this.credentials.email,
                password: this.credentials.password,
                limit: limit,
                folder: folder
            };
            
            const response = await fetch(`${this.apiBaseUrl}/email/receive`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log(`✅ Received ${result.total_count} emails`);
            return result;
            
        } catch (error) {
            console.error('❌ Email receiving failed:', error);
            throw error;
        }
    }

    // Get emails from specific Gmail folder
    async getEmailsFromFolder(folder, limit = 10) {
        try {
            if (!this.credentials) {
                throw new Error('Email credentials not set. Please configure Gmail App Password.');
            }

            console.log(`📬 Getting emails from ${folder}...`);
            
            const requestData = {
                email: this.credentials.email,
                password: this.credentials.password,
                limit: limit
            };
            
            const response = await fetch(`${this.apiBaseUrl}/email/${folder}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log(`✅ Retrieved ${result.total_count} emails from ${folder}`);
            return result;
            
        } catch (error) {
            console.error(`❌ ${folder} email fetch failed:`, error);
            throw error;
        }
    }

    // Get inbox emails
    async getInboxEmails(limit = 10) {
        return this.getEmailsFromFolder('inbox', limit);
    }

    // Get sent emails
    async getSentEmails(limit = 10) {
        return this.getEmailsFromFolder('sent', limit);
    }

    // Get trash emails
    async getTrashEmails(limit = 10) {
        return this.getEmailsFromFolder('trash', limit);
    }

    // Get draft emails
    async getDraftEmails(limit = 10) {
        return this.getEmailsFromFolder('drafts', limit);
    }

    // List available folders
    async listFolders() {
        try {
            if (!this.credentials) {
                throw new Error('Email credentials not set. Please configure Gmail App Password.');
            }

            const requestData = {
                email: this.credentials.email,
                password: this.credentials.password
            };
            
            const response = await fetch(`${this.apiBaseUrl}/email/folders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log('✅ Retrieved Gmail folders');
            return result;
            
        } catch (error) {
            console.error('❌ Folder list failed:', error);
            throw error;
        }
    }

    // Receive only QuMail encrypted emails
    async receiveQuMailEmails(limit = 10) {
        try {
            if (!this.credentials) {
                throw new Error('Email credentials not set. Please configure Gmail App Password.');
            }

            console.log(`🔐 Receiving QuMail encrypted emails...`);
            
            const requestData = {
                email: this.credentials.email,
                password: this.credentials.password,
                limit: limit
            };
            
            const response = await fetch(`${this.apiBaseUrl}/email/receive/qumail`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log(`✅ Received ${result.total_count} QuMail emails`);
            return result;
            
        } catch (error) {
            console.error('❌ QuMail email receiving failed:', error);
            throw error;
        }
    }

    // Show credentials modal
    showCredentialsModal() {
        // Create modal HTML
        const modalHTML = `
            <div id="email-credentials-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                <div class="glass-card border border-violet-500/30 rounded-2xl p-6 max-w-md w-full mx-4">
                    <h3 class="text-xl font-bold text-violet-300 mb-4 flex items-center space-x-2">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                        <span>Gmail Configuration</span>
                    </h3>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-violet-300 text-sm font-medium mb-2">Gmail Address</label>
                            <input id="gmail-address" type="email" placeholder="your.email@gmail.com" 
                                   class="w-full bg-black/30 border border-violet-500/30 rounded-xl px-4 py-2 text-white placeholder-violet-400 focus:border-violet-500 focus:outline-none">
                        </div>
                        
                        <div>
                            <label class="block text-violet-300 text-sm font-medium mb-2">App Password</label>
                            <input id="gmail-password" type="password" placeholder="16-character app password" 
                                   class="w-full bg-black/30 border border-violet-500/30 rounded-xl px-4 py-2 text-white placeholder-violet-400 focus:border-violet-500 focus:outline-none">
                        </div>
                        
                        <div class="text-xs text-violet-400 bg-violet-500/10 rounded-xl p-3">
                            <strong>Setup Instructions:</strong><br>
                            1. Enable 2-Factor Authentication on Gmail<br>
                            2. Go to Google Account → Security → App passwords<br>
                            3. Generate password for "QuMail"<br>
                            4. Use the 16-character password above
                        </div>
                        
                        <div class="flex space-x-3 pt-2">
                            <button id="save-credentials" class="flex-1 bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white py-2 px-4 rounded-xl font-medium transition-all duration-200">
                                Save & Connect
                            </button>
                            <button id="cancel-credentials" class="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-xl font-medium transition-all duration-200">
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Add event listeners
        const modal = document.getElementById('email-credentials-modal');
        const saveBtn = document.getElementById('save-credentials');
        const cancelBtn = document.getElementById('cancel-credentials');
        const emailInput = document.getElementById('gmail-address');
        const passwordInput = document.getElementById('gmail-password');
        
        saveBtn.addEventListener('click', () => {
            const email = emailInput.value.trim();
            const password = passwordInput.value.trim();
            
            if (!email || !password) {
                alert('Please enter both email and app password');
                return;
            }
            
            this.setCredentials(email, password);
            modal.remove();
            
            // Show success message
            this.showNotification('✅ Gmail credentials configured successfully!', 'success');
        });
        
        cancelBtn.addEventListener('click', () => {
            modal.remove();
        });
        
        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                modal.remove();
            }
        });
    }

    // Show notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 glass-card border border-violet-500/30 rounded-xl p-4 text-white max-w-sm transform transition-all duration-300 ${
            type === 'success' ? 'border-green-500/30 bg-green-500/10' : 
            type === 'error' ? 'border-red-500/30 bg-red-500/10' : 
            'border-violet-500/30'
        }`;
        notification.innerHTML = message;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    // Check if connected and has credentials
    isReady() {
        return this.isConnected && this.credentials;
    }
}

// Initialize Email Integration
const emailIntegration = new QuMailEmailIntegration();

// Expose globally for frontend integration
window.emailIntegration = emailIntegration;

// Replace mock encryption with real email sending
if (window.guiTester && window.guiTester.mockEncryption) {
    console.log('🔄 Replacing mock encryption with real email sending...');
    
    const originalEncryptMessage = window.guiTester.mockEncryption.encryptMessage;
    
    window.guiTester.mockEncryption.encryptMessage = async (formData, consumedKeyId) => {
        // Check if email credentials are set
        if (!emailIntegration.isReady()) {
            console.log('⚠️ Email credentials not set - showing configuration modal...');
            emailIntegration.showCredentialsModal();
            
            // Return mock result while waiting for credentials
            return originalEncryptMessage(formData, consumedKeyId);
        }
        
        // Use real email sending
        console.log('📧 Using real email sending via SMTP...');
        return await emailIntegration.sendEncryptedEmail(formData);
    };
    
    console.log('✅ Mock encryption replaced with real email sending');
}

// Email configuration will be handled by the profile icon

console.log(`
📧 QuMail Email Integration Initialized
📡 Backend API: ${emailIntegration.apiBaseUrl}
🚀 Ready for Real Email Sending & Receiving
⚡ Supports Gmail SMTP/IMAP with App Passwords
`);

// Listen for credentials from main process (Electron)
if (typeof require !== 'undefined') {
    try {
        const { ipcRenderer } = require('electron');
        ipcRenderer.on('user-credentials', (event, credentials) => {
            console.log('🔐 Auto-setting credentials from login:', credentials.email);
            emailIntegration.setCredentials(credentials.email, credentials.password);
        });
    } catch (e) {
        // Not in Electron environment
        console.log('🌐 Running in browser mode');
    }
}

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { QuMailEmailIntegration };
}
