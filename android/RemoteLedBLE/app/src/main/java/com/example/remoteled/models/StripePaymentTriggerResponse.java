package com.example.remoteled.models;

import com.google.gson.annotations.SerializedName;

public class StripePaymentTriggerResponse {

    @SerializedName("payment_intent_id")
    private String paymentIntentId;

    @SerializedName("amount_cents")
    private int amountCents;

    @SerializedName("payment_status")
    private String paymentStatus;

    @SerializedName("customer_id")
    private String customerId;

    @SerializedName("led_triggered")
    private boolean ledTriggered;

    @SerializedName("led_color")
    private String ledColor;

    @SerializedName("led_device_id")
    private String ledDeviceId;

    @SerializedName("created_at")
    private long createdAt;

    public String getPaymentIntentId() {
        return paymentIntentId;
    }

    public int getAmountCents() {
        return amountCents;
    }

    public String getPaymentStatus() {
        return paymentStatus;
    }

    public String getCustomerId() {
        return customerId;
    }

    public boolean isLedTriggered() {
        return ledTriggered;
    }

    public String getLedColor() {
        return ledColor;
    }

    public String getLedDeviceId() {
        return ledDeviceId;
    }

    public long getCreatedAt() {
        return createdAt;
    }
}

