package com.example.remoteled.models.requests;

import com.google.gson.annotations.SerializedName;

public class TelemetryRequest {
    @SerializedName("event")
    private String event;  // STARTED, DONE, ERROR
    
    @SerializedName("order_id")
    private String orderId;
    
    @SerializedName("details")
    private String details;
    
    @SerializedName("payload_hash")
    private String payloadHash;
    
    public TelemetryRequest(String event, String orderId) {
        this.event = event;
        this.orderId = orderId;
    }
    
    public TelemetryRequest(String event, String orderId, String details) {
        this.event = event;
        this.orderId = orderId;
        this.details = details;
    }
    
    // Getters and Setters
    public String getEvent() { return event; }
    public void setEvent(String event) { this.event = event; }
    
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }
    
    public String getDetails() { return details; }
    public void setDetails(String details) { this.details = details; }
    
    public String getPayloadHash() { return payloadHash; }
    public void setPayloadHash(String payloadHash) { this.payloadHash = payloadHash; }
}




