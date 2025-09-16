package com.example.remoteled;
import android.Manifest;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.journeyapps.barcodescanner.BarcodeCallback;
import com.journeyapps.barcodescanner.BarcodeResult;
import com.journeyapps.barcodescanner.BarcodeView;
import com.google.zxing.ResultPoint;

import java.util.List;
import android.content.Intent;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QRCodeScannerActivity extends AppCompatActivity {

    private static final int CAMERA_PERMISSION_REQUEST_CODE = 100;
    private BarcodeView barcodeView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_qrcode_scanner);

        barcodeView = findViewById(R.id.barcode_scanner);

        // Check for camera permissions
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
            startQRCodeScanner();
        } else {
            // Request Camera Permission
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION_REQUEST_CODE);
        }
    }

    private void startQRCodeScanner() {
        barcodeView.decodeContinuous(new BarcodeCallback() {
            @Override
            public void barcodeResult(BarcodeResult result) {
                String qrCodeContent = result.getText();
                if (isValidQRCode(qrCodeContent)) {
                    // Open the deep link
                    openDeepLink(qrCodeContent);
                } else {
                    Toast.makeText(QRCodeScannerActivity.this, "Invalid QR Code Format", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private boolean isValidQRCode(String qrContent) {
        // Regular expression to validate the QR code format
        String qrPattern = "^remoteled://connect/([A-Fa-f0-9]{2}:[A-Fa-f0-9]{2}:[A-Fa-f0-9]{2}:[A-Fa-f0-9]{2}:[A-Fa-f0-9]{2}:[A-Fa-f0-9]{2})/([A-Fa-f0-9]{4})/([A-Fa-f0-9]{4})/([A-Fa-f0-9]{4})$";

        // Create a pattern object
        Pattern pattern = Pattern.compile(qrPattern);

        // Match the QR content against the pattern
        Matcher matcher = pattern.matcher(qrContent);

        return matcher.matches();
    }

    private void openDeepLink(String qrContent) {
        // Create an intent to open the deep link
        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(qrContent));
        if (intent.resolveActivity(getPackageManager()) != null) {
            startActivity(intent);
        } else {
            Toast.makeText(this, "No app can handle this deep link", Toast.LENGTH_SHORT).show();
        }
    }
    @Override
    protected void onResume() {
        super.onResume();
        barcodeView.resume();
    }

    @Override
    protected void onPause() {
        super.onPause();
        barcodeView.pause();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // Permission granted
                startQRCodeScanner();
            } else {
                // Permission denied
                Toast.makeText(this, "Camera permission is required to scan QR codes", Toast.LENGTH_SHORT).show();
                finish();
            }
        }
    }
}
