package com.example.remoteled.models.requests;

import com.google.gson.annotations.SerializedName;

public class OrderStatusUpdateRequest {

    @SerializedName("status")
    private final String status;

    public OrderStatusUpdateRequest(String status) {
        this.status = status;
    }
}

