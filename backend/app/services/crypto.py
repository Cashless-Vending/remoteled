"""
Cryptography service for signing authorizations
"""
import hashlib
import secrets
import time
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigencode_der
from typing import Dict
from datetime import datetime, timedelta
from app.core.config import settings


class CryptoService:
    """Handle ECDSA signing for device authorizations"""
    
    def __init__(self):
        # For now, generate a new key each time
        # In production, load from environment or key management service
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
    
    def generate_nonce(self, length: int = 12) -> str:
        """Generate a cryptographically secure random nonce"""
        return secrets.token_hex(length // 2)
    
    def create_payload(
        self,
        device_id: str,
        order_id: str,
        service_type: str,
        authorized_seconds: int
    ) -> Dict:
        """Create authorization payload"""
        nonce = self.generate_nonce()
        expiry_time = datetime.utcnow() + timedelta(minutes=settings.AUTH_EXPIRY_MINUTES)
        
        payload = {
            "deviceId": device_id,
            "orderId": order_id,
            "type": service_type,
            "seconds": authorized_seconds,
            "nonce": nonce,
            "exp": int(expiry_time.timestamp())
        }
        
        return payload
    
    def sign_payload(self, payload: Dict) -> str:
        """Sign a payload with ECDSA and return hex signature"""
        # Convert payload to canonical string for signing
        payload_str = self._serialize_payload(payload)
        
        # Add domain separation
        message = f"RemoteLED:Authorization:{payload_str}"
        message_bytes = message.encode('utf-8')
        
        # Create hash
        message_hash = hashlib.sha256(message_bytes).digest()
        
        # Sign with ECDSA
        signature = self.private_key.sign_digest(
            message_hash,
            sigencode=sigencode_der
        )
        
        # Return hex-encoded signature
        return signature.hex()
    
    def _serialize_payload(self, payload: Dict) -> str:
        """Serialize payload to canonical string"""
        # Sort keys for deterministic signing
        sorted_keys = sorted(payload.keys())
        parts = [f"{k}={payload[k]}" for k in sorted_keys]
        return "&".join(parts)
    
    def hash_payload(self, payload: Dict) -> str:
        """Create SHA-256 hash of payload"""
        payload_str = self._serialize_payload(payload)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()


# Global crypto service instance
crypto_service = CryptoService()

