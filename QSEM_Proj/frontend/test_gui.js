class QuMailGUITester {
    constructor() {
        this.testResults = [];
        this.mockEncryption = new MockEncryptionEngine();
        this.initializeTestSuite();
    }

    initializeTestSuite() {
        console.log('🧪 QuMail GUI Testing Suite Initialized');
        console.log('📧 Testing email composition and quantum encryption simulation');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupTestHandlers());
        } else {
            this.setupTestHandlers();
        }
    }

    setupTestHandlers() {
        // Test handlers disabled - real compose manager handles sending
        console.log('⚠️ Test handlers disabled for production - using real email sending');

        // Add test controls to the interface
        this.addTestControls();
    }

    addTestControls() {
        // Test controls are disabled for production

        // Create modal dialog
        const testModal = document.createElement('div');
        testModal.id = 'test-modal';
        testModal.className = 'fixed inset-0 bg-black/70 backdrop-blur-lg z-50 hidden flex items-center justify-center';
        testModal.innerHTML = `
            <div class="glass-dark border border-violet-500/30 rounded-2xl p-6 mx-4 w-full max-w-md">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-violet-300 font-bold text-lg flex items-center space-x-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                        <span>Test Controls</span>
                    </h3>
                    <button id="close-test-panel" class="text-gray-400 hover:text-white text-2xl">&times;</button>
                </div>
                
                <div class="space-y-3">
                    <button id="auto-fill-test" class="w-full px-3 py-2 bg-violet-500/20 text-violet-300 rounded text-sm hover:bg-violet-500/30 transition-colors">
                        📝 Auto-Fill Test Data
                    </button>
                    <button id="test-all-levels" class="w-full px-3 py-2 bg-green-500/20 text-green-300 rounded text-sm hover:bg-green-500/30 transition-colors">
                        🔒 Test All Security Levels
                    </button>
                    <button id="view-test-log" class="w-full px-3 py-2 bg-blue-500/20 text-blue-300 rounded text-sm hover:bg-blue-500/30 transition-colors">
                        📊 View Test Log
                    </button>
                    <button id="test-animation" class="w-full px-3 py-2 bg-purple-500/20 text-purple-300 rounded text-sm hover:bg-purple-500/30 transition-colors">
                        🎭 Test Animation
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(testModal);

        // Add modal control event listeners
        testButton.addEventListener('click', () => {
            testModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        });

        document.getElementById('close-test-panel').addEventListener('click', () => {
            testModal.classList.add('hidden');
            document.body.style.overflow = '';
        });

        // Close on background click
        testModal.addEventListener('click', (e) => {
            if (e.target === testModal) {
                testModal.classList.add('hidden');
                document.body.style.overflow = '';
            }
        });

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !testModal.classList.contains('hidden')) {
                testModal.classList.add('hidden');
                document.body.style.overflow = '';
            }
        });

        // Add event listeners for test controls
        document.getElementById('auto-fill-test')?.addEventListener('click', () => this.autoFillTestData());
        document.getElementById('test-all-levels')?.addEventListener('click', () => this.testAllSecurityLevels());
        document.getElementById('view-test-log')?.addEventListener('click', () => this.showTestLog());
        document.getElementById('test-animation')?.addEventListener('click', () => this.testHybridAnimation());
    }

    autoFillTestData() {
        const testData = {
            recipient: 'dr.raj.patel@isro.gov.in',
            subject: 'Quantum-Secure Mission Communication - SIH2025',
            message: `Dear Dr. Patel,

This is a test of the QuMail quantum-secure email system developed for the ISRO Smart India Hackathon 2025.

Key Features Being Tested:
- ✅ QKD (Quantum Key Distribution) Integration
- ✅ ETSI GS QKD 014 Compliance
- ✅ Multi-level Hybrid Encryption
- ✅ BB84 Protocol Implementation
- ✅ Post-Quantum Cryptography (ML-KEM-768)

Security Level: ${this.getCurrentSecurityLevel()}
Quantum Keys Available: ${qkdManager ? qkdManager.keyCache.size : 'N/A'}

Best regards,
QuMail Development Team
ISRO SIH 2025`
        };

        // Fill the form fields
        this.fillFormData(testData);
        
        console.log('📝 Auto-filled test data:', testData);
        this.logTest('Auto-fill', 'SUCCESS', 'Test data populated in form fields');
    }

    fillFormData(data) {
        const recipientField = document.getElementById('recipient') || document.querySelector('input[placeholder*="recipient"]');
        const subjectField = document.getElementById('subject') || document.querySelector('input[placeholder*="subject"]');
        const messageField = document.getElementById('message') || document.querySelector('textarea');

        if (recipientField) recipientField.value = data.recipient;
        if (subjectField) subjectField.value = data.subject;
        if (messageField) messageField.value = data.message;

        // Trigger input events to ensure UI updates
        [recipientField, subjectField, messageField].forEach(field => {
            if (field) {
                field.dispatchEvent(new Event('input', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }

    simulateEmailSending() {
        console.log('🚀 Starting email sending simulation...');
        
        // Collect form data
        const formData = this.collectFormData();
        
        // Validate form data
        const validation = this.validateFormData(formData);
        if (!validation.isValid) {
            this.showError(validation.errors);
            return;
        }

        // Show sending animation
        this.showSendingAnimation();

        // Simulate encryption process
        setTimeout(() => {
            this.performMockEncryption(formData);
        }, 500);
    }

    collectFormData() {
        const recipientField = document.getElementById('recipient') || document.querySelector('input[placeholder*="recipient"]');
        const subjectField = document.getElementById('subject') || document.querySelector('input[placeholder*="subject"]');
        const messageField = document.getElementById('message') || document.querySelector('textarea');
        const securityLevel = this.getCurrentSecurityLevel();

        return {
            recipient: recipientField?.value || '',
            subject: subjectField?.value || '',
            message: messageField?.value || '',
            securityLevel: securityLevel,
            timestamp: new Date().toISOString(),
            sessionId: `qumail_${Date.now()}`
        };
    }

    validateFormData(data) {
        const errors = [];
        
        if (!data.recipient.trim()) {
            errors.push('Recipient email is required');
        } else if (!this.isValidEmail(data.recipient)) {
            errors.push('Invalid recipient email format');
        }
        
        if (!data.subject.trim()) {
            errors.push('Subject is required');
        }
        
        if (!data.message.trim()) {
            errors.push('Message content is required');
        }

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    getCurrentSecurityLevel() {
        const levelSelect = document.getElementById('encryption-level');
        if (levelSelect) {
            return levelSelect.value;
        }
        
        // Try to get from current encryption status display
        const statusText = document.querySelector('.encryption-status')?.textContent;
        if (statusText?.includes('Level 1')) return '1';
        if (statusText?.includes('Level 2')) return '2';
        if (statusText?.includes('Level 3')) return '3';
        if (statusText?.includes('Level 4')) return '4';
        
        return '2'; // Default to Level 2
    }

    performMockEncryption(formData) {
        console.log('🔐 Starting mock encryption process...');
        
        // Check if QKD keys should be used based on security level
        const shouldUseQKD = formData.securityLevel === '1' || formData.securityLevel === '2';
        let consumedKeyId = null;
        
        if (shouldUseQKD && window.qkdManager) {
            // Trigger hybrid key animation for quantum security levels
            this.showHybridKeyAnimation(formData.securityLevel);
            
            // Try to consume a QKD key for Level 1 & 2
            const availableKeys = Array.from(window.qkdManager.keyCache.keys());
            if (availableKeys.length > 0) {
                consumedKeyId = availableKeys[0];
                window.qkdManager.consumeQuantumKey(consumedKeyId);
                console.log(`🔑 QKD Key CONSUMED for Level ${formData.securityLevel}: ${consumedKeyId}`);
            } else {
                console.log('⚠️ No QKD keys available - falling back to classical encryption');
            }
        } else {
            console.log(`💡 QKD keys PRESERVED for Level ${formData.securityLevel} - using ${formData.securityLevel === '3' ? 'Post-Quantum' : 'Classical'} encryption`);
        }
        
        const encryptionResult = this.mockEncryption.encryptMessage(formData, consumedKeyId);
        
        // Log detailed results
        console.log('📊 Encryption Results:', encryptionResult);
        
        // Simulate network sending (only if no animation is playing)
        if (!shouldUseQKD || !window.hybridAnimator) {
            this.simulateNetworkSending(formData, encryptionResult);
        } else {
            // Wait for animation to complete before continuing
            document.addEventListener('animationComplete', () => {
                this.simulateNetworkSending(formData, encryptionResult);
            }, { once: true });
        }
    }

    showHybridKeyAnimation(securityLevel) {
        if (!window.showHybridKeyAnimation) {
            console.log('⚠️ Hybrid key animation not available');
            return;
        }

        // Determine which key types to show based on security level
        let keyTypes = [];
        
        switch(securityLevel) {
            case '1': // Quantum Secure - QKD only for demo
                keyTypes = ['qkd'];
                break;
            case '2': // Quantum-aided AES - QKD + classical
                keyTypes = ['qkd', 'ecdh'];
                break;
            case '3': // Hybrid PQC (though this won't trigger in current flow)
                keyTypes = ['mlkem', 'ecdh'];
                break;
            default:
                keyTypes = ['qkd', 'mlkem', 'ecdh']; // Full hybrid
        }

        console.log(`🎭 Triggering hybrid key animation for Level ${securityLevel} with keys:`, keyTypes);
        window.showHybridKeyAnimation(keyTypes);
    }

    simulateNetworkSending(formData, encryptionResult) {
        console.log('📡 Simulating network transmission...');
        
        // Simulate network delay
        setTimeout(() => {
            const success = Math.random() > 0.1; // 90% success rate
            
            if (success) {
                this.handleSendSuccess(formData, encryptionResult);
            } else {
                this.handleSendError('Network transmission failed');
            }
        }, 1000 + Math.random() * 1000); // 1-2 second delay
    }

    handleSendSuccess(formData, encryptionResult) {
        console.log('✅ Email sent successfully!');
        
        const result = {
            status: 'SUCCESS',
            messageId: `msg_${Date.now()}`,
            recipient: formData.recipient,
            subject: formData.subject,
            securityLevel: formData.securityLevel,
            encryptionType: encryptionResult.algorithm,
            keyId: encryptionResult.keyId,
            timestamp: new Date().toISOString()
        };

        this.logTest('Email Send', 'SUCCESS', result);
        this.showSuccessMessage(result);
        this.clearForm();
    }

    handleSendError(error) {
        console.error('❌ Email sending failed:', error);
        this.logTest('Email Send', 'FAILED', error);
        this.showError([error]);
    }

    showSendingAnimation() {
        const sendButton = document.querySelector('.bg-gradient-to-r');
        if (sendButton) {
            const originalText = sendButton.innerHTML;
            sendButton.innerHTML = `
                <div class="flex items-center space-x-2">
                    <div class="quantum-loader" style="width: 16px; height: 16px; border-width: 2px;"></div>
                    <span>Encrypting & Sending...</span>
                </div>
            `;
            sendButton.disabled = true;
            
            // Reset button after animation
            setTimeout(() => {
                sendButton.innerHTML = originalText;
                sendButton.disabled = false;
            }, 3000);
        }
    }

    showSuccessMessage(result) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 glass-dark border border-green-500/30 p-4 rounded-xl z-50 animate-key-generation';
        notification.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                </div>
                <div>
                    <div class="text-green-400 font-medium">Email Sent Successfully!</div>
                    <div class="text-sm text-gray-400">ID: ${result.messageId}</div>
                    <div class="text-xs text-gray-500">${result.encryptionType} encryption</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove notification after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    showError(errors) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 glass-dark border border-red-500/30 p-4 rounded-xl z-50 animate-key-generation';
        notification.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </div>
                <div>
                    <div class="text-red-400 font-medium">Sending Failed</div>
                    ${errors.map(error => `<div class="text-sm text-gray-400">${error}</div>`).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove notification after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    clearForm() {
        const recipientField = document.getElementById('recipient') || document.querySelector('input[placeholder*="recipient"]');
        const subjectField = document.getElementById('subject') || document.querySelector('input[placeholder*="subject"]');
        const messageField = document.getElementById('message') || document.querySelector('textarea');

        if (recipientField) recipientField.value = '';
        if (subjectField) subjectField.value = '';
        if (messageField) messageField.value = '';
    }

    testAllSecurityLevels() {
        console.log('🔬 Testing all security levels...');
        
        const levels = [
            { level: '1', name: 'Quantum Secure' },
            { level: '2', name: 'Quantum-aided AES' },
            { level: '3', name: 'Hybrid PQC' },
            { level: '4', name: 'No Quantum Security' }
        ];

        levels.forEach((levelInfo, index) => {
            setTimeout(() => {
                this.testSecurityLevel(levelInfo);
            }, index * 2000); // 2 second intervals
        });
    }

    testSecurityLevel(levelInfo) {
        console.log(`🔐 Testing Security Level ${levelInfo.level}: ${levelInfo.name}`);
        
        // Set security level
        const levelSelect = document.getElementById('encryption-level');
        if (levelSelect) {
            levelSelect.value = levelInfo.level;
            levelSelect.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // Fill test data
        this.autoFillTestData();
        
        // Simulate sending
        setTimeout(() => {
            this.simulateEmailSending();
        }, 500);
    }

    logTest(testName, status, details) {
        const testResult = {
            timestamp: new Date().toISOString(),
            test: testName,
            status: status,
            details: details
        };
        
        this.testResults.push(testResult);
        console.log(`📋 Test: ${testName} - ${status}`, details);
    }

    showTestLog() {
        console.log('📊 Complete Test Log:');
        console.table(this.testResults);
        
        // Also show in a modal
        const logModal = document.createElement('div');
        logModal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center';
        logModal.innerHTML = `
            <div class="glass-dark border border-violet-500/30 rounded-2xl p-6 m-4 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-xl font-bold text-violet-300">🧪 Test Results Log</h2>
                    <button class="close-log p-2 hover:bg-white/10 rounded-lg">
                        <svg class="w-5 h-5 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <div class="space-y-2">
                    ${this.testResults.map(result => `
                        <div class="glass p-3 rounded">
                            <div class="flex justify-between items-center">
                                <span class="text-violet-300 font-medium">${result.test}</span>
                                <span class="text-${result.status === 'SUCCESS' ? 'green' : 'red'}-400 text-sm">${result.status}</span>
                            </div>
                            <div class="text-xs text-gray-400">${result.timestamp}</div>
                            <div class="text-sm text-gray-300 mt-1">${JSON.stringify(result.details, null, 2)}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(logModal);
        
        logModal.querySelector('.close-log').addEventListener('click', () => {
            logModal.remove();
        });
    }

    testHybridAnimation() {
        console.log('🎭 Testing Hybrid Key Animation...');
        
        if (!window.showHybridKeyAnimation) {
            console.error('❌ Hybrid animation not available');
            this.showError(['Hybrid animation system not loaded']);
            return;
        }

        // Test full hybrid animation (all three key types)
        console.log('🚀 Starting full hybrid animation demo...');
        window.showHybridKeyAnimation(['qkd', 'mlkem', 'ecdh']);
        
        this.logTest('Hybrid Animation', 'SUCCESS', 'Full QKD+ML-KEM+ECDH animation triggered');
    }
}

// Mock Encryption Engine
class MockEncryptionEngine {
    encryptMessage(formData, consumedKeyId = null) {
        const algorithms = {
            '1': 'Quantum-OTP',
            '2': 'AES-256-QKD',
            '3': 'ML-KEM-768-Hybrid',
            '4': 'AES-256-Classical'
        };

        const algorithm = algorithms[formData.securityLevel] || 'AES-256-QKD';
        
        // Mock encryption process
        const encryptedContent = this.generateMockEncryption(formData.message, algorithm);
        
        return {
            algorithm: algorithm,
            keyId: consumedKeyId || this.generateKeyId(formData.securityLevel),
            encryptedMessage: encryptedContent,
            integrity: this.generateIntegrityHash(),
            timestamp: new Date().toISOString(),
            qkdKeyUsed: !!consumedKeyId
        };
    }

    generateMockEncryption(message, algorithm) {
        // Create realistic looking encrypted content
        const base64Chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        let encrypted = '';
        
        for (let i = 0; i < message.length * 2; i++) {
            encrypted += base64Chars[Math.floor(Math.random() * base64Chars.length)];
        }
        
        return `${algorithm}:${encrypted}`;
    }

    generateKeyId(securityLevel) {
        const prefixes = {
            '1': 'qkd',
            '2': 'qkd_aes',
            '3': 'mlkem',
            '4': 'classical'
        };
        
        const prefix = prefixes[securityLevel] || 'qkd_aes';
        return `${prefix}_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
    }

    generateIntegrityHash() {
        // Generate mock SHA-256 hash
        const hexChars = '0123456789abcdef';
        let hash = '';
        for (let i = 0; i < 64; i++) {
            hash += hexChars[Math.floor(Math.random() * 16)];
        }
        return hash;
    }
}

// Initialize the test suite
const guiTester = new QuMailGUITester();

// Export for console access
window.quMailTester = guiTester;

console.log('🎯 GUI Testing loaded! Use window.quMailTester for manual control');
