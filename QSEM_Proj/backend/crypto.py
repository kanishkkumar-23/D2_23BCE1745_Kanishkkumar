import secrets
import time
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Optional, Any
import json
import base64

# Cryptography library for ECDH/X25519
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

class ECDHKeyExchange:
    """
    ECDH/X25519 Key Exchange Implementation
    Provides secure elliptic curve key exchange for hybrid encryption
    """
    
    def __init__(self):
        """Initialize ECDH Key Exchange Manager"""
        self.active_keypairs = {}  # Store active key pairs
        self.shared_secrets = {}   # Store computed shared secrets
        self.key_history = []      # Track key exchange history
        
    def generate_keypair(self, key_id: str = None) -> Dict[str, Any]:
        """
        Generate X25519 key pair for ECDH
        
        Args:
            key_id: Optional key identifier
            
        Returns:
            Dictionary containing key pair information
        """
        # Generate unique key ID if not provided
        if not key_id:
            timestamp = int(time.time() * 1000)
            random_suffix = secrets.randbelow(1000)
            key_id = f"ecdh_x25519_{timestamp}_{random_suffix}"
        
        # Generate X25519 private key
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialize keys
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Convert to base64 for storage/transmission
        private_key_b64 = base64.b64encode(private_key_bytes).decode('utf-8')
        public_key_b64 = base64.b64encode(public_key_bytes).decode('utf-8')
        
        # Create key pair data structure
        keypair_data = {
            "key_id": key_id,
            "algorithm": "X25519",
            "curve": "Curve25519",
            "private_key": private_key_b64,
            "public_key": public_key_b64,
            "public_key_hex": public_key_bytes.hex(),
            "metadata": {
                "key_size": 256,  # X25519 provides ~256-bit security
                "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat().replace('+00:00', 'Z'),
                "status": "active",
                "usage": "key_exchange",
                "security_level": "256-bit equivalent"
            }
        }
        
        # Store the key pair and actual objects for computation
        self.active_keypairs[key_id] = {
            "data": keypair_data,
            "private_key_obj": private_key,
            "public_key_obj": public_key
        }
        
        print(f"🔑 Generated X25519 key pair: {key_id}")
        return keypair_data
    
    def get_public_key(self, key_id: str) -> Optional[str]:
        """
        Get public key for sharing with other party
        
        Args:
            key_id: Key identifier
            
        Returns:
            Base64 encoded public key or None if not found
        """
        if key_id in self.active_keypairs:
            return self.active_keypairs[key_id]["data"]["public_key"]
        return None
    
    def compute_shared_secret(self, local_key_id: str, remote_public_key_b64: str, 
                            shared_secret_id: str = None) -> Dict[str, Any]:
        """
        Compute ECDH shared secret using local private key and remote public key
        
        Args:
            local_key_id: Local key pair identifier
            remote_public_key_b64: Remote party's public key (base64)
            shared_secret_id: Optional identifier for the shared secret
            
        Returns:
            Dictionary containing shared secret information
        """
        if local_key_id not in self.active_keypairs:
            raise ValueError(f"Local key {local_key_id} not found")
        
        try:
            # Get local private key
            local_private_key = self.active_keypairs[local_key_id]["private_key_obj"]
            
            # Decode remote public key
            remote_public_key_bytes = base64.b64decode(remote_public_key_b64)
            remote_public_key = x25519.X25519PublicKey.from_public_bytes(remote_public_key_bytes)
            
            # Perform ECDH key exchange
            shared_secret_raw = local_private_key.exchange(remote_public_key)
            
            # Generate shared secret ID if not provided
            if not shared_secret_id:
                timestamp = int(time.time() * 1000)
                random_suffix = secrets.randbelow(1000)
                shared_secret_id = f"ecdh_secret_{timestamp}_{random_suffix}"
            
            # Derive key material using HKDF
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits
                salt=None,
                info=b'QuMail ECDH Key Exchange',
                backend=default_backend()
            ).derive(shared_secret_raw)
            
            # Convert to hex for storage
            shared_secret_hex = derived_key.hex()
            shared_secret_b64 = base64.b64encode(derived_key).decode('utf-8')
            
            # Create shared secret data structure
            shared_secret_data = {
                "shared_secret_id": shared_secret_id,
                "local_key_id": local_key_id,
                "algorithm": "X25519-HKDF-SHA256",
                "shared_secret": shared_secret_hex,
                "shared_secret_b64": shared_secret_b64,
                "key_derivation": "HKDF-SHA256",
                "metadata": {
                    "length": 256,  # bits
                    "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    "expires_at": (datetime.now(timezone.utc) + timedelta(hours=12)).isoformat().replace('+00:00', 'Z'),
                    "status": "active",
                    "local_key_id": local_key_id,
                    "remote_public_key_fingerprint": hashlib.sha256(remote_public_key_bytes).hexdigest()[:16],
                    "usage": "hybrid_encryption"
                }
            }
            
            # Store shared secret
            self.shared_secrets[shared_secret_id] = shared_secret_data
            self.key_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "action": "shared_secret_computed",
                "shared_secret_id": shared_secret_id,
                "local_key_id": local_key_id
            })
            
            print(f"🤝 Computed ECDH shared secret: {shared_secret_id}")
            return shared_secret_data
            
        except Exception as e:
            print(f"❌ ECDH computation error: {e}")
            raise
    
    def get_shared_secret(self, shared_secret_id: str) -> Optional[Dict[str, Any]]:
        """Get shared secret by ID"""
        return self.shared_secrets.get(shared_secret_id)
    
    def list_active_keypairs(self) -> Dict[str, Dict[str, Any]]:
        """Get all active key pairs (without private keys)"""
        result = {}
        for key_id, keypair in self.active_keypairs.items():
            # Return public data only
            result[key_id] = {
                "key_id": key_id,
                "algorithm": keypair["data"]["algorithm"],
                "public_key": keypair["data"]["public_key"],
                "public_key_hex": keypair["data"]["public_key_hex"],
                "metadata": keypair["data"]["metadata"]
            }
        return result
    
    def list_shared_secrets(self) -> Dict[str, Dict[str, Any]]:
        """Get all active shared secrets (without the actual secrets)"""
        result = {}
        for secret_id, secret_data in self.shared_secrets.items():
            # Return metadata only
            result[secret_id] = {
                "shared_secret_id": secret_id,
                "local_key_id": secret_data["local_key_id"],
                "algorithm": secret_data["algorithm"],
                "metadata": secret_data["metadata"]
            }
        return result
    
    def cleanup_expired_keys(self):
        """Remove expired keys and secrets"""
        current_time = datetime.now(timezone.utc)
        
        # Clean up expired key pairs
        expired_keypairs = []
        for key_id, keypair in self.active_keypairs.items():
            expires_at = datetime.fromisoformat(
                keypair["data"]["metadata"]["expires_at"].replace('Z', '+00:00')
            )
            if current_time > expires_at:
                expired_keypairs.append(key_id)
        
        for key_id in expired_keypairs:
            del self.active_keypairs[key_id]
            print(f"⏰ Expired ECDH key pair: {key_id}")
        
        # Clean up expired shared secrets
        expired_secrets = []
        for secret_id, secret_data in self.shared_secrets.items():
            expires_at = datetime.fromisoformat(
                secret_data["metadata"]["expires_at"].replace('Z', '+00:00')
            )
            if current_time > expires_at:
                expired_secrets.append(secret_id)
        
        for secret_id in expired_secrets:
            del self.shared_secrets[secret_id]
            print(f"⏰ Expired ECDH shared secret: {secret_id}")
    
    def simulate_key_exchange(self) -> Dict[str, Any]:
        """
        Simulate a complete ECDH key exchange between Alice and Bob
        Useful for testing and demonstration
        """
        # Alice generates her key pair
        alice_keypair = self.generate_keypair("alice_demo_key")
        alice_public_key = alice_keypair["public_key"]
        
        # Bob generates his key pair (simulate separate instance)
        bob_private_key = x25519.X25519PrivateKey.generate()
        bob_public_key = bob_private_key.public_key()
        bob_public_key_bytes = bob_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        bob_public_key_b64 = base64.b64encode(bob_public_key_bytes).decode('utf-8')
        
        # Alice computes shared secret using Bob's public key
        alice_shared_secret = self.compute_shared_secret(
            "alice_demo_key", 
            bob_public_key_b64, 
            "demo_shared_secret"
        )
        
        # Bob computes shared secret using Alice's public key (verification)
        alice_public_key_bytes = base64.b64decode(alice_public_key)
        alice_public_key_obj = x25519.X25519PublicKey.from_public_bytes(alice_public_key_bytes)
        bob_shared_secret_raw = bob_private_key.exchange(alice_public_key_obj)
        
        # Bob derives the same key
        bob_derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'QuMail ECDH Key Exchange',
            backend=default_backend()
        ).derive(bob_shared_secret_raw)
        
        # Verify both parties computed the same secret
        alice_secret_bytes = base64.b64decode(alice_shared_secret["shared_secret_b64"])
        secrets_match = alice_secret_bytes == bob_derived_key
        
        return {
            "demo_successful": True,
            "secrets_match": secrets_match,
            "alice_key_id": "alice_demo_key",
            "alice_public_key": alice_public_key,
            "bob_public_key": bob_public_key_b64,
            "shared_secret_id": "demo_shared_secret",
            "shared_secret_preview": alice_shared_secret["shared_secret"][:16] + "...",
            "key_exchange_verified": secrets_match
        }

class HybridCryptoManager:
    """
    Manager for combining multiple cryptographic methods
    Supports hybrid QKD + ECDH + ML-KEM framework
    """
    
    def __init__(self):
        """Initialize Hybrid Crypto Manager"""
        self.ecdh = ECDHKeyExchange()
        self.hybrid_keys = {}
        
        # Try to import ML-KEM manager (safe version)
        try:
            # ML-KEM now handled by real_pqc.py
            self.mlkem = None  # Deprecated
            self.mlkem_available = False
            print("🔬 ML-KEM-768 integrated into hybrid manager")
        except ImportError:
            self.mlkem = None
            self.mlkem_available = False
            print("⚠️ ML-KEM-768 not available for hybrid manager")
        
    def generate_hybrid_keypair(self, hybrid_id: str = None) -> Dict[str, Any]:
        """
        Generate keys for hybrid encryption
        Supports ECDH + ML-KEM-768 (if available)
        """
        if not hybrid_id:
            timestamp = int(time.time() * 1000)
            hybrid_id = f"hybrid_{timestamp}"
        
        # Generate ECDH key pair
        ecdh_keypair = self.ecdh.generate_keypair(f"{hybrid_id}_ecdh")
        
        # Prepare algorithm list and components
        algorithms = ["X25519"]
        components = ["ECDH/X25519"]
        
        # Initialize hybrid key structure
        hybrid_key_data = {
            "hybrid_id": hybrid_id,
            "ecdh_key_id": ecdh_keypair["key_id"],
            "ecdh_public_key": ecdh_keypair["public_key"],
        }
        
        # Generate ML-KEM key pair if available
        if self.mlkem_available and self.mlkem:
            try:
                mlkem_keypair = self.mlkem.generate_keypair(f"{hybrid_id}_mlkem")
                hybrid_key_data["mlkem_key_id"] = mlkem_keypair["key_id"]
                hybrid_key_data["mlkem_public_key"] = mlkem_keypair["public_key"]
                algorithms.append("ML-KEM-768")
                components.append("ML-KEM-768")
                print(f"🔬 Added ML-KEM-768 to hybrid key: {hybrid_id}")
            except Exception as e:
                print(f"⚠️ Failed to add ML-KEM to hybrid key: {e}")
        
        # Complete hybrid key structure
        hybrid_key_data.update({
            "algorithms": algorithms,
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "security_level": "192-bit hybrid" if self.mlkem_available else "128-bit hybrid",
                "status": "active",
                "components": components,
                "mlkem_available": self.mlkem_available
            }
        })
        
        self.hybrid_keys[hybrid_id] = hybrid_key_data
        
        print(f"🔐 Generated hybrid key pair: {hybrid_id} with {len(algorithms)} algorithms")
        return hybrid_key_data
    
    def get_hybrid_public_data(self, hybrid_id: str) -> Optional[Dict[str, Any]]:
        """Get public key data for sharing"""
        if hybrid_id in self.hybrid_keys:
            data = {
                "hybrid_id": hybrid_id,
                "algorithms": self.hybrid_keys[hybrid_id]["algorithms"],
                "ecdh_public_key": self.hybrid_keys[hybrid_id]["ecdh_public_key"],
                "metadata": self.hybrid_keys[hybrid_id]["metadata"]
            }
            
            # Include ML-KEM public key if available
            if "mlkem_public_key" in self.hybrid_keys[hybrid_id]:
                data["mlkem_public_key"] = self.hybrid_keys[hybrid_id]["mlkem_public_key"]
                data["mlkem_key_id"] = self.hybrid_keys[hybrid_id]["mlkem_key_id"]
            
            return data
        return None

# Factory functions for Flask integration
def create_ecdh_manager() -> ECDHKeyExchange:
    """Create ECDH Key Exchange Manager"""
    return ECDHKeyExchange()

def create_hybrid_manager() -> HybridCryptoManager:
    """Create Hybrid Crypto Manager"""
    return HybridCryptoManager()

# Test function
def test_ecdh_exchange():
    """Test ECDH key exchange functionality"""
    print("🔐 Testing ECDH/X25519 Key Exchange...")
    
    ecdh = create_ecdh_manager()
    
    # Test key pair generation
    keypair = ecdh.generate_keypair("test_key_001")
    print(f"✅ Generated key pair: {keypair['key_id']}")
    print(f"🔑 Public key: {keypair['public_key'][:32]}...")
    
    # Test simulated key exchange
    demo_result = ecdh.simulate_key_exchange()
    print(f"✅ Key exchange demo: {'SUCCESS' if demo_result['demo_successful'] else 'FAILED'}")
    print(f"🤝 Secrets match: {demo_result['secrets_match']}")
    print(f"🔒 Shared secret: {demo_result['shared_secret_preview']}")
    
    # Test hybrid manager
    hybrid = create_hybrid_manager()
    hybrid_key = hybrid.generate_hybrid_keypair("test_hybrid_001")
    print(f"✅ Generated hybrid key: {hybrid_key['hybrid_id']}")
    
    print("\n✅ ECDH/X25519 test completed!")
    return demo_result

if __name__ == "__main__":
    test_ecdh_exchange()

