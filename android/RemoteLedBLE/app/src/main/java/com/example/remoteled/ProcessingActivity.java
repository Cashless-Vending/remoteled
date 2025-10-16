package com.example.remoteled;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.remoteled.models.Authorization;
import com.example.remoteled.models.requests.CreateAuthorizationRequest;
import com.example.remoteled.network.RetrofitClient;
import com.google.gson.Gson;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ProcessingActivity extends AppCompatActivity {
    
    private static final String TAG = "ProcessingActivity";
    
    // UI Components
    private TextView statusText;
    private TextView statusSubtext;
    private TextView step1, step2, step3, step4;
    private View led1, led2, led3;
    private TextView ledStatusText;
    
    // Data
    private String deviceId;
    private String deviceLabel;
    private String orderId;
    private String serviceType;
    private int authorizedMinutes;
    private int amountCents;
    
    // Authorization
    private Authorization authorization;
    
    private Handler handler = new Handler();
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_processing);
        
        // Get data from intent
        getIntentData();
        
        // Initialize UI
        initViews();
        
        // Start authorization process
        startAuthorizationProcess();
    }
    
    private void getIntentData() {
        Intent intent = getIntent();
        deviceId = intent.getStringExtra("DEVICE_ID");
        deviceLabel = intent.getStringExtra("DEVICE_LABEL");
        orderId = intent.getStringExtra("ORDER_ID");
        serviceType = intent.getStringExtra("SERVICE_TYPE");
        authorizedMinutes = intent.getIntExtra("AUTHORIZED_MINUTES", 0);
        amountCents = intent.getIntExtra("AMOUNT_CENTS", 0);
        
        Log.d(TAG, "Processing activation for order: " + orderId);
        Log.d(TAG, "Service type: " + serviceType + ", Duration: " + authorizedMinutes + " min");
    }
    
    private void initViews() {
        statusText = findViewById(R.id.status_text);
        statusSubtext = findViewById(R.id.status_subtext);
        step1 = findViewById(R.id.step_1);
        step2 = findViewById(R.id.step_2);
        step3 = findViewById(R.id.step_3);
        step4 = findViewById(R.id.step_4);
        led1 = findViewById(R.id.led_1);
        led2 = findViewById(R.id.led_2);
        led3 = findViewById(R.id.led_3);
        ledStatusText = findViewById(R.id.led_status_text);
    }
    
    private void startAuthorizationProcess() {
        // Step 1: Payment already authorized (completed in previous screen)
        updateStep(1, "✓ Payment authorized", true);
        
        // Step 2: Create authorization
        handler.postDelayed(() -> {
            updateStep(2, "⟳ Authorization signed", false);
            createAuthorization();
        }, 500);
    }
    
    private void createAuthorization() {
        Log.d(TAG, "Requesting authorization for order: " + orderId);
        
        CreateAuthorizationRequest request = new CreateAuthorizationRequest(orderId);
        
        RetrofitClient.getInstance()
                .getApiService()
                .createAuthorization(request)
                .enqueue(new Callback<Authorization>() {
                    @Override
                    public void onResponse(Call<Authorization> call, 
                                         Response<Authorization> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            authorization = response.body();
                            Log.d(TAG, "Authorization created: " + authorization.getId());
                            Log.d(TAG, "Signature: " + authorization.getSignatureHex().substring(0, 20) + "...");
                            Log.d(TAG, "Nonce: " + authorization.getPayload().getNonce());
                            
                            runOnUiThread(() -> {
                                updateStep(2, "✓ Authorization signed", true);
                                
                                // Step 3: Relay to device
                                handler.postDelayed(() -> {
                                    updateStep(3, "⟳ Relaying to device via BLE...", false);
                                    relayToDevice();
                                }, 500);
                            });
                        } else {
                            Log.e(TAG, "Failed to create authorization: " + response.code());
                            showError("Failed to create authorization");
                        }
                    }
                    
                    @Override
                    public void onFailure(Call<Authorization> call, Throwable t) {
                        Log.e(TAG, "Authorization network error: " + t.getMessage(), t);
                        showError("Network error during authorization");
                    }
                });
    }
    
    private void relayToDevice() {
        // In the real implementation, this would:
        // 1. Connect to Pi via BLE
        // 2. Send authorization payload + signature
        // 3. Wait for STARTED event
        
        // For now, simulate BLE relay with delay
        updateStep(3, "✓ Relayed to device via BLE", true);
        
        handler.postDelayed(() -> {
            updateStep(4, "⟳ Verifying signature...", false);
            
            // Simulate verification
            handler.postDelayed(() -> {
                updateStep(4, "✓ Signature verified", true);
                
                // Show LED activation based on type
                activateLED();
                
                // Navigate to Running screen
                handler.postDelayed(this::navigateToRunning, 1000);
            }, 1500);
        }, 1000);
    }
    
    private void activateLED() {
        int ledIndex = 1;  // Middle LED
        int ledDrawable;
        String statusText;
        
        switch (serviceType) {
            case "TRIGGER":
                ledDrawable = R.drawable.led_circle_blue;
                statusText = "🔵 Blue Blink - TRIGGER";
                break;
            case "FIXED":
                ledDrawable = R.drawable.led_circle_green;
                statusText = "🟢 Green Solid - FIXED";
                break;
            case "VARIABLE":
                ledDrawable = R.drawable.led_circle_amber;
                statusText = "🟠 Amber Solid - VARIABLE";
                break;
            default:
                ledDrawable = R.drawable.led_circle_green;
                statusText = "Device activated";
        }
        
        led2.setBackgroundResource(ledDrawable);
        ledStatusText.setText(statusText);
        this.statusText.setText("Device Activated!");
        statusSubtext.setText("Starting session...");
    }
    
    private void updateStep(int stepNumber, String text, boolean completed) {
        TextView step = getStepView(stepNumber);
        if (step != null) {
            step.setText(text);
            if (completed) {
                step.setTextColor(getColor(R.color.success_text));
                step.setAlpha(1.0f);
            } else {
                step.setTextColor(getColor(R.color.primary_purple));
                step.setAlpha(1.0f);
            }
        }
    }
    
    private TextView getStepView(int stepNumber) {
        switch (stepNumber) {
            case 1: return step1;
            case 2: return step2;
            case 3: return step3;
            case 4: return step4;
            default: return null;
        }
    }
    
    private void navigateToRunning() {
        Intent intent = new Intent(this, RunningActivity.class);
        
        // Pass data forward
        intent.putExtra("DEVICE_ID", deviceId);
        intent.putExtra("DEVICE_LABEL", deviceLabel);
        intent.putExtra("ORDER_ID", orderId);
        intent.putExtra("SERVICE_TYPE", serviceType);
        intent.putExtra("AUTHORIZED_MINUTES", authorizedMinutes);
        intent.putExtra("AMOUNT_CENTS", amountCents);
        
        // Pass authorization if needed for BLE
        if (authorization != null) {
            intent.putExtra("AUTHORIZATION_ID", authorization.getId());
            intent.putExtra("AUTHORIZATION_PAYLOAD", new Gson().toJson(authorization.getPayload()));
            intent.putExtra("AUTHORIZATION_SIGNATURE", authorization.getSignatureHex());
        }
        
        startActivity(intent);
        finish();
    }
    
    private void showError(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
        statusText.setText("Error");
        statusSubtext.setText(message);
        
        // Allow user to go back
        handler.postDelayed(this::finish, 3000);
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacksAndMessages(null);
    }
}




