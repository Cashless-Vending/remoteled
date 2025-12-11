package com.example.remoteled.models.requests;

import com.google.gson.annotations.SerializedName;

public class LEDControlRequest {
    @SerializedName("color")
    private String color;  // red, yellow, green

    @SerializedName("mode")
    private String mode;   // blink, on, off

    public LEDControlRequest(String color, String mode) {
        this.color = color;
        this.mode = mode;
    }

    // Getters
    public String getColor() { return color; }
    public String getMode() { return mode; }
}
