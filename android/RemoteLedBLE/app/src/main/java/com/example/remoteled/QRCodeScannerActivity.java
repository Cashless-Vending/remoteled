package com.example.remoteled;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.widget.Button;
import com.example.remoteled.BuildConfig;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.journeyapps.barcodescanner.BarcodeCallback;
import com.journeyapps.barcodescanner.BarcodeResult;
import com.journeyapps.barcodescanner.BarcodeView;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QRCodeScannerActivity extends AppCompatActivity {

    private static final int CAMERA_PERMISSION_REQUEST_CODE = 100;
    private static final boolean DEMO_SKIP_QR = false; // ensure real QR flow
    private BarcodeView barcodeView;
    private Button testModeButton;
    
    // Test device IDs (from database seed data)
    private static final String[] TEST_DEVICES = {
        "d1111111-1111-1111-1111-111111111111", // Laundry Room A
        "d2222222-2222-2222-2222-222222222222", // Vending Machine #42
        "d3333333-3333-3333-3333-333333333333", // Air Compressor Station
        "d4444444-4444-4444-4444-444444444444"  // Massage Chair #7
    };
    
    private static final String[] TEST_DEVICE_NAMES = {
        "Laundry Room A (3 services, ACTIVE)",
        "Vending Machine #42 (2 services, ACTIVE)",
        "Air Compressor (2 services, ACTIVE)",
        "Massage Chair #7 (2 services, OFFLINE)"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_qrcode_scanner);

        barcodeView = findViewById(R.id.barcode_scanner);
        testModeButton = findViewById(R.id.test_mode_button);
        
        // Hide test button and enforce real flow
        testModeButton.setVisibility(android.view.View.GONE);

        // Check for camera permissions
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) 
                == PackageManager.PERMISSION_GRANTED) {
            startQRCodeScanner();
        } else {
            // Request Camera Permission
            ActivityCompat.requestPermissions(this, 
                new String[]{Manifest.permission.CAMERA}, 
                CAMERA_PERMISSION_REQUEST_CODE);
        }
    }
    
    /**
     * Setup test mode button for emulator testing
     * Allows testing complete flow without QR scanning
     * 
     * Test aid (kept but hidden by default)
     */
    private void setupTestModeButton() {
        // Single tap: instantly skip QR and use the first test device
        testModeButton.setOnClickListener(v -> {
            String defaultDeviceId = TEST_DEVICES[0];
            Toast.makeText(this, "Test Mode: skipping QR", Toast.LENGTH_SHORT).show();
            navigateToProductSelection(defaultDeviceId);
        });
        // Long press: show the selector with all test devices
        testModeButton.setOnLongClickListener(v -> {
            showTestDeviceSelector();
            return true;
        });
    }
    
    /**
     * Show dialog to select a test device
     */
    private void showTestDeviceSelector() {
        // Debug: Check if arrays are populated
        Toast.makeText(this, "Devices count: " + TEST_DEVICE_NAMES.length, Toast.LENGTH_SHORT).show();
        
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("🧪 Select Test Device");
        builder.setMessage("Choose a device to test the complete flow:");
        
        // Create a simple list of options
        String[] options = {
            "Laundry Room A (3 services, ACTIVE)",
            "Vending Machine #42 (2 services, ACTIVE)", 
            "Air Compressor (2 services, ACTIVE)",
            "Massage Chair #7 (2 services, OFFLINE)"
        };
        
        builder.setItems(options, (dialog, which) -> {
            String selectedDeviceId = TEST_DEVICES[which];
            Toast.makeText(this, 
                "Testing with: " + options[which], 
                Toast.LENGTH_SHORT).show();
            navigateToProductSelection(selectedDeviceId);
        });
        builder.setNegativeButton("Cancel", null);
        builder.show();
    }

    private void startQRCodeScanner() {
        barcodeView.decodeContinuous(new BarcodeCallback() {
            @Override
            public void barcodeResult(BarcodeResult result) {
                String qrCodeContent = result.getText();

                // Handle HTTPS deep links: https://your-api.com/detail?machineId=XXX&mac=YYY&...
                if (qrCodeContent != null && (qrCodeContent.startsWith("https://") || qrCodeContent.startsWith("http://"))) {
                    // Check if it contains the required BLE parameters
                    if (qrCodeContent.contains("/detail") && qrCodeContent.contains("mac=")) {
                        barcodeView.pause();
                        try {
                            android.net.Uri uri = android.net.Uri.parse(qrCodeContent);
                            // Forward the HTTPS deep link to MainActivity for BLE connection
                            Intent intent = new Intent(Intent.ACTION_VIEW, uri, QRCodeScannerActivity.this, MainActivity.class);
                            startActivity(intent);
                        } catch (Exception e) {
                            Toast.makeText(QRCodeScannerActivity.this, "Invalid detail link", Toast.LENGTH_SHORT).show();
                            barcodeView.resume();
                        }
                        return;
                    }
                }

                // Handle legacy remoteled://connect deep link
                if (qrCodeContent != null && qrCodeContent.startsWith("remoteled://connect/")) {
                    barcodeView.pause();
                    try {
                        android.net.Uri uri = android.net.Uri.parse(qrCodeContent);
                        // Forward the deep link to MainActivity which performs BLE handshake
                        Intent intent = new Intent(Intent.ACTION_VIEW, uri, QRCodeScannerActivity.this, MainActivity.class);
                        startActivity(intent);
                    } catch (Exception e) {
                        Toast.makeText(QRCodeScannerActivity.this, "Invalid connect link", Toast.LENGTH_SHORT).show();
                        barcodeView.resume();
                    }
                    return;
                }

                // Fallback: extract device UUID QR
                String deviceId = extractDeviceId(qrCodeContent);
                if (deviceId != null && isValidUUID(deviceId)) {
                    barcodeView.pause();
                    navigateToProductSelection(deviceId);
                } else {
                    Toast.makeText(QRCodeScannerActivity.this, "Invalid QR Code. Please scan a valid code.", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }
    
    /**
     * Extract device ID from QR code
     * Supports formats:
     * - Direct UUID: d1111111-1111-1111-1111-111111111111
     * - URL format: remoteled://device/d1111111-1111-1111-1111-111111111111
     */
    private String extractDeviceId(String qrContent) {
        if (qrContent == null || qrContent.isEmpty()) {
            return null;
        }
        
        // Pattern 1: Direct UUID
        if (isValidUUID(qrContent)) {
            return qrContent;
        }
        
        // Pattern 2: remoteled://device/{uuid}
        Pattern deepLinkPattern = Pattern.compile("remoteled://device/([a-fA-F0-9-]{36})");
        Matcher deepLinkMatcher = deepLinkPattern.matcher(qrContent);
        if (deepLinkMatcher.find()) {
            return deepLinkMatcher.group(1);
        }
        
        // Pattern 3: Any URL ending with UUID
        Pattern uuidPattern = Pattern.compile("([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})");
        Matcher uuidMatcher = uuidPattern.matcher(qrContent);
        if (uuidMatcher.find()) {
            return uuidMatcher.group(1);
        }
        
        return null;
    }
    
    /**
     * Validate UUID format
     */
    private boolean isValidUUID(String uuid) {
        if (uuid == null) return false;
        String uuidPattern = "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$";
        return uuid.matches(uuidPattern);
    }
    
    /**
     * Navigate to Product Selection Activity
     */
    private void navigateToProductSelection(String deviceId) {
        Intent intent = new Intent(this, ProductSelectionActivity.class);
        intent.putExtra("DEVICE_ID", deviceId);
        startActivity(intent);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (barcodeView != null) {
            barcodeView.resume();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (barcodeView != null) {
            barcodeView.pause();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, 
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // Permission granted
                startQRCodeScanner();
            } else {
                // Permission denied
                Toast.makeText(this, 
                    "Camera permission is required to scan QR codes", 
                    Toast.LENGTH_LONG).show();
                // Don't finish - let user use test mode button
            }
        }
    }
}
