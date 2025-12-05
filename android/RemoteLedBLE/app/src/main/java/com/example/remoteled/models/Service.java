package com.example.remoteled.models;

import com.google.gson.annotations.SerializedName;

public class Service {
    @SerializedName("id")
    private String id;
    
    @SerializedName("device_id")
    private String deviceId;
    
    @SerializedName("type")
    private String type;  // TRIGGER, FIXED, VARIABLE
    
    @SerializedName("price_cents")
    private int priceCents;
    
    @SerializedName("fixed_minutes")
    private Integer fixedMinutes;
    
    @SerializedName("minutes_per_25c")
    private Integer minutesPer25c;
    
    @SerializedName("active")
    private boolean active;
    
    @SerializedName("created_at")
    private String createdAt;
    
    // Constructors
    public Service() {}
    
    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }
    
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    
    public int getPriceCents() { return priceCents; }
    public void setPriceCents(int priceCents) { this.priceCents = priceCents; }
    
    public Integer getFixedMinutes() { return fixedMinutes; }
    public void setFixedMinutes(Integer fixedMinutes) { this.fixedMinutes = fixedMinutes; }
    
    public Integer getMinutesPer25c() { return minutesPer25c; }
    public void setMinutesPer25c(Integer minutesPer25c) { this.minutesPer25c = minutesPer25c; }
    
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    
    // Helper methods
    public double getPriceDollars() {
        return priceCents / 100.0;
    }
    
    public String getFormattedPrice() {
        return String.format("$%.2f", getPriceDollars());
    }
    
    public String getDescription() {
        switch (type) {
            case "TRIGGER":
                return "⚡ Single activation (2 seconds)";
            case "FIXED":
                return "⏱️ " + fixedMinutes + " minutes fixed duration";
            case "VARIABLE":
                return String.format("🔄 $0.25 per %d minutes", minutesPer25c);
            default:
                return "";
        }
    }
    
    public String getLedIndicator() {
        // All service types use GREEN LED on payment success
        // RED = idle, YELLOW = processing, GREEN = success/running
        return "💡 LED: 🟢 Green on Success";
    }
}




