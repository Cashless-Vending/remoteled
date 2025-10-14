package com.example.remoteled.models.requests;

import com.google.gson.annotations.SerializedName;

public class CreateAuthorizationRequest {
    @SerializedName("order_id")
    private String orderId;
    
    public CreateAuthorizationRequest(String orderId) {
        this.orderId = orderId;
    }
    
    // Getter
    public String getOrderId() { return orderId; }
}

