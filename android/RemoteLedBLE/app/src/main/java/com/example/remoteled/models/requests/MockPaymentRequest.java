package com.example.remoteled.models.requests;

import com.google.gson.annotations.SerializedName;

public class MockPaymentRequest {
    @SerializedName("order_id")
    private String orderId;
    
    @SerializedName("success")
    private boolean success;
    
    public MockPaymentRequest(String orderId, boolean success) {
        this.orderId = orderId;
        this.success = success;
    }
    
    // Getters
    public String getOrderId() { return orderId; }
    public boolean isSuccess() { return success; }
}




