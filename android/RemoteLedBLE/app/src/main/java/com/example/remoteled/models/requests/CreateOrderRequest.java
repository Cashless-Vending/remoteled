package com.example.remoteled.models.requests;

import com.google.gson.annotations.SerializedName;

public class CreateOrderRequest {
    @SerializedName("device_id")
    private String deviceId;
    
    @SerializedName("product_id")
    private String productId;
    
    @SerializedName("amount_cents")
    private int amountCents;
    
    public CreateOrderRequest(String deviceId, String productId, int amountCents) {
        this.deviceId = deviceId;
        this.productId = productId;
        this.amountCents = amountCents;
    }
    
    // Getters
    public String getDeviceId() { return deviceId; }
    public String getProductId() { return productId; }
    public int getAmountCents() { return amountCents; }
}

