import { initializeApp } from 'firebase/app'
import { getAuth, connectAuthEmulator } from 'firebase/auth'

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCwmm9OuEGQxynfVSf-Cua9hPC0wAEnjwU",
  authDomain: "remoteled-7f6ba.firebaseapp.com",
  projectId: "remoteled-7f6ba",
  storageBucket: "remoteled-7f6ba.firebasestorage.app",
  messagingSenderId: "863867121810",
  appId: "1:863867121810:web:a642add94737a8c719b64b"
}

// Initialize Firebase
export const app = initializeApp(firebaseConfig)

// Initialize Firebase Authentication
export const auth = getAuth(app)

// For development: uncomment to use Firebase Auth Emulator
// if (import.meta.env.DEV) {
//   connectAuthEmulator(auth, 'http://localhost:9099')
// }

