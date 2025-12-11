#!/bin/bash
set -e

echo "================================================"
echo "Rebuild Android App (APK)"
echo "================================================"

cd android/RemoteLedBLE

echo "Cleaning previous build..."
./gradlew clean

echo "Building debug APK..."
./gradlew assembleDebug

echo ""
echo "✓ APK built successfully!"
echo ""
echo "APK location:"
echo "  app/build/outputs/apk/debug/app-debug.apk"
echo ""
echo "To install on connected device via USB:"
echo "  adb install -r app/build/outputs/apk/debug/app-debug.apk"
echo ""
echo "Or transfer via MacDroid and install manually"
echo ""
