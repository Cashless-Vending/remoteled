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
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.remoteled.adapters.ProductAdapter;
import com.example.remoteled.models.Device;
import com.example.remoteled.models.DeviceWithServices;
import com.example.remoteled.models.Service;
import com.example.remoteled.network.RetrofitClient;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ProductSelectionActivity extends AppCompatActivity {
    
    private static final String TAG = "ProductSelection";
    
    // UI Components
    private TextView deviceName;
    private TextView deviceLocation;
    private RecyclerView productsRecyclerView;
    private ProgressBar loadingIndicator;
    private TextView errorMessage;
    private Button continueButton;
    private TextView backButton;
    
    // Data
    private String deviceId;
    private Device currentDevice;
    private ProductAdapter productAdapter;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_product_selection);
        
        // Get device ID from intent
        deviceId = getIntent().getStringExtra("DEVICE_ID");
        if (deviceId == null || deviceId.isEmpty()) {
            Toast.makeText(this, "Error: No device ID provided", Toast.LENGTH_LONG).show();
            finish();
            return;
        }
        
        // Initialize UI components
        initViews();
        setupRecyclerView();
        setupListeners();
        
        // Fetch device and services from API
        fetchDeviceWithServices();
    }
    
    private void initViews() {
        deviceName = findViewById(R.id.device_name);
        deviceLocation = findViewById(R.id.device_location);
        productsRecyclerView = findViewById(R.id.products_recycler_view);
        loadingIndicator = findViewById(R.id.loading_indicator);
        errorMessage = findViewById(R.id.error_message);
        continueButton = findViewById(R.id.continue_button);
        backButton = findViewById(R.id.back_button);
    }
    
    private void setupRecyclerView() {
        productAdapter = new ProductAdapter((service, position) -> {
            // Enable continue button when product is selected
            continueButton.setEnabled(true);
            continueButton.setAlpha(1.0f);
            Log.d(TAG, "Product selected: " + service.getType() + " - " + service.getFormattedPrice());
        });
        
        productsRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        productsRecyclerView.setAdapter(productAdapter);
    }
    
    private void setupListeners() {
        backButton.setOnClickListener(v -> finish());
        
        continueButton.setOnClickListener(v -> {
            Service selectedService = productAdapter.getSelectedService();
            if (selectedService != null && currentDevice != null) {
                navigateToPayment(selectedService);
            } else {
                Toast.makeText(this, "Please select a product", Toast.LENGTH_SHORT).show();
            }
        });
    }
    
    private void fetchDeviceWithServices() {
        showLoading();
        
        Log.d(TAG, "Fetching device and services for ID: " + deviceId);
        
        RetrofitClient.getInstance()
                .getApiService()
                .getDeviceWithServices(deviceId)
                .enqueue(new Callback<DeviceWithServices>() {
                    @Override
                    public void onResponse(Call<DeviceWithServices> call, 
                                         Response<DeviceWithServices> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            DeviceWithServices data = response.body();
                            currentDevice = data.getDevice();
                            
                            Log.d(TAG, "Device loaded: " + currentDevice.getLabel());
                            Log.d(TAG, "Services count: " + data.getServices().size());
                            
                            runOnUiThread(() -> {
                                displayDeviceInfo(currentDevice);
                                displayServices(data.getServices());
                                hideLoading();
                            });
                        } else {
                            Log.e(TAG, "API Error: " + response.code() + " - " + response.message());
                            runOnUiThread(() -> showError("Device not found or unavailable"));
                        }
                    }
                    
                    @Override
                    public void onFailure(Call<DeviceWithServices> call, Throwable t) {
                        Log.e(TAG, "Network error: " + t.getMessage(), t);
                        runOnUiThread(() -> showError("Network error. Please check connection."));
                    }
                });
    }
    
    private void displayDeviceInfo(Device device) {
        deviceName.setText(device.getLabel());
        deviceLocation.setText("📍 " + (device.getLocation() != null ? device.getLocation() : "Location unavailable"));
    }
    
    private void displayServices(List<Service> services) {
        if (services.isEmpty()) {
            showError("No products available for this device");
            return;
        }
        
        productAdapter.setServices(services);
        productsRecyclerView.setVisibility(View.VISIBLE);
        continueButton.setVisibility(View.VISIBLE);
    }
    
    private void showLoading() {
        loadingIndicator.setVisibility(View.VISIBLE);
        productsRecyclerView.setVisibility(View.GONE);
        errorMessage.setVisibility(View.GONE);
        continueButton.setVisibility(View.GONE);
    }
    
    private void hideLoading() {
        loadingIndicator.setVisibility(View.GONE);
    }
    
    private void showError(String message) {
        loadingIndicator.setVisibility(View.GONE);
        productsRecyclerView.setVisibility(View.GONE);
        continueButton.setVisibility(View.GONE);
        errorMessage.setVisibility(View.VISIBLE);
        errorMessage.setText(message);
    }
    
    private void navigateToPayment(Service selectedService) {
        Intent intent = new Intent(this, PaymentActivity.class);
        
        // Pass device and service info
        intent.putExtra("DEVICE_ID", currentDevice.getId());
        intent.putExtra("DEVICE_LABEL", currentDevice.getLabel());
        intent.putExtra("DEVICE_LOCATION", currentDevice.getLocation());
        intent.putExtra("SERVICE_ID", selectedService.getId());
        intent.putExtra("SERVICE_TYPE", selectedService.getType());
        intent.putExtra("SERVICE_PRICE_CENTS", selectedService.getPriceCents());
        intent.putExtra("SERVICE_FIXED_MINUTES", selectedService.getFixedMinutes() != null ? 
            selectedService.getFixedMinutes() : 0);
        
        startActivity(intent);
    }
}




