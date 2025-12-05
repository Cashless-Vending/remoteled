package com.example.remoteled;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.example.remoteled.ble.BLEConnectionManager;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class SuccessActivity extends AppCompatActivity {
    
    private static final String TAG = "SuccessActivity";
    
    // UI Components
    private TextView closeButton;
    private TextView summaryProduct;
    private TextView summaryDuration;
    private TextView summaryAmount;
    private TextView summaryDevice;
    private TextView summaryCompletedAt;
    private Button doneButton;
    private Button startAnotherButton;
    
    // Data
    private String deviceLabel;
    private String orderId;
    private String serviceType;
    private int authorizedMinutes;
    private int amountCents;
    private long startedAtMillis;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_success);
        
        // Get data
        getIntentData();
        
        // Initialize UI
        initViews();
        setupListeners();
        displaySummary();
    }
    
    private void getIntentData() {
        Intent intent = getIntent();
        deviceLabel = intent.getStringExtra("DEVICE_LABEL");
        orderId = intent.getStringExtra("ORDER_ID");
        serviceType = intent.getStringExtra("SERVICE_TYPE");
        authorizedMinutes = intent.getIntExtra("AUTHORIZED_MINUTES", 0);
        amountCents = intent.getIntExtra("AMOUNT_CENTS", 0);
        startedAtMillis = intent.getLongExtra("STARTED_AT", System.currentTimeMillis());
    }
    
    private void initViews() {
        closeButton = findViewById(R.id.close_button);
        summaryProduct = findViewById(R.id.summary_product);
        summaryDuration = findViewById(R.id.summary_duration);
        summaryAmount = findViewById(R.id.summary_amount);
        summaryDevice = findViewById(R.id.summary_device);
        summaryCompletedAt = findViewById(R.id.summary_completed_at);
        doneButton = findViewById(R.id.done_button);
        startAnotherButton = findViewById(R.id.start_another_button);
    }
    
    private void setupListeners() {
        closeButton.setOnClickListener(v -> finishAndGoHome());
        
        doneButton.setOnClickListener(v -> finishAndGoHome());
        
        startAnotherButton.setOnClickListener(v -> {
            // Go back to QR scanner for another session
            Intent intent = new Intent(this, QRCodeScannerActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
            finish();
        });
    }
    
    private void displaySummary() {
        // Product
        String productName = getProductName(serviceType);
        summaryProduct.setText(productName);
        
        // Duration (actual completion time)
        if (serviceType.equals("TRIGGER")) {
            summaryDuration.setText("Single activation");
        } else {
            summaryDuration.setText(authorizedMinutes + " minutes");
        }
        
        // Amount
        String amount = String.format("$%.2f", amountCents / 100.0);
        summaryAmount.setText(amount);
        
        // Device
        summaryDevice.setText(deviceLabel);
        
        // Completed at (current time)
        SimpleDateFormat timeFormat = new SimpleDateFormat("h:mm a", Locale.getDefault());
        summaryCompletedAt.setText(timeFormat.format(new Date()));
    }
    
    private String getProductName(String type) {
        switch (type) {
            case "TRIGGER": return "Quick Dispense";
            case "FIXED": return "Standard Cycle";
            case "VARIABLE": return "Extended Time";
            default: return "Service";
        }
    }
    
    private void finishAndGoHome() {
        // Send OFF command to Pi to reset LED to RED and show QR again
        Log.d(TAG, "Sending OFF command to Pi to reset for next user");
        BLEConnectionManager.getInstance().sendOffCommand();
        
        // Close all activities and return to home (QR scanner)
        Intent intent = new Intent(this, QRCodeScannerActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
        finish();
    }
    
    @Override
    public void onBackPressed() {
        // Prevent going back, user must use Done or Start Another
        // Do nothing or show message
    }
}




