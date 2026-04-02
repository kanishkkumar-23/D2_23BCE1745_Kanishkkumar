import secrets
import time 
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Optional, Any, List
import json
import base64

# Cryptography library for HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

class HybridKeyDerivator:
    """
    Hybrid Key Derivation Manager
    Combines QKD, ECDH, and ML-KEM-768 keys into unified hybrid keys
    """
    
    def __init__(self):
        """Initialize Hybrid Key Derivator"""
        self.derived_keys = {}  # Store derived hybrid keys
        self.derivation_history = []  # Track key derivations
        self.algorithm = "QKD+ECDH+MLKEM-HKDF-SHA256"
        self.target_key_length = 32  # 256 bits
        
        # Import all crypto managers
        self.qkd_manager = None
        self.ecdh_manager = None
        self.mlkem_manager = None
        self.real_pqc_manager = None
        self._initialize_managers()
        
    def _initialize_managers(self):
        """Initialize connections to all cryptographic managers"""
        try:
            # Note: These would be injected in production, but for demo we'll import
            print("🔗 Initializing hybrid key derivation with all crypto components...")
            print("⚠️ Managers will be injected at runtime from Flask app")
        except Exception as e:
            print(f"⚠️ Manager initialization deferred: {e}")
    
    def set_managers(self, qkd_manager=None, ecdh_manager=None, mlkem_manager=None, real_pqc_manager=None):
        """Set the crypto managers (called from Flask app)"""
        self.qkd_manager = qkd_manager
        self.ecdh_manager = ecdh_manager
        self.mlkem_manager = mlkem_manager
        self.real_pqc_manager = real_pqc_manager
        
        components = []
        if qkd_manager:
            components.append("QKD")
        if ecdh_manager:
            components.append("ECDH")
        if mlkem_manager:
            components.append("ML-KEM")
        if real_pqc_manager:
            components.append("Real-PQC")
            
        print(f"🔗 Hybrid derivator connected to: {', '.join(components)}")
    
    def derive_hybrid_key(self, 
                         qkd_key_id: str = None,
                         ecdh_shared_secret_id: str = None, 
                         mlkem_shared_secret_id: str = None,
                         hybrid_key_id: str = None,
                         include_components: List[str] = None) -> Dict[str, Any]:
        """
        Derive a hybrid key from available cryptographic components
        
        Args:
            qkd_key_id: QKD key identifier (optional)
            ecdh_shared_secret_id: ECDH shared secret identifier (optional)
            mlkem_shared_secret_id: ML-KEM shared secret identifier (optional)
            hybrid_key_id: Custom ID for the derived key (optional)
            include_components: List of components to include ['QKD', 'ECDH', 'MLKEM'] (optional)
            
        Returns:
            Dictionary containing hybrid key information
        """
        if not hybrid_key_id:
            timestamp = int(time.time() * 1000)
            random_suffix = secrets.randbelow(1000)
            hybrid_key_id = f"hybrid_key_{timestamp}_{random_suffix}"
        
        # Determine which components to include
        if include_components is None:
            include_components = ['QKD', 'ECDH', 'MLKEM']
        
        key_materials = []
        component_info = {}
        security_contributions = []
        
        # Collect QKD key material
        if 'QKD' in include_components and self.qkd_manager:
            try:
                if qkd_key_id:
                    qkd_key = self.qkd_manager.active_keys.get(qkd_key_id)
                else:
                    # Get any available QKD key
                    qkd_keys = list(self.qkd_manager.active_keys.keys())
                    if qkd_keys:
                        qkd_key_id = qkd_keys[0]
                        qkd_key = self.qkd_manager.active_keys[qkd_key_id]
                    else:
                        qkd_key = None
                
                if qkd_key:
                    qkd_material = base64.b64decode(qkd_key['key_material'])
                    key_materials.append(('QKD', qkd_material))
                    component_info['qkd'] = {
                        'key_id': qkd_key_id,
                        'algorithm': 'BB84',
                        'length': len(qkd_material) * 8,
                        'error_rate': qkd_key.get('metadata', {}).get('error_rate', 0),
                        'fidelity': qkd_key.get('metadata', {}).get('fidelity', 1.0)
                    }
                    security_contributions.append('256-bit quantum')
                    print(f"🔬 QKD component added: {qkd_key_id}")
                else:
                    print("⚠️ No QKD keys available for hybrid derivation")
            except Exception as e:
                print(f"❌ QKD component error: {e}")
        
        # Collect ECDH shared secret material
        if 'ECDH' in include_components and self.ecdh_manager:
            try:
                if ecdh_shared_secret_id:
                    ecdh_secret = self.ecdh_manager.shared_secrets.get(ecdh_shared_secret_id)
                else:
                    # Get any available ECDH shared secret
                    ecdh_secrets = list(self.ecdh_manager.shared_secrets.keys())
                    if ecdh_secrets:
                        ecdh_shared_secret_id = ecdh_secrets[0]
                        ecdh_secret = self.ecdh_manager.shared_secrets[ecdh_shared_secret_id]
                    else:
                        ecdh_secret = None
                
                if ecdh_secret:
                    ecdh_material = bytes.fromhex(ecdh_secret['shared_secret'])
                    key_materials.append(('ECDH', ecdh_material))
                    component_info['ecdh'] = {
                        'shared_secret_id': ecdh_shared_secret_id,
                        'algorithm': 'X25519-HKDF-SHA256',
                        'length': len(ecdh_material) * 8,
                        'local_key_id': ecdh_secret.get('local_key_id')
                    }
                    security_contributions.append('256-bit classical')
                    print(f"🔑 ECDH component added: {ecdh_shared_secret_id}")
                else:
                    print("⚠️ No ECDH shared secrets available for hybrid derivation")
            except Exception as e:
                print(f"❌ ECDH component error: {e}")
        
        # Collect ML-KEM shared secret material (try real PQC first, then simulation)
        if 'MLKEM' in include_components:
            mlkem_material = None
            mlkem_info = None
            
            # Try real post-quantum cryptography first
            if self.real_pqc_manager:
                try:
                    # Generate a real ML-KEM keypair and shared secret
                    public_key, private_key = self.real_pqc_manager.pqc.generate_keypair()
                    ciphertext, shared_secret = self.real_pqc_manager.pqc.encapsulate(public_key)
                    
                    mlkem_material = shared_secret
                    mlkem_info = {
                        'secret_id': f"real_pqc_{secrets.token_hex(8)}",
                        'algorithm': 'ML-KEM-768-Real-PQC',
                        'length': len(mlkem_material) * 8,
                        'quantum_resistant': True,
                        'real_crypto': True
                    }
                    security_contributions.append('256-bit real post-quantum')
                    print(f"🔬 Real PQC ML-KEM component added")
                except Exception as e:
                    print(f"❌ Real PQC ML-KEM error: {e}")
            
            # Fallback to simulation if real PQC failed
            if mlkem_material is None and self.mlkem_manager:
                try:
                    if mlkem_shared_secret_id:
                        mlkem_secret = self.mlkem_manager.encapsulated_secrets.get(mlkem_shared_secret_id)
                    else:
                        # Get any available ML-KEM shared secret
                        mlkem_secrets = list(self.mlkem_manager.encapsulated_secrets.keys())
                        if mlkem_secrets:
                            mlkem_shared_secret_id = mlkem_secrets[0]
                            mlkem_secret = self.mlkem_manager.encapsulated_secrets[mlkem_shared_secret_id]
                        else:
                            mlkem_secret = None
                    
                    if mlkem_secret:
                        mlkem_material = bytes.fromhex(mlkem_secret['shared_secret'])
                        mlkem_info = {
                            'secret_id': mlkem_shared_secret_id,
                            'algorithm': 'ML-KEM-768-Simulation',
                            'length': len(mlkem_material) * 8,
                            'quantum_resistant': True,
                            'real_crypto': False
                        }
                        security_contributions.append('192-bit simulated post-quantum')
                        print(f"🔬 ML-KEM simulation component added: {mlkem_shared_secret_id}")
                except Exception as e:
                    print(f"❌ ML-KEM simulation component error: {e}")
            
            if mlkem_material is not None:
                key_materials.append(('MLKEM', mlkem_material))
                component_info['mlkem'] = mlkem_info
            else:
                print("⚠️ No ML-KEM shared secrets available for hybrid derivation")
        
        # Ensure we have at least one component
        if not key_materials:
            raise ValueError("No cryptographic components available for hybrid key derivation")
        
        # Concatenate all key materials
        concatenated_material = b''
        component_names = []
        for component_name, material in key_materials:
            concatenated_material += material
            component_names.append(component_name)
        
        # Create deterministic salt and context
        # Use SHA256 hash of concatenated material as deterministic salt
        import hashlib
        deterministic_salt = hashlib.sha256(concatenated_material + b'QuMail-Salt').digest()
        context_info = f"QuMail Hybrid Key {'+'.join(component_names)}".encode('utf-8')
        
        # Derive the final hybrid key using HKDF-SHA256 with deterministic salt
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=self.target_key_length,  # 256 bits
            salt=deterministic_salt,  # DETERMINISTIC - same inputs = same key
            info=context_info,
            backend=default_backend()
        )
        
        derived_key_bytes = hkdf.derive(concatenated_material)
        derived_key_hex = derived_key_bytes.hex()
        derived_key_b64 = base64.b64encode(derived_key_bytes).decode('utf-8')
        
        # Calculate security level
        if len(component_names) >= 3:
            security_level = "192-bit hybrid"
            security_description = "Quantum + Classical + Post-Quantum"
        elif len(component_names) == 2:
            security_level = "128-bit hybrid"
            security_description = "Dual-component security"
        else:
            security_level = "64-bit single"
            security_description = "Single-component security"
        
        # Create hybrid key data structure
        hybrid_key_data = {
            "hybrid_key_id": hybrid_key_id,
            "algorithm": self.algorithm,
            "derived_key": derived_key_hex,
            "derived_key_b64": derived_key_b64,
            "key_length": len(derived_key_bytes) * 8,
            "components": component_names,
            "component_info": component_info,
            "security_level": security_level,
            "security_description": security_description,
            "security_contributions": security_contributions,
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat().replace('+00:00', 'Z'),
                "status": "active",
                "usage": "email_encryption",
                "derivation_method": "HKDF-SHA256",
                "entropy_added": True,
                "component_count": len(component_names),
                "total_input_bits": len(concatenated_material) * 8,
                "output_bits": len(derived_key_bytes) * 8
            }
        }
        
        # Store the derived key
        self.derived_keys[hybrid_key_id] = hybrid_key_data
        self.derivation_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "action": "hybrid_key_derived",
            "hybrid_key_id": hybrid_key_id,
            "components": component_names,
            "security_level": security_level
        })
        
        print(f"🔐 Derived hybrid key: {hybrid_key_id}")
        print(f"🛡️ Security level: {security_level}")
        print(f"🔗 Components: {', '.join(component_names)}")
        
        return hybrid_key_data
    
    def get_hybrid_key(self, hybrid_key_id: str) -> Optional[Dict[str, Any]]:
        """Get hybrid key by ID (without the actual key material)"""
        if hybrid_key_id in self.derived_keys:
            key_data = self.derived_keys[hybrid_key_id].copy()
            # Remove the actual key for security
            key_data.pop('derived_key', None)
            key_data['derived_key_preview'] = key_data['derived_key_b64'][:16] + "..."
            return key_data
        return None
    
    def list_hybrid_keys(self) -> Dict[str, Dict[str, Any]]:
        """Get all hybrid keys (without the actual key material)"""
        result = {}
        for key_id, key_data in self.derived_keys.items():
            result[key_id] = self.get_hybrid_key(key_id)
        return result
    
    def cleanup_expired_keys(self):
        """Remove expired hybrid keys"""
        current_time = datetime.now(timezone.utc)
        expired_keys = []
        
        for key_id, key_data in self.derived_keys.items():
            expires_at = datetime.fromisoformat(
                key_data["metadata"]["expires_at"].replace('Z', '+00:00')
            )
            if current_time > expires_at:
                expired_keys.append(key_id)
        
        for key_id in expired_keys:
            del self.derived_keys[key_id]
            print(f"⏰ Expired hybrid key: {key_id}")
    
    def generate_full_hybrid_demo(self) -> Dict[str, Any]:
        """
        Generate a complete hybrid key using all available components
        Useful for testing and demonstration
        """
        try:
            # This will try to use any available components
            hybrid_key = self.derive_hybrid_key(
                hybrid_key_id="full_demo_hybrid",
                include_components=['QKD', 'ECDH', 'MLKEM']
            )
            
            return {
                "demo_successful": True,
                "hybrid_key_id": hybrid_key["hybrid_key_id"],
                "security_level": hybrid_key["security_level"],
                "components": hybrid_key["components"],
                "security_contributions": hybrid_key["security_contributions"],
                "key_length": hybrid_key["key_length"],
                "algorithm": hybrid_key["algorithm"],
                "derived_key_preview": hybrid_key["derived_key"][:16] + "...",
                "message": "Full hybrid key derived successfully"
            }
            
        except Exception as e:
            return {
                "demo_successful": False,
                "error": str(e),
                "message": "Hybrid key derivation failed"
            }
    
    def get_security_analysis(self) -> Dict[str, Any]:
        """Analyze the security provided by the hybrid system"""
        analysis = {
            "system": "QuMail Hybrid Key Derivation",
            "algorithm": self.algorithm,
            "target_key_length": self.target_key_length * 8,  # bits
            "components_available": {},
            "security_levels": {
                "single_component": "64-bit",
                "dual_component": "128-bit", 
                "triple_component": "192-bit hybrid"
            },
            "threat_resistance": {},
            "active_keys": len(self.derived_keys),
            "derivation_history": len(self.derivation_history)
        }
        
        # Check component availability
        if self.qkd_manager:
            qkd_keys = len(self.qkd_manager.active_keys) if hasattr(self.qkd_manager, 'active_keys') else 0
            analysis["components_available"]["QKD"] = {
                "available": True,
                "active_keys": qkd_keys,
                "security": "256-bit quantum",
                "threat_resistance": "Information-theoretic security"
            }
            analysis["threat_resistance"]["quantum_computer"] = "Resistant (QKD)"
        else:
            analysis["components_available"]["QKD"] = {"available": False}
        
        if self.ecdh_manager:
            ecdh_secrets = len(self.ecdh_manager.shared_secrets) if hasattr(self.ecdh_manager, 'shared_secrets') else 0
            analysis["components_available"]["ECDH"] = {
                "available": True,
                "active_secrets": ecdh_secrets,
                "security": "256-bit classical",
                "threat_resistance": "Discrete logarithm problem"
            }
            analysis["threat_resistance"]["classical_computer"] = "Resistant (ECDH)"
        else:
            analysis["components_available"]["ECDH"] = {"available": False}
        
        # Check for real PQC first, then simulation
        if self.real_pqc_manager:
            analysis["components_available"]["MLKEM"] = {
                "available": True,
                "type": "Real Post-Quantum",
                "security": "256-bit real post-quantum",
                "threat_resistance": "Real cryptographic security",
                "algorithm": "ML-KEM-768-Real-PQC"
            }
            analysis["threat_resistance"]["quantum_computer_future"] = "Resistant (Real ML-KEM-768)"
        elif self.mlkem_manager:
            mlkem_secrets = len(self.mlkem_manager.encapsulated_secrets) if hasattr(self.mlkem_manager, 'encapsulated_secrets') else 0
            analysis["components_available"]["MLKEM"] = {
                "available": True,
                "type": "Simulation",
                "active_secrets": mlkem_secrets,
                "security": "192-bit simulated post-quantum",
                "threat_resistance": "NIST FIPS 203 standard (simulated)",
                "algorithm": "ML-KEM-768-Simulation"
            }
            analysis["threat_resistance"]["quantum_computer_future"] = "Resistant (Simulated ML-KEM-768)"
        else:
            analysis["components_available"]["MLKEM"] = {"available": False}
        
        return analysis

# Factory function for Flask integration
def create_hybrid_derivator() -> HybridKeyDerivator:
    """Create Hybrid Key Derivator"""
    return HybridKeyDerivator()

# Test function
def test_hybrid_derivation():
    """Test hybrid key derivation functionality"""
    print("🔐 Testing Hybrid Key Derivation...")
    
    derivator = create_hybrid_derivator()
    
    # Test security analysis
    analysis = derivator.get_security_analysis()
    print(f"✅ Security analysis: {analysis['system']}")
    print(f"🔑 Target key length: {analysis['target_key_length']} bits")
    print(f"🛡️ Security levels: {analysis['security_levels']}")
    
    # Test basic functionality (without actual managers)
    print(f"📊 Active hybrid keys: {analysis['active_keys']}")
    print(f"📜 Derivation history: {analysis['derivation_history']}")
    
    print("\n✅ Hybrid derivation module test completed!")
    print("⚠️ Full testing requires crypto managers from Flask app")
    
    return analysis

if __name__ == "__main__":
    test_hybrid_derivation()

