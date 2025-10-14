package com.example.remoteled.models;

import com.google.gson.annotations.SerializedName;

public class Device {
    @SerializedName("id")
    private String id;
    
    @SerializedName("label")
    private String label;
    
    @SerializedName("model")
    private String model;
    
    @SerializedName("location")
    private String location;
    
    @SerializedName("status")
    private String status;
    
    @SerializedName("created_at")
    private String createdAt;
    
    // Constructors
    public Device() {}
    
    public Device(String id, String label, String model, String location, String status) {
        this.id = id;
        this.label = label;
        this.model = model;
        this.location = location;
        this.status = status;
    }
    
    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getLabel() { return label; }
    public void setLabel(String label) { this.label = label; }
    
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}

