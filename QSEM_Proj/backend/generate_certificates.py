import os
import datetime
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class QuMailCertificateGenerator:
    """Generate mTLS certificates for QuMail secure communication"""
    
    def __init__(self, cert_dir="certs"):
        """Initialize certificate generator"""
        self.cert_dir = cert_dir
        self.backend = default_backend()
        
        # Create certificates directory
        os.makedirs(cert_dir, exist_ok=True)
        
    def generate_ca_certificate(self):
        """Generate Certificate Authority (CA) certificate"""
        print("🔐 Generating Certificate Authority (CA)...")
        
        # Generate CA private key
        ca_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,  # High security for ISRO
            backend=self.backend
        )
        
        # Create CA certificate
        ca_name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Karnataka"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Bengaluru"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ISRO QuMail Project"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Quantum Communications"),
            x509.NameAttribute(NameOID.COMMON_NAME, "QuMail Root CA"),
        ])
        
        ca_cert = x509.CertificateBuilder().subject_name(
            ca_name
        ).issuer_name(
            ca_name  # Self-signed
        ).public_key(
            ca_private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now(datetime.timezone.utc)
        ).not_valid_after(
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650)  # 10 years
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,  # CA can sign certificates
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_private_key.public_key()),
            critical=False,
        ).sign(ca_private_key, hashes.SHA256(), self.backend)
        
        # Save CA certificate and private key
        with open(os.path.join(self.cert_dir, "ca.crt"), "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
            
        with open(os.path.join(self.cert_dir, "ca.key"), "wb") as f:
            f.write(ca_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        print(f"✅ CA Certificate generated: {self.cert_dir}/ca.crt")
        print(f"✅ CA Private Key generated: {self.cert_dir}/ca.key")
        
        return ca_cert, ca_private_key
    
    def generate_server_certificate(self, ca_cert, ca_private_key):
        """Generate server certificate signed by CA"""
        print("🖥️ Generating Server Certificate...")
        
        # Generate server private key
        server_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=self.backend
        )
        
        # Create server certificate
        server_name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Karnataka"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Bengaluru"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ISRO QuMail Project"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "QKD API Server"),
            x509.NameAttribute(NameOID.COMMON_NAME, "qumail-server"),
        ])
        
        server_cert = x509.CertificateBuilder().subject_name(
            server_name
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            server_private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now(datetime.timezone.utc)
        ).not_valid_after(
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)  # 1 year
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,
            ]),
            critical=True,
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("qumail-server"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv4Address("0.0.0.0")),
            ]),
            critical=False,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(server_private_key.public_key()),
            critical=False,
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_private_key.public_key()),
            critical=False,
        ).sign(ca_private_key, hashes.SHA256(), self.backend)
        
        # Save server certificate and private key
        with open(os.path.join(self.cert_dir, "server.crt"), "wb") as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))
            
        with open(os.path.join(self.cert_dir, "server.key"), "wb") as f:
            f.write(server_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        print(f"✅ Server Certificate generated: {self.cert_dir}/server.crt")
        print(f"✅ Server Private Key generated: {self.cert_dir}/server.key")
        
        return server_cert, server_private_key
    
    def generate_client_certificate(self, ca_cert, ca_private_key, client_name="qumail-client"):
        """Generate client certificate signed by CA"""
        print(f"👤 Generating Client Certificate: {client_name}...")
        
        # Generate client private key
        client_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=self.backend
        )
        
        # Create client certificate
        client_cert_name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Karnataka"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Bengaluru"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ISRO QuMail Project"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "QKD API Client"),
            x509.NameAttribute(NameOID.COMMON_NAME, client_name),
        ])
        
        client_cert = x509.CertificateBuilder().subject_name(
            client_cert_name
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            client_private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now(datetime.timezone.utc)
        ).not_valid_after(
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)  # 1 year
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(client_private_key.public_key()),
            critical=False,
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_private_key.public_key()),
            critical=False,
        ).sign(ca_private_key, hashes.SHA256(), self.backend)
        
        # Save client certificate and private key
        client_cert_file = os.path.join(self.cert_dir, f"{client_name}.crt")
        client_key_file = os.path.join(self.cert_dir, f"{client_name}.key")
        
        with open(client_cert_file, "wb") as f:
            f.write(client_cert.public_bytes(serialization.Encoding.PEM))
            
        with open(client_key_file, "wb") as f:
            f.write(client_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        print(f"✅ Client Certificate generated: {client_cert_file}")
        print(f"✅ Client Private Key generated: {client_key_file}")
        
        return client_cert, client_private_key
    
    def generate_all_certificates(self):
        """Generate complete certificate chain for mTLS"""
        print("🔒 Generating QuMail mTLS Certificate Chain")
        print("=" * 50)
        
        # Generate CA
        ca_cert, ca_private_key = self.generate_ca_certificate()
        
        # Generate server certificate
        server_cert, server_private_key = self.generate_server_certificate(ca_cert, ca_private_key)
        
        # Generate client certificates
        client_cert, client_private_key = self.generate_client_certificate(ca_cert, ca_private_key, "qumail-client")
        alice_cert, alice_private_key = self.generate_client_certificate(ca_cert, ca_private_key, "alice")
        bob_cert, bob_private_key = self.generate_client_certificate(ca_cert, ca_private_key, "bob")
        
        # Create certificate bundle for easy distribution
        print("\n📦 Creating Certificate Bundles...")
        
        # Server bundle (server cert + CA cert)
        with open(os.path.join(self.cert_dir, "server-bundle.crt"), "wb") as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
        
        # Client bundle (client cert + CA cert)  
        with open(os.path.join(self.cert_dir, "client-bundle.crt"), "wb") as f:
            f.write(client_cert.public_bytes(serialization.Encoding.PEM))
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
            
        print(f"✅ Server Bundle: {self.cert_dir}/server-bundle.crt")
        print(f"✅ Client Bundle: {self.cert_dir}/client-bundle.crt")
        
        print("\n🎉 mTLS Certificate Generation Complete!")
        print("=" * 50)
        print("📋 Generated Files:")
        for file in os.listdir(self.cert_dir):
            if file.endswith(('.crt', '.key')):
                print(f"   • {self.cert_dir}/{file}")
        
        print("\n🔐 Security Information:")
        print("   • Key Size: 4096-bit RSA")
        print("   • Hash Algorithm: SHA-256")
        print("   • CA Validity: 10 years")
        print("   • Server/Client Validity: 1 year")
        print("   • Compliant with ETSI GS QKD 014")
        
        return {
            "ca_cert": ca_cert,
            "ca_key": ca_private_key,
            "server_cert": server_cert,
            "server_key": server_private_key,
            "client_cert": client_cert,
            "client_key": client_private_key
        }

def main():
    """Generate all certificates for QuMail mTLS"""
    
    print("QuMail mTLS Certificate Generator")
    print("ISRO Smart India Hackathon 2025")
    print("Quantum-Secure Email Communication System")
    print()
    
    generator = QuMailCertificateGenerator()
    certificates = generator.generate_all_certificates()
    
    print("\n🚀 Ready for mTLS-secured QuMail deployment!")
    print("🇮🇳 JAI HIND!")
    
    return certificates

if __name__ == "__main__":
    main()
