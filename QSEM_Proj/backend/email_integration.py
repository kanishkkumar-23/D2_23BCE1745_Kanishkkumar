import smtplib
import imaplib
import email
import ssl
import os
import json
import base64
import logging
import secrets
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Union
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from dataclasses import dataclass, asdict

# Import QuMail encryption
from encryption import QuMailMultiLevelEncryption, SecurityLevel, EncryptedMessage, EncryptionMetadata

# Import shared encryptor function from app.py to ensure same instance
def get_encryptor():
    """Get the shared encryption instance from app.py"""
    try:
        # Import from app.py to use the same singleton instance
        from app import get_encryptor as app_get_encryptor
        return app_get_encryptor()
    except ImportError:
        # Fallback: create our own instance if app.py not available
        global global_encryptor
        if 'global_encryptor' not in globals():
            global_encryptor = QuMailMultiLevelEncryption()
        return global_encryptor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmailCredentials:
    """Email account credentials"""
    email: str
    password: str  # App Password for Gmail
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993

@dataclass
class EmailMessage:
    """Email message structure"""
    sender: str
    recipient: str
    subject: str
    content: str
    attachments: List[Dict[str, Any]] = None
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AIDED
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []

@dataclass
class EmailSendResult:
    """Result of email sending operation"""
    success: bool
    message_id: str = ""
    error: str = ""
    encryption_metadata: Dict[str, Any] = None
    sent_at: str = ""

@dataclass
class ReceivedEmail:
    """Received email structure"""
    message_id: str
    sender: str
    recipient: str
    subject: str
    received_at: str
    is_qumail: bool = False
    security_level: int = 0
    decrypted_content: str = ""
    original_content: str = ""
    encryption_metadata: Dict[str, Any] = None
    signature_verified: bool = False
    decryption_successful: bool = False
    decryption_error: str = ""
    algorithm: str = ""
    error: str = ""

@dataclass
class EmailReceiveResult:
    """Result of email receiving operation"""
    success: bool
    emails: List[ReceivedEmail] = None
    total_count: int = 0
    error: str = ""
    
    def __post_init__(self):
        if self.emails is None:
            self.emails = []

class QuMailEmailSender:
    """
    QuMail Email Sender with Hybrid Encryption
    Integrates multi-level encryption with Gmail SMTP
    """
    
    def __init__(self, credentials: EmailCredentials):
        """
        Initialize email sender
        
        Args:
            credentials: Email account credentials
        """
        self.credentials = credentials
        self.encryptor = get_encryptor()  # Use shared encryption instance
        self.smtp_server = None
        
    def connect_smtp(self) -> bool:
        """
        Connect to Gmail SMTP server
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"🔄 Connecting to Gmail SMTP: {self.credentials.smtp_server}:{self.credentials.smtp_port}")
            
            # Create SMTP connection with TLS
            self.smtp_server = smtplib.SMTP(self.credentials.smtp_server, self.credentials.smtp_port)
            self.smtp_server.starttls()  # Enable TLS encryption
            
            # Login with App Password
            self.smtp_server.login(self.credentials.email, self.credentials.password)
            
            logger.info("✅ Gmail SMTP connection established")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication failed: {e}")
            logger.error("💡 Tip: Use Gmail App Password, not regular password")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected SMTP error: {e}")
            return False
    
    def disconnect_smtp(self):
        """Disconnect from SMTP server"""
        if self.smtp_server:
            try:
                self.smtp_server.quit()
                logger.info("✅ SMTP connection closed")
            except Exception as e:
                logger.warning(f"⚠️ Error closing SMTP: {e}")
            finally:
                self.smtp_server = None
    
    def encrypt_email_content(self, email_msg: EmailMessage) -> Tuple[str, Dict[str, Any]]:
        """
        Encrypt email content using specified security level
        
        Args:
            email_msg: Email message to encrypt
            
        Returns:
            Tuple of (encrypted_content, encryption_metadata)
        """
        try:
            logger.info(f"🔐 Encrypting email with Security Level {email_msg.security_level.value}")
            
            # Encrypt the email content
            encrypted_message = self.encryptor.encrypt_message(
                plaintext=email_msg.content,
                security_level=email_msg.security_level,
                sender=email_msg.sender,
                recipient=email_msg.recipient,
                subject=email_msg.subject,
                attachments=email_msg.attachments
            )
            
            # Extract encryption metadata
            metadata = {
                "security_level": encrypted_message.metadata.security_level,
                "algorithm": encrypted_message.metadata.algorithm,
                "key_source": encrypted_message.metadata.key_source,
                "timestamp": encrypted_message.metadata.timestamp,
                "message_id": encrypted_message.metadata.message_id,
                "key_ids": encrypted_message.metadata.key_ids,
                "quantum_resistant": encrypted_message.metadata.quantum_resistant,
                "etsi_compliant": encrypted_message.metadata.etsi_compliant
            }
            
            logger.info(f"✅ Email encrypted: {encrypted_message.metadata.algorithm}")
            logger.info(f"🔑 Key Source: {encrypted_message.metadata.key_source}")
            logger.info(f"🛡️ Quantum Resistant: {encrypted_message.metadata.quantum_resistant}")
            
            return encrypted_message.ciphertext, metadata
            
        except Exception as e:
            logger.error(f"❌ Encryption error: {e}")
            raise
    
    def create_mime_message(self, email_msg: EmailMessage, encrypted_content: str, 
                           encryption_metadata: Dict[str, Any]) -> MIMEMultipart:
        """
        Create MIME multipart message with encrypted content
        
        Args:
            email_msg: Original email message
            encrypted_content: Encrypted email content
            encryption_metadata: Encryption metadata
            
        Returns:
            MIMEMultipart: Constructed email message
        """
        try:
            # Create multipart message
            mime_msg = MIMEMultipart('alternative')
            
            # Set headers
            mime_msg['From'] = email_msg.sender
            mime_msg['To'] = email_msg.recipient
            mime_msg['Subject'] = f"[QuMail-L{email_msg.security_level.value}] {email_msg.subject}"
            
            # Add QuMail headers for identification
            mime_msg['X-QuMail-Version'] = "1.0.0"
            mime_msg['X-QuMail-Security-Level'] = str(email_msg.security_level.value)
            mime_msg['X-QuMail-Algorithm'] = encryption_metadata['algorithm']
            mime_msg['X-QuMail-Quantum-Resistant'] = str(encryption_metadata['quantum_resistant'])
            mime_msg['X-QuMail-ETSI-Compliant'] = str(encryption_metadata['etsi_compliant'])
            
            # Create encrypted content part
            # For all levels (including Level 4), include both plain text and JSON attachment
            encrypted_body = {
                "qumail_version": "1.0.0",
                "encrypted_content": encrypted_content,
                "encryption_metadata": encryption_metadata,
                "instructions": "This email was encrypted with QuMail. Use QuMail client to decrypt."
            }
            
            # Create both plain text and JSON parts
            plain_text = f"""
🔐 QuMail Encrypted Message 🔐

This email was encrypted using QuMail's hybrid quantum-classical encryption.

Security Level: {email_msg.security_level.value} ({encryption_metadata['algorithm']})
Quantum Resistant: {encryption_metadata['quantum_resistant']}
ETSI Compliant: {encryption_metadata['etsi_compliant']}

To decrypt this message, please use the QuMail client.

---
Encrypted Content:
{encrypted_content[:100]}...

Encryption Metadata:
{json.dumps(encryption_metadata, indent=2)[:300]}...

---
QuMail - Quantum Secure Email for ISRO
Smart India Hackathon 2025
            """.strip()
            
            # Add plain text part for non-QuMail clients
            plain_part = MIMEText(plain_text, 'plain', 'utf-8')
            mime_msg.attach(plain_part)
            
            # Add JSON part for QuMail clients
            json_part = MIMEApplication(
                json.dumps(encrypted_body, indent=2).encode('utf-8'),
                _subtype='json',
                name='qumail_encrypted.json'
            )
            json_part.add_header('Content-Disposition', 'attachment', filename='qumail_encrypted.json')
            mime_msg.attach(json_part)
            
            # Handle attachments (if any)
            for attachment in email_msg.attachments:
                try:
                    att_part = MIMEBase('application', 'octet-stream')
                    att_part.set_payload(attachment.get('data', b''))
                    encoders.encode_base64(att_part)
                    att_part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment.get("filename", "attachment")}'
                    )
                    mime_msg.attach(att_part)
                    logger.info(f"📎 Attached: {attachment.get('filename', 'attachment')}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to attach {attachment.get('filename', 'file')}: {e}")
            
            return mime_msg
            
        except Exception as e:
            logger.error(f"❌ MIME construction error: {e}")
            raise
    
    def send_email(self, email_msg: EmailMessage) -> EmailSendResult:
        """
        Send encrypted email via Gmail SMTP
        
        Args:
            email_msg: Email message to send
            
        Returns:
            EmailSendResult: Result of send operation
        """
        try:
            logger.info(f"📧 Sending email from {email_msg.sender} to {email_msg.recipient}")
            logger.info(f"🔒 Security Level: {email_msg.security_level.value}")
            
            # Connect to SMTP if not already connected
            if not self.smtp_server:
                if not self.connect_smtp():
                    return EmailSendResult(
                        success=False,
                        error="Failed to connect to SMTP server"
                    )
            
            # Encrypt email content
            encrypted_content, encryption_metadata = self.encrypt_email_content(email_msg)
            
            # Create MIME message
            mime_msg = self.create_mime_message(email_msg, encrypted_content, encryption_metadata)
            
            # Send email
            result = self.smtp_server.send_message(mime_msg)
            
            # Generate message ID
            message_id = f"qumail_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
            
            logger.info(f"✅ Email sent successfully!")
            logger.info(f"📨 Message ID: {message_id}")
            logger.info(f"🔐 Algorithm: {encryption_metadata['algorithm']}")
            
            return EmailSendResult(
                success=True,
                message_id=message_id,
                encryption_metadata=encryption_metadata,
                sent_at=datetime.now(timezone.utc).isoformat()
            )
            
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP send error: {e}")
            return EmailSendResult(
                success=False,
                error=f"SMTP error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Send email error: {e}")
            return EmailSendResult(
                success=False,
                error=f"Send error: {str(e)}"
            )
    
    def send_test_email(self, recipient: str, security_level: SecurityLevel = SecurityLevel.QUANTUM_AIDED) -> EmailSendResult:
        """
        Send a test email with specified security level
        
        Args:
            recipient: Email address to send to
            security_level: Security level to use
            
        Returns:
            EmailSendResult: Result of send operation
        """
        test_content = f"""
🔐 QuMail Test Email - Security Level {security_level.value} 🔐

This is a test email from QuMail's hybrid quantum-classical encryption system.

Security Level: {security_level.value}
Timestamp: {datetime.now(timezone.utc).isoformat()}

Test Message Content:
- Quantum Key Distribution (QKD) simulation using BB84 protocol
- Post-Quantum Cryptography with ML-KEM-768 and ML-DSA-65
- Classical cryptography with X25519 ECDH and EdDSA
- Hybrid key derivation using HKDF-SHA256

This email demonstrates the integration of multiple cryptographic layers 
for quantum-resistant email security.

---
QuMail - Quantum Secure Email for ISRO
Smart India Hackathon 2025
        """.strip()
        
        test_email = EmailMessage(
            sender=self.credentials.email,
            recipient=recipient,
            subject=f"QuMail Test - Level {security_level.value} Encryption",
            content=test_content,
            security_level=security_level
        )
        
        return self.send_email(test_email)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect_smtp()

class QuMailEmailReceiver:
    """
    QuMail Email Receiver with Hybrid Decryption
    Integrates multi-level decryption with Gmail IMAP
    """
    
    def __init__(self, credentials: EmailCredentials):
        """
        Initialize email receiver
        
        Args:
            credentials: Email account credentials
        """
        self.credentials = credentials
        self.encryptor = get_encryptor()  # Use shared encryption instance
        self.imap_server = None
        
    def connect_imap(self) -> bool:
        """
        Connect to Gmail IMAP server
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"🔄 Connecting to Gmail IMAP: {self.credentials.imap_server}:{self.credentials.imap_port}")
            
            # Create IMAP connection with SSL
            self.imap_server = imaplib.IMAP4_SSL(self.credentials.imap_server, self.credentials.imap_port)
            
            # Login with App Password
            self.imap_server.login(self.credentials.email, self.credentials.password)
            
            logger.info("✅ Gmail IMAP connection established")
            return True
            
        except imaplib.IMAP4.error as e:
            logger.error(f"❌ IMAP Authentication failed: {e}")
            logger.error("💡 Tip: Use Gmail App Password, not regular password")
            return False
        except Exception as e:
            logger.error(f"❌ IMAP connection error: {e}")
            return False
    
    def disconnect_imap(self):
        """Disconnect from IMAP server"""
        if self.imap_server:
            try:
                self.imap_server.close()
                self.imap_server.logout()
                logger.info("✅ IMAP connection closed")
            except Exception as e:
                logger.warning(f"⚠️ Error closing IMAP: {e}")
            finally:
                self.imap_server = None
    
    def select_folder(self, folder: str = "INBOX") -> bool:
        """
        Select email folder
        
        Args:
            folder: Folder name (default: INBOX)
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.imap_server:
                return False
                
            status, messages = self.imap_server.select(folder)
            if status == 'OK':
                logger.info(f"📂 Selected folder: {folder}")
                return True
            else:
                logger.error(f"❌ Failed to select folder {folder}: {messages}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Folder selection error: {e}")
            return False
    
    def search_emails(self, criteria: str = "ALL", limit: int = 10) -> List[str]:
        """
        Search for emails based on criteria
        
        Args:
            criteria: IMAP search criteria (default: ALL)
            limit: Maximum number of emails to fetch
            
        Returns:
            List of message IDs
        """
        try:
            if not self.imap_server:
                return []
            
            # Search for emails
            status, messages = self.imap_server.search(None, criteria)
            if status != 'OK':
                logger.error(f"❌ Email search failed: {messages}")
                return []
            
            # Get message IDs
            message_ids = messages[0].split()
            
            # Limit results and reverse for newest first
            message_ids = message_ids[-limit:] if len(message_ids) > limit else message_ids
            message_ids.reverse()
            
            logger.info(f"🔍 Found {len(message_ids)} emails matching criteria: {criteria}")
            return [mid.decode() for mid in message_ids]
            
        except Exception as e:
            logger.error(f"❌ Email search error: {e}")
            return []
    
    def parse_email_message(self, raw_email: bytes) -> email.message.EmailMessage:
        """
        Parse raw email bytes into EmailMessage object
        
        Args:
            raw_email: Raw email bytes
            
        Returns:
            email.message.EmailMessage: Parsed email
        """
        try:
            return email.message_from_bytes(raw_email)
        except Exception as e:
            logger.error(f"❌ Email parsing error: {e}")
            return None
    
    def extract_email_content(self, email_msg: email.message.EmailMessage) -> str:
        """
        Extract email content from parsed email message
        Prefers plain text, falls back to HTML, then to any text content
        
        Args:
            email_msg: Parsed email message
            
        Returns:
            str: Extracted email content
        """
        try:
            content = ""
            
            if email_msg.is_multipart():
                # Handle multipart emails
                plain_text = ""
                html_text = ""
                
                for part in email_msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))
                    
                    # Skip attachments
                    if "attachment" in content_disposition:
                        continue
                    
                    if content_type == "text/plain":
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                plain_text = payload.decode('utf-8', errors='ignore')
                        except Exception as e:
                            logger.warning(f"⚠️ Error decoding plain text part: {e}")
                    
                    elif content_type == "text/html":
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                html_text = payload.decode('utf-8', errors='ignore')
                        except Exception as e:
                            logger.warning(f"⚠️ Error decoding HTML part: {e}")
                
                # Prefer plain text, fallback to HTML
                if plain_text.strip():
                    content = plain_text
                elif html_text.strip():
                    # Convert HTML to plain text for better readability
                    content = self.html_to_plain_text(html_text)
                else:
                    content = "No readable content found"
                    
            else:
                # Handle single-part emails
                content_type = email_msg.get_content_type()
                try:
                    payload = email_msg.get_payload(decode=True)
                    if payload:
                        raw_content = payload.decode('utf-8', errors='ignore')
                        
                        if content_type == "text/html":
                            content = self.html_to_plain_text(raw_content)
                        else:
                            content = raw_content
                    else:
                        content = "No content found"
                except Exception as e:
                    logger.warning(f"⚠️ Error decoding single-part email: {e}")
                    content = "Error reading email content"
            
            return content.strip() if content else "No content available"
            
        except Exception as e:
            logger.error(f"❌ Error extracting email content: {e}")
            return "Error reading email content"
    
    def html_to_plain_text(self, html_content: str) -> str:
        """
        Convert HTML content to plain text for better readability
        
        Args:
            html_content: HTML content string
            
        Returns:
            str: Plain text content
        """
        try:
            import re
            
            # Remove HTML tags but preserve line breaks
            text = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
            text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
            text = re.sub(r'<[^>]+>', '', text)
            
            # Decode HTML entities
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&amp;', '&')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&quot;', '"')
            text = text.replace('&#39;', "'")
            
            # Normalize whitespace
            text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 consecutive line breaks
            text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces and tabs
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.warning(f"⚠️ Error converting HTML to plain text: {e}")
            return html_content  # Return original if conversion fails
    
    def decode_header_field(self, header_value: str) -> str:
        """
        Decode email header field that may contain encoded characters
        
        Args:
            header_value: Raw header value
            
        Returns:
            str: Decoded header value
        """
        try:
            if not header_value:
                return 'Unknown'
            
            # Handle encoded headers (RFC 2047)
            from email.header import decode_header
            
            decoded_parts = decode_header(header_value)
            decoded_string = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        try:
                            decoded_string += part.decode(encoding)
                        except (UnicodeDecodeError, LookupError):
                            # Fallback to utf-8 if specified encoding fails
                            try:
                                decoded_string += part.decode('utf-8')
                            except UnicodeDecodeError:
                                # Last resort: decode with errors='ignore'
                                decoded_string += part.decode('utf-8', errors='ignore')
                    else:
                        # No encoding specified, try common encodings
                        for enc in ['utf-8', 'latin-1', 'ascii']:
                            try:
                                decoded_string += part.decode(enc)
                                break
                            except UnicodeDecodeError:
                                continue
                        else:
                            # If all encodings fail, use utf-8 with error handling
                            decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    # Already a string
                    decoded_string += str(part)
            
            return decoded_string.strip()
            
        except Exception as e:
            logger.warning(f"⚠️ Error decoding header field: {e}")
            return str(header_value) if header_value else 'Unknown'
    
    def extract_qumail_data(self, email_msg: email.message.EmailMessage) -> Tuple[bool, Dict[str, Any]]:
        """
        Extract QuMail encrypted data from email
        
        Args:
            email_msg: Parsed email message
            
        Returns:
            Tuple of (is_qumail, encrypted_data)
        """
        try:
            # Check for QuMail headers
            qumail_version = email_msg.get('X-QuMail-Version')
            security_level = email_msg.get('X-QuMail-Security-Level')
            
            if not qumail_version:
                return False, {}
            
            logger.info(f"🔐 QuMail email detected: Version {qumail_version}, Level {security_level}")
            
            # Look for QuMail encrypted JSON attachment
            encrypted_data = None
            for part in email_msg.walk():
                if part.get_content_type() == 'application/json':
                    filename = part.get_filename()
                    if filename and 'qumail_encrypted' in filename:
                        try:
                            json_content = part.get_payload(decode=True)
                            encrypted_data = json.loads(json_content.decode('utf-8'))
                            logger.info("📦 QuMail encrypted data found in JSON attachment")
                            break
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to parse QuMail JSON: {e}")
            
            if not encrypted_data:
                logger.warning("⚠️ QuMail headers found but no encrypted data")
                return True, {}
            
            return True, encrypted_data
            
        except Exception as e:
            logger.error(f"❌ QuMail data extraction error: {e}")
            return False, {}
    
    def decrypt_qumail_content(self, encrypted_data: Dict[str, Any]) -> Tuple[str, bool]:
        """
        Decrypt QuMail encrypted content
        
        Args:
            encrypted_data: QuMail encrypted data dictionary
            
        Returns:
            Tuple of (decrypted_content, signature_verified)
        """
        try:
            if 'encrypted_content' not in encrypted_data or 'encryption_metadata' not in encrypted_data:
                logger.error("❌ Invalid QuMail encrypted data structure")
                return "", False
            
            # Reconstruct EncryptedMessage object
            metadata_dict = encrypted_data['encryption_metadata']
            metadata = EncryptionMetadata(
                security_level=metadata_dict['security_level'],
                algorithm=metadata_dict['algorithm'],
                key_source=metadata_dict['key_source'],
                timestamp=metadata_dict['timestamp'],
                message_id=metadata_dict['message_id'],
                sender=metadata_dict.get('sender', ''),
                recipient=metadata_dict.get('recipient', ''),
                key_ids=metadata_dict['key_ids'],
                integrity_hash=metadata_dict.get('integrity_hash', ''),
                quantum_resistant=metadata_dict['quantum_resistant'],
                etsi_compliant=metadata_dict['etsi_compliant']
            )
            
            encrypted_message = EncryptedMessage(
                ciphertext=encrypted_data['encrypted_content'],
                metadata=metadata,
                attachments=[],
                mime_structure=""
            )
            
            # Decrypt the message
            logger.info(f"🔓 Decrypting message with {metadata.algorithm}")
            decrypted_content = self.encryptor.decrypt_message(encrypted_message)
            
            # For levels with signatures, verify them
            signature_verified = True
            if metadata.security_level in [2, 3]:  # Levels with signatures
                logger.info("🔍 Verifying signatures...")
                # Signature verification is handled within the decryption process
                # If decryption succeeds, signatures are valid
                signature_verified = True
            
            logger.info(f"✅ Message decrypted successfully")
            return decrypted_content, signature_verified
            
        except Exception as e:
            logger.error(f"❌ Decryption error: {e}")
            # Store the error message for frontend display
            self._last_decryption_error = str(e)
            return "", False
    
    def fetch_emails(self, limit: int = 10, folder: str = "INBOX") -> EmailReceiveResult:
        """
        Fetch and decrypt emails from Gmail
        
        Args:
            limit: Maximum number of emails to fetch
            folder: Email folder to search
            
        Returns:
            EmailReceiveResult: Result with decrypted emails
        """
        try:
            logger.info(f"📬 Fetching {limit} emails from {folder}...")
            
            # Connect if not already connected
            if not self.imap_server:
                if not self.connect_imap():
                    return EmailReceiveResult(
                        success=False,
                        error="Failed to connect to IMAP server"
                    )
            
            # Select folder
            if not self.select_folder(folder):
                return EmailReceiveResult(
                    success=False,
                    error=f"Failed to select folder: {folder}"
                )
            
            # Search for emails
            message_ids = self.search_emails("ALL", limit)
            
            received_emails = []
            
            for msg_id in message_ids:
                try:
                    # Fetch email
                    status, msg_data = self.imap_server.fetch(msg_id, '(RFC822)')
                    if status != 'OK':
                        logger.warning(f"⚠️ Failed to fetch message {msg_id}")
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    email_msg = self.parse_email_message(raw_email)
                    
                    if not email_msg:
                        continue
                    
                    # Extract basic email info with proper encoding handling
                    sender = self.decode_header_field(email_msg.get('From', 'Unknown'))
                    recipient = self.decode_header_field(email_msg.get('To', 'Unknown'))
                    subject = self.decode_header_field(email_msg.get('Subject', 'No Subject'))
                    date = email_msg.get('Date', '')
                    
                    # Check if this is a QuMail encrypted email
                    is_qumail, encrypted_data = self.extract_qumail_data(email_msg)
                    
                    received_email = ReceivedEmail(
                        message_id=msg_id,
                        sender=sender,
                        recipient=recipient,
                        subject=subject,
                        received_at=date,
                        is_qumail=is_qumail
                    )
                    
                    if is_qumail and encrypted_data:
                        # Decrypt QuMail content
                        security_level = int(email_msg.get('X-QuMail-Security-Level', 0))
                        decrypted_content, signature_verified = self.decrypt_qumail_content(encrypted_data)
                        
                        received_email.security_level = security_level
                        received_email.decrypted_content = decrypted_content
                        received_email.encryption_metadata = encrypted_data.get('encryption_metadata', {})
                        received_email.signature_verified = signature_verified
                        received_email.algorithm = encrypted_data.get('encryption_metadata', {}).get('algorithm', '')
                        
                        if decrypted_content:
                            received_email.decryption_successful = True
                            logger.info(f"✅ QuMail email decrypted: Level {security_level}")
                        else:
                            received_email.decryption_successful = False
                            # Get the actual error message from decryption
                            received_email.decryption_error = getattr(self, '_last_decryption_error', 'Decryption failed - no content returned')
                            received_email.error = "Decryption failed"
                            logger.warning(f"⚠️ QuMail email decryption failed")
                    else:
                        # Regular email - extract content (prefer plain text, fallback to HTML)
                        received_email.original_content = self.extract_email_content(email_msg)
                    
                    received_emails.append(received_email)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing email {msg_id}: {e}")
                    continue
            
            logger.info(f"✅ Processed {len(received_emails)} emails")
            
            return EmailReceiveResult(
                success=True,
                emails=received_emails,
                total_count=len(received_emails)
            )
            
        except Exception as e:
            logger.error(f"❌ Email fetch error: {e}")
            return EmailReceiveResult(
                success=False,
                error=str(e)
            )
    
    def fetch_inbox_emails(self, limit: int = 10) -> EmailReceiveResult:
        """Fetch emails from Inbox"""
        return self.fetch_emails(limit=limit, folder="INBOX")
    
    def fetch_sent_emails(self, limit: int = 10) -> EmailReceiveResult:
        """Fetch emails from Sent folder"""
        
        # First ensure connection
        if not self.imap_server:
            if not self.connect_imap():
                return EmailReceiveResult(
                    success=False,
                    error="Failed to connect to IMAP server"
                )
        
        # Try different possible sent folder names
        possible_sent_folders = [
            "[Gmail]/Sent Mail",  # Gmail English
            "[Gmail]/Mensagens enviadas",  # Gmail Portuguese
            "[Gmail]/Elementos enviados",  # Gmail Spanish
            "[Gmail]/Éléments envoyés",  # Gmail French
            "[Gmail]/Gesendete Nachrichten",  # Gmail German
            "INBOX.Sent",  # Some IMAP servers
            "Sent",  # Standard
            "Sent Items",  # Outlook/Exchange
            "Sent Messages"  # Alternative
        ]
        
        for folder_name in possible_sent_folders:
            try:
                logger.info(f"Trying to access sent folder: {folder_name}")
                
                # Try to select the folder first to check if it exists
                status, _ = self.imap_server.select(folder_name, readonly=True)
                if status == 'OK':
                    # Folder exists, now fetch emails
                    result = self.fetch_emails(limit=limit, folder=folder_name)
                    if result.success:
                        logger.info(f"✅ Successfully accessed sent folder: {folder_name}")
                        return result
                else:
                    logger.debug(f"Folder {folder_name} does not exist or cannot be accessed")
                    
            except Exception as e:
                logger.warning(f"Failed to access {folder_name}: {str(e)}")
                continue
        
        # If all fail, try to list available folders to help debug
        available_folders = []
        try:
            self.imap_server.select("INBOX", readonly=True)  # Select inbox first
            status, folders = self.imap_server.list()
            if status == 'OK':
                available_folders = [folder.decode() for folder in folders]
                logger.error(f"Available folders: {available_folders}")
                
                # Look for any folder containing "sent" (case insensitive)
                sent_candidates = [f for f in available_folders if 'sent' in f.lower()]
                if sent_candidates:
                    logger.info(f"Found potential sent folders: {sent_candidates}")
                    # Try the first candidate
                    folder_name = sent_candidates[0].split('"')[-2] if '"' in sent_candidates[0] else sent_candidates[0]
                    try:
                        result = self.fetch_emails(limit=limit, folder=folder_name)
                        if result.success:
                            logger.info(f"✅ Successfully used detected sent folder: {folder_name}")
                            return result
                    except Exception as e:
                        logger.warning(f"Failed to use detected folder {folder_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Could not list folders: {e}")
        
        # Return error with helpful info
        error_msg = "Could not access sent folder. "
        if available_folders:
            error_msg += f"Available folders: {', '.join(available_folders[:5])}{'...' if len(available_folders) > 5 else ''}"
        else:
            error_msg += "Check Gmail IMAP settings and ensure 'Less secure app access' or App Passwords are configured."
            
        return EmailReceiveResult(
            success=False,
            error=error_msg
        )
    
    def fetch_trash_emails(self, limit: int = 10) -> EmailReceiveResult:
        """Fetch emails from Trash folder"""
        
        # First ensure connection
        if not self.imap_server:
            if not self.connect_imap():
                return EmailReceiveResult(
                    success=False,
                    error="Failed to connect to IMAP server"
                )
        
        # Try different possible trash folder names
        possible_trash_folders = [
            "[Gmail]/Trash",  # Gmail English
            "[Gmail]/Lixeira",  # Gmail Portuguese
            "[Gmail]/Papelera",  # Gmail Spanish
            "[Gmail]/Corbeille",  # Gmail French
            "[Gmail]/Papierkorb",  # Gmail German
            "INBOX.Trash",
            "Trash",
            "Deleted Items",
            "Deleted"
        ]
        
        for folder_name in possible_trash_folders:
            try:
                status, _ = self.imap_server.select(folder_name, readonly=True)
                if status == 'OK':
                    result = self.fetch_emails(limit=limit, folder=folder_name)
                    if result.success:
                        logger.info(f"✅ Successfully accessed trash folder: {folder_name}")
                        return result
            except Exception as e:
                logger.warning(f"Failed to access trash folder {folder_name}: {str(e)}")
                continue
        
        return EmailReceiveResult(
            success=False,
            error="Could not access trash folder - tried multiple folder names"
        )
    
    def fetch_draft_emails(self, limit: int = 10) -> EmailReceiveResult:
        """Fetch emails from Drafts folder"""
        
        # First ensure connection
        if not self.imap_server:
            if not self.connect_imap():
                return EmailReceiveResult(
                    success=False,
                    error="Failed to connect to IMAP server"
                )
        
        # Try different possible drafts folder names
        possible_draft_folders = [
            "[Gmail]/Drafts",  # Gmail English
            "[Gmail]/Rascunhos",  # Gmail Portuguese
            "[Gmail]/Borradores",  # Gmail Spanish
            "[Gmail]/Brouillons",  # Gmail French
            "[Gmail]/Entwürfe",  # Gmail German
            "INBOX.Drafts",
            "Drafts",
            "Draft"
        ]
        
        for folder_name in possible_draft_folders:
            try:
                status, _ = self.imap_server.select(folder_name, readonly=True)
                if status == 'OK':
                    result = self.fetch_emails(limit=limit, folder=folder_name)
                    if result.success:
                        logger.info(f"✅ Successfully accessed drafts folder: {folder_name}")
                        return result
            except Exception as e:
                logger.warning(f"Failed to access drafts folder {folder_name}: {str(e)}")
                continue
        
        return EmailReceiveResult(
            success=False,
            error="Could not access drafts folder - tried multiple folder names"
        )
    
    def fetch_all_mail(self, limit: int = 10) -> EmailReceiveResult:
        """Fetch emails from All Mail folder"""
        return self.fetch_emails(limit=limit, folder="[Gmail]/All Mail")
    
    def list_folders(self) -> dict:
        """List all available Gmail folders"""
        try:
            if not self.imap_server:
                if not self.connect_imap():
                    return {"success": False, "error": "Failed to connect to IMAP"}
            
            # List all folders
            folders = []
            typ, folder_list = self.imap_server.list()
            
            if typ == 'OK':
                for folder in folder_list:
                    folder_name = folder.decode().split('"/"')[-1].strip().strip('"')
                    folders.append(folder_name)
            
            return {
                "success": True,
                "folders": folders,
                "common_folders": {
                    "inbox": "INBOX",
                    "sent": "[Gmail]/Sent Mail", 
                    "trash": "[Gmail]/Trash",
                    "drafts": "[Gmail]/Drafts",
                    "all_mail": "[Gmail]/All Mail",
                    "spam": "[Gmail]/Spam"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Folder list error: {e}")
            return {"success": False, "error": str(e)}
    
    def search_qumail_emails(self, limit: int = 10) -> EmailReceiveResult:
        """
        Search specifically for QuMail encrypted emails
        
        Args:
            limit: Maximum number of emails to search
            
        Returns:
            EmailReceiveResult: Result with QuMail emails only
        """
        try:
            # Search for emails with QuMail in subject
            result = self.fetch_emails(limit * 2)  # Fetch more to find QuMail emails
            
            if not result.success:
                return result
            
            # Filter for QuMail emails only
            qumail_emails = [email for email in result.emails if email.is_qumail]
            
            return EmailReceiveResult(
                success=True,
                emails=qumail_emails[:limit],
                total_count=len(qumail_emails)
            )
            
        except Exception as e:
            logger.error(f"❌ QuMail search error: {e}")
            return EmailReceiveResult(
                success=False,
                error=str(e)
            )
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect_imap()

# Factory functions for easy integration
def create_email_sender(email: str, password: str) -> QuMailEmailSender:
    """
    Create QuMail email sender instance
    
    Args:
        email: Gmail address
        password: Gmail App Password
        
    Returns:
        QuMailEmailSender: Configured email sender
    """
    credentials = EmailCredentials(email=email, password=password)
    return QuMailEmailSender(credentials)

def create_email_receiver(email: str, password: str) -> QuMailEmailReceiver:
    """
    Create QuMail email receiver instance
    
    Args:
        email: Gmail address
        password: Gmail App Password
        
    Returns:
        QuMailEmailReceiver: Configured email receiver
    """
    credentials = EmailCredentials(email=email, password=password)
    return QuMailEmailReceiver(credentials)

# Demo functions
def demo_email_integration():
    """Demonstrate complete email integration with sending and receiving"""
    print("🔐 QuMail Complete Email Integration Demo")
    print("=" * 60)
    
    # Note: Replace with actual credentials for testing
    demo_email = "your_email@gmail.com"
    demo_password = "your_app_password"
    recipient = "recipient@gmail.com"
    
    print("⚠️ Demo requires actual Gmail credentials")
    print("1. Enable 2-Factor Authentication on Gmail")
    print("2. Generate App Password for QuMail")
    print("3. Update demo_email and demo_password variables")
    print("4. Set recipient email address")
    
    print("\n📧 Email Sending Demo:")
    print("- Send encrypted emails with all security levels")
    print("- QuMail headers and JSON attachments")
    print("- SMTP with TLS encryption")
    
    print("\n📬 Email Receiving Demo:")
    print("- Fetch emails from Gmail IMAP")
    print("- Detect QuMail encrypted emails")
    print("- Decrypt content and verify signatures")
    print("- Support for all security levels")
    
    # Uncomment below for actual testing:
    """
    try:
        # Test email sending
        print("\n🔐 Testing Email Sending...")
        with create_email_sender(demo_email, demo_password) as sender:
            for level in [SecurityLevel.QUANTUM_SECURE, SecurityLevel.QUANTUM_AIDED, SecurityLevel.HYBRID_PQC]:
                print(f"\n📤 Sending Level {level.value} email...")
                result = sender.send_test_email(recipient, level)
                
                if result.success:
                    print(f"✅ Email sent: {result.message_id}")
                    print(f"🔐 Algorithm: {result.encryption_metadata['algorithm']}")
                else:
                    print(f"❌ Send failed: {result.error}")
        
        # Wait for emails to arrive
        print("\n⏳ Waiting for emails to arrive...")
        import time
        time.sleep(10)
        
        # Test email receiving
        print("\n📬 Testing Email Receiving...")
        with create_email_receiver(demo_email, demo_password) as receiver:
            result = receiver.fetch_emails(limit=10)
            
            if result.success:
                print(f"✅ Fetched {result.total_count} emails")
                
                for email in result.emails:
                    print(f"\n📧 Email: {email.subject}")
                    print(f"   From: {email.sender}")
                    print(f"   QuMail: {email.is_qumail}")
                    
                    if email.is_qumail:
                        print(f"   Security Level: {email.security_level}")
                        print(f"   Decrypted: {'Yes' if email.decrypted_content else 'No'}")
                        print(f"   Signatures Verified: {email.signature_verified}")
                        if email.decrypted_content:
                            print(f"   Content: {email.decrypted_content[:100]}...")
            else:
                print(f"❌ Receive failed: {result.error}")
                    
        print("\n✅ Complete email integration demo completed!")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    """

if __name__ == "__main__":
    demo_email_integration()
