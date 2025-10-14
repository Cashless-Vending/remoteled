package com.example.remoteled;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.remoteled.models.Order;
import com.example.remoteled.models.requests.CreateOrderRequest;
import com.example.remoteled.models.requests.MockPaymentRequest;
import com.example.remoteled.network.RetrofitClient;

import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class PaymentActivity extends AppCompatActivity {
    
    private static final String TAG = "PaymentActivity";
    
    // UI Components
    private TextView backButton;
    private TextView summaryProduct;
    private TextView summaryDuration;
    private TextView summaryDevice;
    private TextView summaryTotal;
    private Button payButton;
    private ProgressBar paymentLoading;
    
    // Data from previous screen
    private String deviceId;
    private String deviceLabel;
    private String deviceLocation;
    private String serviceId;
    private String serviceType;
    private int priceCents;
    private int fixedMinutes;
    
    // Created order
    private Order createdOrder;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_payment);
        
        // Get data from intent
        getIntentData();
        
        // Initialize UI
        initViews();
        setupListeners();
        displaySummary();
    }
    
    private void getIntentData() {
        Intent intent = getIntent();
        deviceId = intent.getStringExtra("DEVICE_ID");
        deviceLabel = intent.getStringExtra("DEVICE_LABEL");
        deviceLocation = intent.getStringExtra("DEVICE_LOCATION");
        serviceId = intent.getStringExtra("SERVICE_ID");
        serviceType = intent.getStringExtra("SERVICE_TYPE");
        priceCents = intent.getIntExtra("SERVICE_PRICE_CENTS", 0);
        fixedMinutes = intent.getIntExtra("SERVICE_FIXED_MINUTES", 0);
        
        Log.d(TAG, "Payment screen opened for device: " + deviceLabel);
        Log.d(TAG, "Service: " + serviceType + " - $" + (priceCents / 100.0));
    }
    
    private void initViews() {
        backButton = findViewById(R.id.back_button);
        summaryProduct = findViewById(R.id.summary_product);
        summaryDuration = findViewById(R.id.summary_duration);
        summaryDevice = findViewById(R.id.summary_device);
        summaryTotal = findViewById(R.id.summary_total);
        payButton = findViewById(R.id.pay_button);
        paymentLoading = findViewById(R.id.payment_loading);
    }
    
    private void setupListeners() {
        backButton.setOnClickListener(v -> finish());
        
        payButton.setOnClickListener(v -> processPayment());
    }
    
    private void displaySummary() {
        // Product name based on type
        String productName = getProductName(serviceType);
        summaryProduct.setText(productName);
        
        // Duration
        String duration = getDurationText(serviceType, fixedMinutes);
        summaryDuration.setText(duration);
        
        // Device
        summaryDevice.setText(deviceLabel);
        
        // Total
        String total = String.format("$%.2f", priceCents / 100.0);
        summaryTotal.setText(total);
        payButton.setText("Pay " + total);
    }
    
    private String getProductName(String type) {
        switch (type) {
            case "TRIGGER": return "Quick Dispense";
            case "FIXED": return "Standard Cycle";
            case "VARIABLE": return "Extended Time";
            default: return "Service";
        }
    }
    
    private String getDurationText(String type, int minutes) {
        switch (type) {
            case "TRIGGER":
                return "Single activation";
            case "FIXED":
                return minutes + " minutes";
            case "VARIABLE":
                return "Variable duration";
            default:
                return "N/A";
        }
    }
    
    private void processPayment() {
        Log.d(TAG, "Starting payment process...");
        
        // Step 1: Create order
        createOrder();
    }
    
    private void createOrder() {
        showLoading();
        
        CreateOrderRequest request = new CreateOrderRequest(deviceId, serviceId, priceCents);
        
        Log.d(TAG, "Creating order...");
        
        RetrofitClient.getInstance()
                .getApiService()
                .createOrder(request)
                .enqueue(new Callback<Order>() {
                    @Override
                    public void onResponse(Call<Order> call, Response<Order> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            createdOrder = response.body();
                            Log.d(TAG, "Order created: " + createdOrder.getId());
                            Log.d(TAG, "Status: " + createdOrder.getStatus());
                            Log.d(TAG, "Authorized minutes: " + createdOrder.getAuthorizedMinutes());
                            
                            // Step 2: Process mock payment
                            processMockPayment();
                        } else {
                            Log.e(TAG, "Failed to create order: " + response.code());
                            hideLoading();
                            showError("Failed to create order");
                        }
                    }
                    
                    @Override
                    public void onFailure(Call<Order> call, Throwable t) {
                        Log.e(TAG, "Network error creating order: " + t.getMessage(), t);
                        hideLoading();
                        showError("Network error. Please check connection.");
                    }
                });
    }
    
    private void processMockPayment() {
        MockPaymentRequest request = new MockPaymentRequest(createdOrder.getId(), true);
        
        Log.d(TAG, "Processing mock payment for order: " + createdOrder.getId());
        
        RetrofitClient.getInstance()
                .getApiService()
                .processMockPayment(request)
                .enqueue(new Callback<Map<String, Object>>() {
                    @Override
                    public void onResponse(Call<Map<String, Object>> call, 
                                         Response<Map<String, Object>> response) {
                        hideLoading();
                        
                        if (response.isSuccessful() && response.body() != null) {
                            Map<String, Object> result = response.body();
                            boolean success = (boolean) result.get("success");
                            
                            if (success) {
                                Log.d(TAG, "Payment successful!");
                                navigateToProcessing();
                            } else {
                                Log.e(TAG, "Payment failed (simulated)");
                                showError("Payment failed");
                            }
                        } else {
                            Log.e(TAG, "Payment API error: " + response.code());
                            showError("Payment processing failed");
                        }
                    }
                    
                    @Override
                    public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                        Log.e(TAG, "Payment network error: " + t.getMessage(), t);
                        hideLoading();
                        showError("Network error during payment");
                    }
                });
    }
    
    private void navigateToProcessing() {
        Intent intent = new Intent(this, ProcessingActivity.class);
        
        // Pass all data forward
        intent.putExtra("DEVICE_ID", deviceId);
        intent.putExtra("DEVICE_LABEL", deviceLabel);
        intent.putExtra("DEVICE_LOCATION", deviceLocation);
        intent.putExtra("ORDER_ID", createdOrder.getId());
        intent.putExtra("SERVICE_TYPE", serviceType);
        intent.putExtra("AUTHORIZED_MINUTES", createdOrder.getAuthorizedMinutes());
        intent.putExtra("AMOUNT_CENTS", priceCents);
        
        startActivity(intent);
        finish();  // Don't allow back to payment screen
    }
    
    private void showLoading() {
        paymentLoading.setVisibility(View.VISIBLE);
        payButton.setEnabled(false);
        payButton.setAlpha(0.5f);
    }
    
    private void hideLoading() {
        paymentLoading.setVisibility(View.GONE);
        payButton.setEnabled(true);
        payButton.setAlpha(1.0f);
    }
    
    private void showError(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }
}

