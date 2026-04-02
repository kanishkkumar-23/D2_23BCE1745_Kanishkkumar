import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class QuMailMessageFlowTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_results = []
        self.alice_email = "alice@isro.gov.in"
        self.bob_email = "bob@isro.gov.in"
        
    def run_complete_message_flow_test(self):
        """Run complete Alice-to-Bob message flow for all security levels"""
        print("🚀 QuMail Alice-to-Bob Message Flow Test")
        print("=" * 60)
        print(f"👤 Alice: {self.alice_email}")
        print(f"👤 Bob: {self.bob_email}")
        print("=" * 60)
        
        # Test message for all levels
        test_messages = {
            1: "🔐 TOP SECRET: Chandrayaan-4 mission data - Level 1 Quantum Secure",
            2: "🔒 CONFIDENTIAL: ISRO satellite communication protocols - Level 2 Quantum-aided",
            3: "🛡️ SENSITIVE: Future quantum-resistant communications - Level 3 Hybrid PQC", 
            4: "📧 STANDARD: Regular ISRO team coordination - Level 4 Classical"
        }
        
        # Test all 4 security levels
        for level in range(1, 5):
            print(f"\n🔍 Testing Level {level} Message Flow")
            print("-" * 40)
            
            message = test_messages[level]
            subject = f"QuMail Test Level {level} - {datetime.now().strftime('%H:%M:%S')}"
            
            # Step 1: Alice encrypts message
            encrypted_data = self.alice_encrypts_message(level, message, subject)
            if not encrypted_data:
                continue
                
            # Step 2: Simulate message transmission (network delay)
            self.simulate_network_transmission(level)
            
            # Step 3: Bob decrypts message
            decrypted_data = self.bob_decrypts_message(encrypted_data)
            if not decrypted_data:
                continue
                
            # Step 4: Verify message integrity
            self.verify_message_integrity(level, message, decrypted_data)
            
        # Print final results
        self.print_test_summary()
        
    def alice_encrypts_message(self, level: int, message: str, subject: str) -> Dict[str, Any]:
        """Alice encrypts a message using specified security level"""
        print(f"   🔐 Alice encrypting with Level {level}...")
        
        try:
            request_data = {
                "plaintext": message,
                "security_level": level,
                "sender": self.alice_email,
                "recipient": self.bob_email,
                "subject": subject,
                "attachments": []
            }
            
            response = requests.post(
                f"{self.base_url}/api/encrypt",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    metadata = result['encrypted_data']['metadata']
                    print(f"   ✅ Encrypted: {metadata['algorithm']}")
                    print(f"   🔑 Key Source: {metadata['key_source']}")
                    print(f"   🛡️ Quantum Resistant: {metadata['quantum_resistant']}")
                    print(f"   📋 ETSI Compliant: {metadata['etsi_compliant']}")
                    print(f"   📦 Ciphertext Length: {len(result['encrypted_data']['ciphertext'])} chars")
                    
                    self.test_results.append({
                        'level': level,
                        'action': 'encrypt',
                        'status': 'success',
                        'algorithm': metadata['algorithm'],
                        'key_source': metadata['key_source'],
                        'quantum_resistant': metadata['quantum_resistant'],
                        'etsi_compliant': metadata['etsi_compliant']
                    })
                    
                    return result['encrypted_data']
                else:
                    print(f"   ❌ Encryption failed: {result.get('error')}")
                    self.test_results.append({
                        'level': level,
                        'action': 'encrypt', 
                        'status': 'failed',
                        'error': result.get('error')
                    })
                    return None
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                self.test_results.append({
                    'level': level,
                    'action': 'encrypt',
                    'status': 'failed', 
                    'error': f"HTTP {response.status_code}"
                })
                return None
                
        except Exception as e:
            print(f"   ❌ Encryption error: {e}")
            self.test_results.append({
                'level': level,
                'action': 'encrypt',
                'status': 'failed',
                'error': str(e)
            })
            return None
    
    def simulate_network_transmission(self, level: int):
        """Simulate network transmission with realistic delays"""
        print(f"   🌐 Transmitting Level {level} message...")
        
        # Simulate different transmission times based on security level
        transmission_delays = {
            1: 0.5,  # Quantum secure - fastest (OTP)
            2: 0.8,  # Quantum-aided - medium (hybrid)
            3: 1.2,  # Hybrid PQC - slower (complex crypto)
            4: 0.3   # Classical - fastest (simple AES)
        }
        
        delay = transmission_delays.get(level, 0.5)
        time.sleep(delay)
        
        print(f"   ✅ Message transmitted in {delay:.1f}s")
    
    def bob_decrypts_message(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Bob decrypts the received message"""
        print(f"   🔓 Bob decrypting message...")
        
        try:
            request_data = {
                "encrypted_data": encrypted_data
            }
            
            response = requests.post(
                f"{self.base_url}/api/decrypt",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    plaintext = result['plaintext']
                    metadata = result['metadata']
                    
                    print(f"   ✅ Decrypted successfully")
                    print(f"   📄 Message length: {len(plaintext)} characters")
                    print(f"   ⏱️ Decryption time: {metadata.get('decryption_timestamp', 'N/A')}")
                    
                    self.test_results.append({
                        'level': encrypted_data['metadata']['security_level'],
                        'action': 'decrypt',
                        'status': 'success',
                        'message_length': len(plaintext)
                    })
                    
                    return {
                        'plaintext': plaintext,
                        'metadata': metadata,
                        'original_metadata': encrypted_data['metadata']
                    }
                else:
                    print(f"   ❌ Decryption failed: {result.get('error')}")
                    self.test_results.append({
                        'level': encrypted_data['metadata']['security_level'],
                        'action': 'decrypt',
                        'status': 'failed',
                        'error': result.get('error')
                    })
                    return None
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                self.test_results.append({
                    'level': encrypted_data['metadata']['security_level'],
                    'action': 'decrypt',
                    'status': 'failed',
                    'error': f"HTTP {response.status_code}"
                })
                return None
                
        except Exception as e:
            print(f"   ❌ Decryption error: {e}")
            self.test_results.append({
                'level': encrypted_data['metadata']['security_level'],
                'action': 'decrypt',
                'status': 'failed',
                'error': str(e)
            })
            return None
    
    def verify_message_integrity(self, level: int, original_message: str, decrypted_data: Dict[str, Any]):
        """Verify that the decrypted message matches the original"""
        print(f"   🔍 Verifying message integrity...")
        
        decrypted_message = decrypted_data['plaintext']
        original_metadata = decrypted_data['original_metadata']
        
        # Check message content
        if decrypted_message == original_message:
            print(f"   ✅ Message integrity verified - Perfect match!")
            print(f"   📝 Original: {original_message[:50]}...")
            print(f"   📝 Decrypted: {decrypted_message[:50]}...")
            
            # Additional verification
            print(f"   🔐 Security Level: {original_metadata['security_level']}")
            print(f"   🛡️ Quantum Resistant: {original_metadata['quantum_resistant']}")
            print(f"   📋 ETSI Compliant: {original_metadata['etsi_compliant']}")
            
            self.test_results.append({
                'level': level,
                'action': 'verify',
                'status': 'success',
                'message_match': True,
                'security_level': original_metadata['security_level'],
                'quantum_resistant': original_metadata['quantum_resistant'],
                'etsi_compliant': original_metadata['etsi_compliant']
            })
        else:
            print(f"   ❌ Message integrity FAILED!")
            print(f"   📝 Original: {original_message}")
            print(f"   📝 Decrypted: {decrypted_message}")
            
            self.test_results.append({
                'level': level,
                'action': 'verify',
                'status': 'failed',
                'message_match': False,
                'original_length': len(original_message),
                'decrypted_length': len(decrypted_message)
            })
    
    def print_test_summary(self):
        """Print comprehensive test results summary"""
        print("\n" + "=" * 60)
        print("📊 ALICE-TO-BOB MESSAGE FLOW TEST RESULTS")
        print("=" * 60)
        
        # Group results by level
        level_results = {}
        for result in self.test_results:
            level = result['level']
            if level not in level_results:
                level_results[level] = {'encrypt': None, 'decrypt': None, 'verify': None}
            level_results[level][result['action']] = result
        
        # Print results for each level
        for level in sorted(level_results.keys()):
            results = level_results[level]
            print(f"\n🔍 Level {level} Results:")
            print("-" * 30)
            
            # Encryption results
            if results['encrypt']:
                encrypt_result = results['encrypt']
                status_icon = "✅" if encrypt_result['status'] == 'success' else "❌"
                print(f"   {status_icon} Encryption: {encrypt_result['status']}")
                if encrypt_result['status'] == 'success':
                    print(f"      Algorithm: {encrypt_result['algorithm']}")
                    print(f"      Key Source: {encrypt_result['key_source']}")
                    print(f"      Quantum Resistant: {encrypt_result['quantum_resistant']}")
                    print(f"      ETSI Compliant: {encrypt_result['etsi_compliant']}")
                else:
                    print(f"      Error: {encrypt_result.get('error', 'Unknown')}")
            
            # Decryption results
            if results['decrypt']:
                decrypt_result = results['decrypt']
                status_icon = "✅" if decrypt_result['status'] == 'success' else "❌"
                print(f"   {status_icon} Decryption: {decrypt_result['status']}")
                if decrypt_result['status'] == 'success':
                    print(f"      Message Length: {decrypt_result['message_length']} chars")
                else:
                    print(f"      Error: {decrypt_result.get('error', 'Unknown')}")
            
            # Verification results
            if results['verify']:
                verify_result = results['verify']
                status_icon = "✅" if verify_result['status'] == 'success' else "❌"
                print(f"   {status_icon} Verification: {verify_result['status']}")
                if verify_result['status'] == 'success':
                    print(f"      Message Match: {verify_result['message_match']}")
                    print(f"      Security Level: {verify_result['security_level']}")
                else:
                    print(f"      Message Match: {verify_result['message_match']}")
        
        # Overall statistics
        print("\n" + "-" * 60)
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['status'] == 'success'])
        failed_tests = total_tests - successful_tests
        
        print(f"📈 OVERALL STATISTICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Successful: {successful_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📊 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Level-specific success rates
        print(f"\n📊 LEVEL-SPECIFIC SUCCESS RATES:")
        for level in sorted(level_results.keys()):
            level_tests = [r for r in self.test_results if r['level'] == level]
            level_success = len([r for r in level_tests if r['status'] == 'success'])
            level_total = len(level_tests)
            success_rate = (level_success/level_total)*100 if level_total > 0 else 0
            print(f"   Level {level}: {level_success}/{level_total} ({success_rate:.1f}%)")
        
        # Final verdict
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! QuMail message flow is working perfectly!")
            print(f"🚀 Ready for ISRO Smart India Hackathon 2025 demo!")
        else:
            print(f"\n⚠️ {failed_tests} tests failed. Please check the issues above.")
        
        print("=" * 60)

def main():
    """Main test execution"""
    print("🔐 QuMail Alice-to-Bob Message Flow Test Suite")
    print("ISRO Smart India Hackathon 2025")
    print("Testing complete encryption/decryption flow for all security levels")
    print()
    
    tester = QuMailMessageFlowTester()
    tester.run_complete_message_flow_test()

if __name__ == "__main__":
    main()
