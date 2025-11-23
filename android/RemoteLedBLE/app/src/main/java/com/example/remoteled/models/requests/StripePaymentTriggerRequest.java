package com.example.remoteled.models.requests;

import androidx.annotation.Nullable;

import com.google.gson.annotations.SerializedName;

public class StripePaymentTriggerRequest {

    @SerializedName("amount_cents")
    private final int amountCents;

    @SerializedName("customer_id")
    @Nullable
    private final String customerId;

    @SerializedName("device_id")
    private final String deviceId;

    @SerializedName("description")
    @Nullable
    private final String description;

    @SerializedName("duration_seconds")
    @Nullable
    private final Integer durationSeconds;

    @SerializedName("order_id")
    @Nullable
    private final String orderId;

    @SerializedName("skip_led")
    private final boolean skipLed;

    public StripePaymentTriggerRequest(
            int amountCents,
            @Nullable String customerId,
            String deviceId,
            @Nullable String description,
            @Nullable Integer durationSeconds,
            @Nullable String orderId,
            boolean skipLed
    ) {
        this.amountCents = amountCents;
        this.customerId = customerId;
        this.deviceId = deviceId;
        this.description = description;
        this.durationSeconds = durationSeconds;
        this.orderId = orderId;
        this.skipLed = skipLed;
    }
}

