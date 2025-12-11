package com.example.remoteled.models.requests;

import com.google.gson.annotations.SerializedName;

public class CreateOrderRequest {
    @SerializedName("device_id")
    private String deviceId;

    @SerializedName("service_id")
    private String serviceId;

    @SerializedName("amount_cents")
    private int amountCents;

    public CreateOrderRequest(String deviceId, String serviceId, int amountCents) {
        this.deviceId = deviceId;
        this.serviceId = serviceId;
        this.amountCents = amountCents;
    }

    // Getters
    public String getDeviceId() { return deviceId; }
    public String getServiceId() { return serviceId; }
    public int getAmountCents() { return amountCents; }
}




