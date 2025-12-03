package com.example.remoteled;

import android.content.Intent;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.remoteled.ble.BLEConnectionManager;
import com.example.remoteled.models.Order;
import com.example.remoteled.models.requests.TelemetryRequest;
import com.example.remoteled.network.RetrofitClient;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class RunningActivity extends AppCompatActivity {
    
    private static final String TAG = "RunningActivity";
    
    // UI Components
    private TextView countdownTime;
    private TextView detailsProduct;
    private TextView detailsStartedAt;
    private TextView detailsEstimatedEnd;
    private TextView detailsOrderId;
    private View runningLed;
    private TextView runningLedText;
    private Button viewHistoryButton;
    
    // Data
    private String deviceId;
    private String deviceLabel;
    private String orderId;
    private String serviceType;
    private int authorizedMinutes;
    private int amountCents;
    
    // Timer
    private CountDownTimer countDownTimer;
    private long remainingTimeMillis;
    private Date startTime;

    // Status polling
    private Handler statusPollHandler = new Handler();
    private static final int POLL_INTERVAL_MS = 3000;  // 3 seconds
    private boolean isPolling = false;
    private boolean isGreenLEDOn = false;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_running);
        
        // Get data
        getIntentData();
        
        // Initialize UI
        initViews();
        setupListeners();
        displayDetails();

        // Send STARTED telemetry and turn on GREEN LED
        sendTelemetry("STARTED");

        // Start countdown
        startCountdown();

        // Start polling order status
        startStatusPolling();
    }
    
    private void getIntentData() {
        Intent intent = getIntent();
        deviceId = intent.getStringExtra("DEVICE_ID");
        deviceLabel = intent.getStringExtra("DEVICE_LABEL");
        orderId = intent.getStringExtra("ORDER_ID");
        serviceType = intent.getStringExtra("SERVICE_TYPE");
        authorizedMinutes = intent.getIntExtra("AUTHORIZED_MINUTES", 0);
        amountCents = intent.getIntExtra("AMOUNT_CENTS", 0);

        startTime = new Date();

        Log.d(TAG, "Running screen for order: " + orderId);
        Log.d(TAG, "Duration: " + authorizedMinutes + " minutes");
    }
    
    private void initViews() {
        countdownTime = findViewById(R.id.countdown_time);
        detailsProduct = findViewById(R.id.details_product);
        detailsStartedAt = findViewById(R.id.details_started_at);
        detailsEstimatedEnd = findViewById(R.id.details_estimated_end);
        detailsOrderId = findViewById(R.id.details_order_id);
        runningLed = findViewById(R.id.running_led);
        runningLedText = findViewById(R.id.running_led_text);
        viewHistoryButton = findViewById(R.id.view_history_button);
    }
    
    private void setupListeners() {
        viewHistoryButton.setOnClickListener(v -> 
            Toast.makeText(this, "Order history feature coming soon", Toast.LENGTH_SHORT).show()
        );
    }
    
    private void displayDetails() {
        // Product name
        String productName = getProductName(serviceType);
        detailsProduct.setText(productName);
        
        // Started at time
        SimpleDateFormat timeFormat = new SimpleDateFormat("h:mm a", Locale.getDefault());
        detailsStartedAt.setText(timeFormat.format(startTime));
        
        // Estimated end time
        Calendar endCal = Calendar.getInstance();
        endCal.setTime(startTime);
        endCal.add(Calendar.MINUTE, authorizedMinutes);
        detailsEstimatedEnd.setText(timeFormat.format(endCal.getTime()));
        
        // Order ID (show first 12 chars)
        String shortOrderId = orderId.length() > 12 ? 
            "ord_" + orderId.substring(0, 12) : orderId;
        detailsOrderId.setText(shortOrderId);
        
        // LED Status based on service type
        setLEDStatus();
    }
    
    private void setLEDStatus() {
        int ledDrawable;
        String ledText;
        
        switch (serviceType) {
            case "TRIGGER":
                ledDrawable = R.drawable.led_circle_blue;
                ledText = "🔵 Blue Blink - TRIGGER Product";
                break;
            case "FIXED":
                ledDrawable = R.drawable.led_circle_green;
                ledText = "🟢 Green Solid - FIXED Product Running";
                break;
            case "VARIABLE":
                ledDrawable = R.drawable.led_circle_amber;
                ledText = "🟠 Amber Solid - VARIABLE Product Running";
                break;
            default:
                ledDrawable = R.drawable.led_circle_green;
                ledText = "Device Running";
        }
        
        runningLed.setBackgroundResource(ledDrawable);
        runningLedText.setText(ledText);
    }
    
    private String getProductName(String type) {
        switch (type) {
            case "TRIGGER": return "Quick Dispense";
            case "FIXED": return "Standard Cycle";
            case "VARIABLE": return "Extended Time";
            default: return "Service";
        }
    }
    
    private void startCountdown() {
        if (serviceType.equals("TRIGGER")) {
            // TRIGGER has no duration, complete immediately
            countdownTime.setText("00:02");
            // Send DONE telemetry - polling will detect status change
            sendTelemetry("DONE");
            return;
        }

        // FOR TESTING: Use 30 seconds instead of actual authorized minutes
        // TODO: Change back to: remainingTimeMillis = authorizedMinutes * 60 * 1000;
        remainingTimeMillis = 30 * 1000;  // 30 seconds for testing
        
        countDownTimer = new CountDownTimer(remainingTimeMillis, 1000) {
            @Override
            public void onTick(long millisUntilFinished) {
                remainingTimeMillis = millisUntilFinished;
                updateCountdownDisplay(millisUntilFinished);
            }
            
            @Override
            public void onFinish() {
                countdownTime.setText("00:00");
                Log.d(TAG, "Countdown finished, sending DONE telemetry");

                // Send DONE telemetry - server will update status to DONE
                // Polling will detect the status change and turn off GREEN LED
                sendTelemetry("DONE");
            }
        }.start();
    }
    
    private void updateCountdownDisplay(long millisUntilFinished) {
        long minutes = (millisUntilFinished / 1000) / 60;
        long seconds = (millisUntilFinished / 1000) % 60;
        
        String timeString = String.format(Locale.getDefault(), "%02d:%02d", minutes, seconds);
        countdownTime.setText(timeString);
    }
    
    private void sendTelemetry(String event) {
        Log.d(TAG, "Sending telemetry: " + event + " for order: " + orderId);

        TelemetryRequest request = new TelemetryRequest(event, orderId);

        RetrofitClient.getInstance()
                .getApiService()
                .sendTelemetry(deviceId, request)
                .enqueue(new Callback<Map<String, Object>>() {
                    @Override
                    public void onResponse(Call<Map<String, Object>> call,
                                         Response<Map<String, Object>> response) {
                        if (response.isSuccessful()) {
                            Log.d(TAG, "Telemetry " + event + " sent successfully");
                            // After STARTED telemetry succeeds, start polling to check when status becomes RUNNING
                            if (event.equals("STARTED")) {
                                Log.d(TAG, "STARTED telemetry sent, server should update to RUNNING soon");
                            }
                        } else {
                            Log.w(TAG, "Telemetry failed: " + response.code());
                        }
                    }

                    @Override
                    public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                        Log.e(TAG, "Telemetry network error: " + t.getMessage());
                    }
                });
    }
    
    private void navigateToQRScreen() {
        if (countDownTimer != null) {
            countDownTimer.cancel();
        }

        Log.d(TAG, "Service completed, returning to QR screen for next user");

        // Navigate back to MainActivity (QR scanner)
        Intent intent = new Intent(this, MainActivity.class);
        // Clear all activities above MainActivity
        intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
        finish();
    }
    
    private void startGreenLED() {
        // Send GREEN ON with 30-second duration for Pi status page
        BLEConnectionManager.getInstance().sendOnCommand("green", 30);
        Log.d(TAG, "Started GREEN LED with 30s duration");
    }

    private void stopGreenLED() {
        BLEConnectionManager.getInstance().sendOffCommand();
        Log.d(TAG, "Stopped GREEN LED");
    }

    private void startStatusPolling() {
        if (isPolling) {
            Log.w(TAG, "Status polling already running");
            return;
        }

        isPolling = true;
        Log.d(TAG, "Starting order status polling (every " + POLL_INTERVAL_MS + "ms)");
        pollOrderStatus();
    }

    private void stopStatusPolling() {
        isPolling = false;
        statusPollHandler.removeCallbacksAndMessages(null);
        Log.d(TAG, "Stopped order status polling");
    }

    private void pollOrderStatus() {
        if (!isPolling) {
            return;
        }

        Log.d(TAG, "Polling order status for: " + orderId);

        RetrofitClient.getInstance()
                .getApiService()
                .getOrder(orderId)
                .enqueue(new Callback<Order>() {
                    @Override
                    public void onResponse(Call<Order> call, Response<Order> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            Order order = response.body();
                            String status = order.getStatus();
                            Log.d(TAG, "Polled order status: " + status);

                            // Turn GREEN LED ON when status is RUNNING (only once)
                            if ("RUNNING".equals(status)) {
                                if (!isGreenLEDOn) {
                                    // Add 500ms delay to avoid GPIO timing conflicts
                                    statusPollHandler.postDelayed(() -> {
                                        startGreenLED();
                                        isGreenLEDOn = true;
                                    }, 500);
                                }
                                scheduleNextPoll();
                            }
                            // Turn GREEN LED OFF and navigate when status is DONE
                            else if ("DONE".equals(status)) {
                                Log.d(TAG, "Order status is DONE - stopping device");
                                stopStatusPolling();
                                if (isGreenLEDOn) {
                                    stopGreenLED();
                                    isGreenLEDOn = false;
                                }
                                navigateToQRScreen();
                            }
                            // For other statuses (PAID, CREATED, etc.), keep polling
                            else {
                                Log.d(TAG, "Status not RUNNING yet, will poll again");
                                scheduleNextPoll();
                            }
                        } else {
                            Log.w(TAG, "Failed to fetch order status: " + response.code());
                            scheduleNextPoll();
                        }
                    }

                    @Override
                    public void onFailure(Call<Order> call, Throwable t) {
                        Log.e(TAG, "Error polling order status: " + t.getMessage());
                        scheduleNextPoll();
                    }
                });
    }

    private void scheduleNextPoll() {
        if (isPolling) {
            statusPollHandler.postDelayed(this::pollOrderStatus, POLL_INTERVAL_MS);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();

        // Stop polling
        stopStatusPolling();

        // Cancel countdown timer
        if (countDownTimer != null) {
            countDownTimer.cancel();
        }
    }
}




