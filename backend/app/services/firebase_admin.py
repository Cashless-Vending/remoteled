"""
Firebase Admin SDK service for verifying Firebase ID tokens.
"""
import os
import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional, Dict


class FirebaseAdminService:
    """Service for Firebase Admin operations."""
    
    def __init__(self):
        self._initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Firebase Admin SDK."""
        if self._initialized:
            return
        
        try:
            # Check if already initialized
            firebase_admin.get_app()
            self._initialized = True
            print("✅ Firebase Admin SDK already initialized")
        except ValueError:
            # Not initialized, so initialize it
            cred_path = os.getenv(
                "FIREBASE_CREDENTIALS_PATH",
                "/app/remoteled-7f6ba-firebase-adminsdk-fbsvc-f20bfcc258.json"
            )
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self._initialized = True
                print(f"✅ Firebase Admin SDK initialized with credentials from {cred_path}")
            else:
                print(f"⚠️  Firebase credentials not found at {cred_path}")
                print("⚠️  Firebase authentication will not work")
    
    async def verify_id_token(self, id_token: str) -> Optional[Dict]:
        """
        Verify a Firebase ID token and return the decoded token.
        
        Args:
            id_token: The Firebase ID token to verify
            
        Returns:
            Dict containing user information if valid, None otherwise
        """
        if not self._initialized:
            print("❌ Firebase Admin SDK not initialized")
            return None
        
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            
            return {
                "uid": decoded_token.get("uid"),
                "email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture")
            }
        except auth.InvalidIdTokenError:
            print("❌ Invalid Firebase ID token")
            return None
        except auth.ExpiredIdTokenError:
            print("❌ Expired Firebase ID token")
            return None
        except Exception as e:
            print(f"❌ Error verifying Firebase ID token: {e}")
            return None
    
    async def get_user(self, uid: str) -> Optional[Dict]:
        """
        Get user information by UID.
        
        Args:
            uid: The Firebase user UID
            
        Returns:
            Dict containing user information if found, None otherwise
        """
        if not self._initialized:
            return None
        
        try:
            user = auth.get_user(uid)
            return {
                "uid": user.uid,
                "email": user.email,
                "email_verified": user.email_verified,
                "display_name": user.display_name,
                "photo_url": user.photo_url,
                "disabled": user.disabled
            }
        except auth.UserNotFoundError:
            print(f"❌ User not found: {uid}")
            return None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None


# Singleton instance
firebase_admin_service = FirebaseAdminService()

