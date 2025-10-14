package com.example.remoteled.models;

import com.google.gson.annotations.SerializedName;

public class Order {
    @SerializedName("id")
    private String id;
    
    @SerializedName("device_id")
    private String deviceId;
    
    @SerializedName("product_id")
    private String productId;
    
    @SerializedName("amount_cents")
    private int amountCents;
    
    @SerializedName("authorized_minutes")
    private int authorizedMinutes;
    
    @SerializedName("status")
    private String status;  // CREATED, PAID, RUNNING, DONE, FAILED
    
    @SerializedName("created_at")
    private String createdAt;
    
    @SerializedName("updated_at")
    private String updatedAt;
    
    // Constructors
    public Order() {}
    
    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }
    
    public String getProductId() { return productId; }
    public void setProductId(String productId) { this.productId = productId; }
    
    public int getAmountCents() { return amountCents; }
    public void setAmountCents(int amountCents) { this.amountCents = amountCents; }
    
    public int getAuthorizedMinutes() { return authorizedMinutes; }
    public void setAuthorizedMinutes(int authorizedMinutes) { this.authorizedMinutes = authorizedMinutes; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
    
    // Helper methods
    public double getAmountDollars() {
        return amountCents / 100.0;
    }
    
    public String getFormattedAmount() {
        return String.format("$%.2f", getAmountDollars());
    }
    
    public int getAuthorizedSeconds() {
        return authorizedMinutes * 60;
    }
}

