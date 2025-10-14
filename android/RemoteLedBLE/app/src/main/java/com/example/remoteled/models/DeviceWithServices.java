package com.example.remoteled.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class DeviceWithServices {
    @SerializedName("device")
    private Device device;
    
    @SerializedName("services")
    private List<Service> services;
    
    // Constructors
    public DeviceWithServices() {}
    
    public DeviceWithServices(Device device, List<Service> services) {
        this.device = device;
        this.services = services;
    }
    
    // Getters and Setters
    public Device getDevice() { return device; }
    public void setDevice(Device device) { this.device = device; }
    
    public List<Service> getServices() { return services; }
    public void setServices(List<Service> services) { this.services = services; }
}

