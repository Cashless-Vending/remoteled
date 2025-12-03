package com.example.remoteled;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Size;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.StringRes;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.ImageProxy;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.remoteled.models.requests.LEDControlRequest;
import com.example.remoteled.network.RetrofitClient;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.mlkit.vision.barcode.BarcodeScanner;
import com.google.mlkit.vision.barcode.BarcodeScannerOptions;
import com.google.mlkit.vision.barcode.BarcodeScanning;
import com.google.mlkit.vision.barcode.common.Barcode;
import com.google.mlkit.vision.common.InputImage;

import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QRCodeScannerActivity extends AppCompatActivity {

    private static final int CAMERA_PERMISSION_REQUEST_CODE = 100;
    private static final String LOG_TAG = "QRScanner";

    private PreviewView previewView;
    private TextView statusText;
    private Button startScanButton;
    private Button stopScanButton;

    private ExecutorService cameraExecutor;
    private BarcodeScanner barcodeScanner;
    private boolean isProcessing = false;
    private boolean hasCameraPermission = false;
    private boolean cameraStarted = false;
    private boolean pendingStartAfterPermission = false;
    private ProcessCameraProvider cameraProvider;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_qrcode_scanner);

        previewView = findViewById(R.id.preview_view);
        statusText = findViewById(R.id.status_text);
        startScanButton = findViewById(R.id.start_scan_button);
        stopScanButton = findViewById(R.id.stop_scan_button);

        statusText.setText(R.string.scan_status_idle);

        cameraExecutor = Executors.newSingleThreadExecutor();

        // Initialize ML Kit Barcode Scanner (bundled)
        BarcodeScannerOptions options = new BarcodeScannerOptions.Builder()
            .setBarcodeFormats(Barcode.FORMAT_QR_CODE)
            .build();
        barcodeScanner = BarcodeScanning.getClient(options);

        hasCameraPermission = ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            == PackageManager.PERMISSION_GRANTED;

        startScanButton.setOnClickListener(v -> handleStartScanButtonClick());
        stopScanButton.setOnClickListener(v -> handleStopScanButtonClick());
        updateStartButtonState(true, R.string.scan_qr_button);
        updateStopButtonState(false);

        if (!hasCameraPermission) {
            ActivityCompat.requestPermissions(this,
                new String[]{Manifest.permission.CAMERA},
                CAMERA_PERMISSION_REQUEST_CODE);
        }
    }

    private void handleStartScanButtonClick() {
        android.util.Log.d(LOG_TAG, "Start Scan button tapped (cameraStarted=" + cameraStarted + ")");
        if (cameraStarted) {
            statusText.setText(R.string.scan_status_scanning);
            return;
        }

        if (!hasCameraPermission) {
            pendingStartAfterPermission = true;
            ActivityCompat.requestPermissions(this,
                new String[]{Manifest.permission.CAMERA},
                CAMERA_PERMISSION_REQUEST_CODE);
            return;
        }

        beginCameraScan();
    }

    private void handleStopScanButtonClick() {
        android.util.Log.d(LOG_TAG, "Stop Scan button tapped (cameraStarted=" + cameraStarted + ")");
        if (!cameraStarted) {
            statusText.setText(R.string.scan_status_idle);
            return;
        }
        stopCamera("User tapped Stop");
    }

    private void beginCameraScan() {
        pendingStartAfterPermission = false;
        updateStartButtonState(false, R.string.scan_qr_button_scanning);
        startCamera();
    }

    private void startCamera() {
        ListenableFuture<ProcessCameraProvider> cameraProviderFuture =
            ProcessCameraProvider.getInstance(this);

        cameraProviderFuture.addListener(() -> {
            try {
                cameraProvider = cameraProviderFuture.get();
                bindCameraUseCases(cameraProvider);
            } catch (ExecutionException | InterruptedException e) {
                android.util.Log.e("QRScanner", "Error starting camera", e);
                Toast.makeText(this, "Failed to start camera", Toast.LENGTH_SHORT).show();
                cameraStarted = false;
                updateStartButtonState(true, R.string.scan_qr_button_retry);
                updateStopButtonState(false);
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void bindCameraUseCases(ProcessCameraProvider cameraProvider) {
        // Preview
        Preview preview = new Preview.Builder().build();
        preview.setSurfaceProvider(previewView.getSurfaceProvider());

        // Image Analysis for barcode scanning
        ImageAnalysis imageAnalysis = new ImageAnalysis.Builder()
            .setTargetResolution(new Size(1280, 720))
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build();

        imageAnalysis.setAnalyzer(cameraExecutor, imageProxy -> {
            processImageProxy(imageProxy);
        });

        // Camera selector
        CameraSelector cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA;

        try {
            // Unbind all before rebinding
            cameraProvider.unbindAll();

            // Bind use cases to camera
            cameraProvider.bindToLifecycle(
                this,
                cameraSelector,
                preview,
                imageAnalysis
            );

            cameraStarted = true;
            statusText.setText(R.string.scan_status_point_camera);
            updateStopButtonState(true);
            android.util.Log.d("QRScanner", "Camera started successfully");

        } catch (Exception e) {
            android.util.Log.e("QRScanner", "Camera binding failed", e);
            Toast.makeText(this, "Camera binding failed", Toast.LENGTH_SHORT).show();
            cameraStarted = false;
            updateStartButtonState(true, R.string.scan_qr_button_retry);
            updateStopButtonState(false);
        }
    }

    @androidx.camera.core.ExperimentalGetImage
    private void processImageProxy(ImageProxy imageProxy) {
        if (isProcessing) {
            android.util.Log.v(LOG_TAG, "Skipping frame because another is processing");
            imageProxy.close();
            return;
        }

        android.media.Image mediaImage = imageProxy.getImage();
        if (mediaImage == null) {
            android.util.Log.w(LOG_TAG, "ImageProxy returned null mediaImage");
            imageProxy.close();
            return;
        }

        InputImage image = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.getImageInfo().getRotationDegrees()
        );

        isProcessing = true;
        android.util.Log.v(LOG_TAG, "Submitting frame to ML Kit (rotation=" +
            imageProxy.getImageInfo().getRotationDegrees() + ")");

        barcodeScanner.process(image)
            .addOnSuccessListener(barcodes -> {
                android.util.Log.v(LOG_TAG, "ML Kit returned " + barcodes.size() + " barcodes");
                if (!barcodes.isEmpty()) {
                    handleBarcodes(barcodes);
                }
            })
            .addOnFailureListener(e -> {
                android.util.Log.e("QRScanner", "Barcode scanning failed", e);
            })
            .addOnCompleteListener(task -> {
                isProcessing = false;
                imageProxy.close();
            });
    }

    private void handleBarcodes(List<Barcode> barcodes) {
        for (Barcode barcode : barcodes) {
            String qrCodeContent = barcode.getRawValue();
            if (qrCodeContent == null || qrCodeContent.isEmpty()) {
                continue;
            }

            android.util.Log.d("QRScanner", "QR Code scanned: " + qrCodeContent);
            runOnUiThread(() -> processQRCode(qrCodeContent));
            break; // Process only first barcode
        }
    }

    private void processQRCode(String qrCodeContent) {
        // Prevent multiple scans
        isProcessing = true;
        statusText.setText(R.string.scan_status_scanning);

        // Accept remoteled://connect deep link
        if (qrCodeContent.startsWith("remoteled://connect/")) {
            try {
                android.net.Uri uri = android.net.Uri.parse(qrCodeContent);
                Intent intent = new Intent(Intent.ACTION_VIEW, uri, this, MainActivity.class);
                startActivity(intent);
                finish();
            } catch (Exception e) {
                Toast.makeText(this, "Invalid connect link", Toast.LENGTH_SHORT).show();
                isProcessing = false;
            }
            return;
        }

        // Accept HTTP deep link (new format)
        if (qrCodeContent.startsWith("http://") || qrCodeContent.startsWith("https://")) {
            try {
                android.net.Uri uri = android.net.Uri.parse(qrCodeContent);
                // Check if this is a /detail deep link
                if (uri.getPath() != null && uri.getPath().equals("/detail")) {
                    Intent intent = new Intent(Intent.ACTION_VIEW, uri, this, MainActivity.class);
                    startActivity(intent);
                    finish();
                    return;
                }
            } catch (Exception e) {
                Toast.makeText(this, "Invalid URL format", Toast.LENGTH_SHORT).show();
                isProcessing = false;
                return;
            }
        }

        // Fallback: extract device UUID QR
        String deviceId = extractDeviceId(qrCodeContent);
        if (deviceId != null && isValidUUID(deviceId)) {
            navigateToProductSelection(deviceId);
        } else {
            Toast.makeText(this, "Invalid QR Code. Please try again.", Toast.LENGTH_SHORT).show();
            isProcessing = false;
        }
    }

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

    private boolean isValidUUID(String uuid) {
        if (uuid == null) return false;
        String uuidPattern = "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$";
        return uuid.matches(uuidPattern);
    }

    private void navigateToProductSelection(String deviceId) {
        Intent intent = new Intent(this, ProductSelectionActivity.class);
        intent.putExtra("DEVICE_ID", deviceId);
        startActivity(intent);
        finish();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                          @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                hasCameraPermission = true;
                Toast.makeText(this,
                    R.string.scan_permission_granted,
                    Toast.LENGTH_SHORT).show();
                if (pendingStartAfterPermission) {
                    beginCameraScan();
                }
            } else {
                Toast.makeText(this,
                    "Camera permission is required to scan QR codes",
                    Toast.LENGTH_LONG).show();
                updateStartButtonState(true, R.string.scan_qr_button);
                updateStopButtonState(false);
            }
        }
    }

    private void stopCamera(String reason) {
        if (cameraProvider != null) {
            cameraProvider.unbindAll();
        }
        cameraStarted = false;
        isProcessing = false;
        pendingStartAfterPermission = false;
        statusText.setText(R.string.scan_status_stopped);
        updateStartButtonState(true, R.string.scan_qr_button);
        updateStopButtonState(false);
        android.util.Log.d(LOG_TAG, "Camera scan stopped: " + reason);
    }

    private void updateStartButtonState(boolean enabled, @StringRes int labelRes) {
        if (startScanButton == null) {
            return;
        }
        runOnUiThread(() -> {
            startScanButton.setEnabled(enabled);
            startScanButton.setAlpha(enabled ? 1f : 0.6f);
            startScanButton.setText(labelRes);
        });
    }

    private void updateStopButtonState(boolean enabled) {
        if (stopScanButton == null) {
            return;
        }
        runOnUiThread(() -> {
            stopScanButton.setEnabled(enabled);
            stopScanButton.setAlpha(enabled ? 1f : 0.6f);
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (cameraStarted) {
            stopCamera("Activity destroyed");
        }
        if (cameraExecutor != null) {
            cameraExecutor.shutdown();
        }
        if (barcodeScanner != null) {
            barcodeScanner.close();
        }
    }
}
