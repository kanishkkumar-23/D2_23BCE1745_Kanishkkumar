class QuMailLiveTester {
    constructor() {
        this.testResults = [];
        this.apiBaseUrl = 'http://localhost:5000';
    }

    async runAllTests() {
        console.log('🚀 QuMail Live Integration Test Suite');
        console.log('=' + '='.repeat(50));
        
        // Test 1: Backend Connection
        await this.testBackendConnection();
        
        // Test 2: Real Encryption Manager
        await this.testRealEncryption();
        
        // Test 3: All Security Levels
        await this.testAllSecurityLevels();
        
        // Test 4: QKD Integration
        await this.testQKDIntegration();
        
        // Test 5: UI Components
        this.testUIComponents();
        
        // Print Results
        this.printResults();
    }

    async testBackendConnection() {
        console.log('\n🔍 Test 1: Backend Connection');
        console.log('-'.repeat(30));
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/`);
            const data = await response.json();
            
            if (response.ok) {
                console.log('✅ Backend API connected');
                console.log(`📊 System: ${data.system || 'QuMail Backend'}`);
                this.testResults.push(['Backend Connection', 'PASS']);
            } else {
                console.log('❌ Backend API error:', response.status);
                this.testResults.push(['Backend Connection', 'FAIL']);
            }
        } catch (error) {
            console.log('❌ Backend connection failed:', error.message);
            this.testResults.push(['Backend Connection', 'FAIL']);
        }
    }

    async testRealEncryption() {
        console.log('\n🔍 Test 2: Real Encryption Manager');
        console.log('-'.repeat(35));
        
        if (window.realEncryption) {
            console.log('✅ Real Encryption Manager found');
            
            const connected = window.realEncryption.isApiConnected();
            console.log(`🔗 API Connected: ${connected}`);
            
            const capabilities = window.realEncryption.getSystemCapabilities();
            console.log(`📊 Capabilities:`, capabilities);
            
            this.testResults.push(['Real Encryption Manager', connected ? 'PASS' : 'FAIL']);
        } else {
            console.log('❌ Real Encryption Manager not found');
            this.testResults.push(['Real Encryption Manager', 'FAIL']);
        }
    }

    async testAllSecurityLevels() {
        console.log('\n🔍 Test 3: All Security Levels');
        console.log('-'.repeat(35));
        
        const testMessage = 'Live test message from QuMail frontend';
        
        for (let level = 1; level <= 4; level++) {
            try {
                console.log(`\n   Testing Level ${level}...`);
                
                const formData = {
                    message: testMessage,
                    securityLevel: level.toString(),
                    from: 'alice@isro.gov.in',
                    to: 'bob@isro.gov.in',
                    subject: `Live Test Level ${level}`
                };
                
                if (window.realEncryption) {
                    const result = await window.realEncryption.encryptMessage(formData);
                    
                    if (result.success) {
                        console.log(`   ✅ Level ${level}: ${result.algorithm}`);
                        console.log(`      🔑 Key: ${result.keyId}`);
                        console.log(`      🛡️ Quantum Resistant: ${result.quantum_resistant}`);
                        this.testResults.push([`Level ${level} Encryption`, 'PASS']);
                    } else {
                        console.log(`   ❌ Level ${level}: Encryption failed`);
                        this.testResults.push([`Level ${level} Encryption`, 'FAIL']);
                    }
                } else {
                    console.log(`   ⚠️ Level ${level}: Real encryption not available`);
                    this.testResults.push([`Level ${level} Encryption`, 'SKIP']);
                }
            } catch (error) {
                console.log(`   ❌ Level ${level}: ${error.message}`);
                this.testResults.push([`Level ${level} Encryption`, 'FAIL']);
            }
        }
    }

    async testQKDIntegration() {
        console.log('\n🔍 Test 4: QKD Integration');
        console.log('-'.repeat(30));
        
        if (window.qkdManager) {
            console.log('✅ QKD Manager found');
            
            try {
                // Test key generation
                const keyData = await window.qkdManager.generateNewQuantumKey();
                
                if (keyData && keyData.key_id) {
                    console.log(`✅ QKD Key generated: ${keyData.key_id}`);
                    console.log(`🔐 Protocol: ${keyData.metadata?.protocol || 'BB84'}`);
                    console.log(`📊 Security Level: ${keyData.metadata?.security_level || 'N/A'}`);
                    this.testResults.push(['QKD Integration', 'PASS']);
                } else {
                    console.log('❌ QKD Key generation failed');
                    this.testResults.push(['QKD Integration', 'FAIL']);
                }
            } catch (error) {
                console.log('❌ QKD test error:', error.message);
                this.testResults.push(['QKD Integration', 'FAIL']);
            }
        } else {
            console.log('❌ QKD Manager not found');
            this.testResults.push(['QKD Integration', 'FAIL']);
        }
    }

    testUIComponents() {
        console.log('\n🔍 Test 5: UI Components');
        console.log('-'.repeat(30));
        
        const components = [
            { id: 'encryption-level', name: 'Security Level Selector' },
            { id: 'generate-qkd-key', name: 'QKD Key Generator' },
            { id: 'quantum-keys-display', name: 'QKD Keys Display' },
            { id: 'security-bar', name: 'Security Gauge' },
            { id: 'send-email-btn', name: 'Send Email Button' }
        ];
        
        let foundComponents = 0;
        
        components.forEach(component => {
            const element = document.getElementById(component.id);
            if (element) {
                console.log(`✅ ${component.name}: Found`);
                foundComponents++;
            } else {
                console.log(`❌ ${component.name}: Not found`);
            }
        });
        
        const allFound = foundComponents === components.length;
        console.log(`📊 UI Components: ${foundComponents}/${components.length} found`);
        
        this.testResults.push(['UI Components', allFound ? 'PASS' : 'PARTIAL']);
    }

    printResults() {
        console.log('\n' + '='.repeat(60));
        console.log('📊 LIVE TEST RESULTS SUMMARY');
        console.log('='.repeat(60));
        
        let passed = 0;
        let failed = 0;
        let skipped = 0;
        
        this.testResults.forEach(([test, result]) => {
            const icon = result === 'PASS' ? '✅' : result === 'FAIL' ? '❌' : '⚠️';
            console.log(`${icon} ${test.padEnd(30)} ${result}`);
            
            if (result === 'PASS') passed++;
            else if (result === 'FAIL') failed++;
            else skipped++;
        });
        
        console.log('-'.repeat(60));
        console.log(`📈 TOTAL: ${this.testResults.length} tests`);
        console.log(`✅ PASSED: ${passed}`);
        console.log(`❌ FAILED: ${failed}`);
        if (skipped > 0) console.log(`⚠️ SKIPPED: ${skipped}`);
        
        if (failed === 0) {
            console.log('\n🎉 ALL TESTS PASSED! QuMail frontend is fully operational!');
        } else {
            console.log(`\n⚠️ ${failed} tests failed. Check the issues above.`);
        }
        
        console.log('='.repeat(60));
    }

    // Quick test methods for manual testing
    async quickEncryptTest(level = 2) {
        console.log(`🔐 Quick Encryption Test - Level ${level}`);
        
        const formData = {
            message: 'Quick test message',
            securityLevel: level.toString(),
            from: 'test@isro.gov.in',
            to: 'recipient@isro.gov.in',
            subject: 'Quick Test'
        };
        
        if (window.realEncryption) {
            try {
                const result = await window.realEncryption.encryptMessage(formData);
                console.log('✅ Encryption Result:', result);
                return result;
            } catch (error) {
                console.log('❌ Encryption failed:', error);
                return null;
            }
        } else {
            console.log('❌ Real encryption not available');
            return null;
        }
    }

    async quickQKDTest() {
        console.log('🔑 Quick QKD Test');
        
        if (window.qkdManager) {
            try {
                const keyData = await window.qkdManager.generateNewQuantumKey();
                console.log('✅ QKD Key:', keyData);
                return keyData;
            } catch (error) {
                console.log('❌ QKD failed:', error);
                return null;
            }
        } else {
            console.log('❌ QKD Manager not available');
            return null;
        }
    }
}

// Initialize the live tester
const liveTester = new QuMailLiveTester();

// Expose globally for manual testing
window.liveTester = liveTester;

console.log(`
🚀 QuMail Live Testing Suite Loaded
📝 Commands available:
   • liveTester.runAllTests() - Run complete test suite
   • liveTester.quickEncryptTest(level) - Quick encryption test
   • liveTester.quickQKDTest() - Quick QKD test
   
🎮 Usage:
   1. Open Developer Console (F12)
   2. Run: liveTester.runAllTests()
   3. Watch the results!
`);

// Auto-run if requested
if (window.location.search.includes('autotest')) {
    setTimeout(() => liveTester.runAllTests(), 2000);
}
