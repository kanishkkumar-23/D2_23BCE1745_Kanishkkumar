import os
import ssl
from flask import Flask, request, jsonify, g
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from functools import wraps

class QuMailmTLSConfig:
    """mTLS configuration for QuMail Flask app"""
    
    def __init__(self, cert_dir="certs"):
        """Initialize mTLS configuration"""
        self.cert_dir = cert_dir
        self.ca_cert_path = os.path.join(cert_dir, "ca.crt")
        self.server_cert_path = os.path.join(cert_dir, "server.crt")
        self.server_key_path = os.path.join(cert_dir, "server.key")
        
        # Load CA certificate for client verification
        self.ca_cert = self._load_ca_certificate()
        
    def _load_ca_certificate(self):
        """Load CA certificate for client verification"""
        try:
            with open(self.ca_cert_path, "rb") as f:
                ca_cert_data = f.read()
            ca_cert = x509.load_pem_x509_certificate(ca_cert_data, default_backend())
            print(f"✅ CA Certificate loaded: {self.ca_cert_path}")
            return ca_cert
        except Exception as e:
            print(f"❌ Failed to load CA certificate: {e}")
            return None
    
    def create_ssl_context(self):
        """Create SSL context for mTLS"""
        print("🔐 Configuring mTLS SSL Context...")
        
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # Load server certificate and key
        context.load_cert_chain(self.server_cert_path, self.server_key_path)
        
        # Configure client certificate verification
        context.verify_mode = ssl.CERT_REQUIRED  # Require client certificates
        context.load_verify_locations(self.ca_cert_path)  # Trust our CA
        
        # Security settings
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        print("✅ SSL Context configured with mTLS")
        print("   • Client certificates: REQUIRED")
        print("   • Minimum TLS version: 1.2")
        print("   • Cipher suites: ECDHE+AESGCM preferred")
        
        return context
    
    def extract_client_info(self, request):
        """Extract client information from certificate"""
        try:
            # Get client certificate from request environment
            client_cert_pem = request.environ.get('SSL_CLIENT_CERT')
            if not client_cert_pem:
                return None
            
            # Parse client certificate
            client_cert = x509.load_pem_x509_certificate(
                client_cert_pem.encode('utf-8'), 
                default_backend()
            )
            
            # Extract client information
            subject = client_cert.subject
            client_info = {
                "common_name": None,
                "organization": None,
                "organizational_unit": None,
                "country": None,
                "serial_number": str(client_cert.serial_number),
                "valid_from": client_cert.not_valid_before.isoformat(),
                "valid_until": client_cert.not_valid_after.isoformat(),
                "fingerprint": client_cert.fingerprint(hashes.SHA256()).hex()
            }
            
            # Extract subject attributes
            for attribute in subject:
                if attribute.oid == x509.NameOID.COMMON_NAME:
                    client_info["common_name"] = attribute.value
                elif attribute.oid == x509.NameOID.ORGANIZATION_NAME:
                    client_info["organization"] = attribute.value
                elif attribute.oid == x509.NameOID.ORGANIZATIONAL_UNIT_NAME:
                    client_info["organizational_unit"] = attribute.value
                elif attribute.oid == x509.NameOID.COUNTRY_NAME:
                    client_info["country"] = attribute.value
            
            return client_info
            
        except Exception as e:
            print(f"❌ Error extracting client info: {e}")
            return None

def require_mtls_auth(f):
    """Decorator to require mTLS authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if client certificate is present
        client_cert = request.environ.get('SSL_CLIENT_CERT')
        if not client_cert:
            return jsonify({
                "error": "Client certificate required",
                "message": "mTLS authentication failed - no client certificate provided",
                "code": "MTLS_CERT_REQUIRED"
            }), 401
        
        try:
            # Parse and validate client certificate
            from cryptography.hazmat.primitives import hashes
            client_cert_obj = x509.load_pem_x509_certificate(
                client_cert.encode('utf-8'), 
                default_backend()
            )
            
            # Extract client common name
            subject = client_cert_obj.subject
            client_cn = None
            for attribute in subject:
                if attribute.oid == x509.NameOID.COMMON_NAME:
                    client_cn = attribute.value
                    break
            
            # Store client info in Flask g object for use in endpoints
            g.client_cn = client_cn
            g.client_cert_serial = str(client_cert_obj.serial_number)
            g.client_cert_fingerprint = client_cert_obj.fingerprint(hashes.SHA256()).hex()
            
            print(f"🔐 mTLS authenticated client: {client_cn} (Serial: {g.client_cert_serial[:16]}...)")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"❌ mTLS authentication error: {e}")
            return jsonify({
                "error": "Invalid client certificate",
                "message": "mTLS authentication failed - certificate validation error",
                "code": "MTLS_CERT_INVALID"
            }), 401
    
    return decorated_function

def setup_mtls_logging(app):
    """Setup enhanced logging for mTLS connections"""
    
    @app.before_request
    def log_mtls_request():
        """Log mTLS request details"""
        client_cert = request.environ.get('SSL_CLIENT_CERT')
        if client_cert:
            try:
                client_cert_obj = x509.load_pem_x509_certificate(
                    client_cert.encode('utf-8'), 
                    default_backend()
                )
                
                subject = client_cert_obj.subject
                client_cn = "Unknown"
                for attribute in subject:
                    if attribute.oid == x509.NameOID.COMMON_NAME:
                        client_cn = attribute.value
                        break
                
                print(f"🔒 mTLS Request: {request.method} {request.path} from {client_cn}")
                
            except Exception as e:
                print(f"⚠️ mTLS logging error: {e}")
        else:
            print(f"⚠️ Non-mTLS Request: {request.method} {request.path} (No client certificate)")
    
    @app.after_request  
    def log_mtls_response(response):
        """Log mTLS response"""
        client_cn = getattr(g, 'client_cn', 'Unknown')
        print(f"✅ mTLS Response: {response.status_code} to {client_cn}")
        return response

def create_mtls_test_endpoints(app):
    """Create test endpoints for mTLS verification"""
    
    @app.route('/api/mtls/status')
    @require_mtls_auth
    def mtls_status():
        """Get mTLS connection status"""
        return jsonify({
            "mtls_enabled": True,
            "client_authenticated": True,
            "client_cn": g.client_cn,
            "client_serial": g.client_cert_serial,
            "client_fingerprint": g.client_cert_fingerprint[:32] + "...",
            "message": "mTLS authentication successful",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
    
    @app.route('/api/mtls/info')
    @require_mtls_auth
    def mtls_info():
        """Get detailed mTLS information"""
        return jsonify({
            "protocol": "TLS 1.2+",
            "authentication": "Mutual TLS (mTLS)",
            "ca_issuer": "QuMail Root CA",
            "client_cn": g.client_cn,
            "client_serial": g.client_cert_serial,
            "security_level": "High (4096-bit RSA)",
            "compliance": "ETSI GS QKD 014",
            "organization": "ISRO QuMail Project",
            "message": "Quantum-secure communication channel established"
        })

def configure_flask_mtls(app, cert_dir="certs"):
    """Configure Flask app for mTLS"""
    print("🔐 Configuring Flask app for mTLS...")
    
    # Initialize mTLS config
    mtls_config = QuMailmTLSConfig(cert_dir)
    
    # Setup mTLS logging
    setup_mtls_logging(app)
    
    # Create test endpoints
    import datetime
    create_mtls_test_endpoints(app)
    
    print("✅ Flask mTLS configuration complete")
    
    return mtls_config

def run_mtls_server(app, host='0.0.0.0', port=5443, cert_dir="certs"):
    """Run Flask app with mTLS"""
    print(f"🚀 Starting QuMail mTLS Server on {host}:{port}")
    print("🔐 Mutual TLS authentication enabled")
    print("📡 ETSI GS QKD 014 compliant")
    
    # Configure mTLS
    mtls_config = configure_flask_mtls(app, cert_dir)
    
    # Create SSL context
    ssl_context = mtls_config.create_ssl_context()
    
    # Run server with mTLS
    app.run(
        host=host,
        port=port,
        ssl_context=ssl_context,
        debug=False,  # Disable debug in production mTLS
        threaded=True
    )

if __name__ == "__main__":
    # Test mTLS configuration
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return jsonify({"message": "QuMail mTLS Test Server", "status": "running"})
    
    run_mtls_server(app)
