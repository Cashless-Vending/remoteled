package com.example.remoteled.models;

import com.google.gson.annotations.SerializedName;

public class Authorization {
    @SerializedName("id")
    private String id;
    
    @SerializedName("order_id")
    private String orderId;
    
    @SerializedName("device_id")
    private String deviceId;
    
    @SerializedName("payload")
    private AuthorizationPayload payload;
    
    @SerializedName("signature_hex")
    private String signatureHex;
    
    @SerializedName("expires_at")
    private String expiresAt;
    
    @SerializedName("created_at")
    private String createdAt;
    
    // Constructors
    public Authorization() {}
    
    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }
    
    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }
    
    public AuthorizationPayload getPayload() { return payload; }
    public void setPayload(AuthorizationPayload payload) { this.payload = payload; }
    
    public String getSignatureHex() { return signatureHex; }
    public void setSignatureHex(String signatureHex) { this.signatureHex = signatureHex; }
    
    public String getExpiresAt() { return expiresAt; }
    public void setExpiresAt(String expiresAt) { this.expiresAt = expiresAt; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    
    // Inner class for payload
    public static class AuthorizationPayload {
        @SerializedName("deviceId")
        private String deviceId;
        
        @SerializedName("orderId")
        private String orderId;
        
        @SerializedName("type")
        private String type;
        
        @SerializedName("seconds")
        private int seconds;
        
        @SerializedName("nonce")
        private String nonce;
        
        @SerializedName("exp")
        private long exp;
        
        // Getters and Setters
        public String getDeviceId() { return deviceId; }
        public void setDeviceId(String deviceId) { this.deviceId = deviceId; }
        
        public String getOrderId() { return orderId; }
        public void setOrderId(String orderId) { this.orderId = orderId; }
        
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        
        public int getSeconds() { return seconds; }
        public void setSeconds(int seconds) { this.seconds = seconds; }
        
        public String getNonce() { return nonce; }
        public void setNonce(String nonce) { this.nonce = nonce; }
        
        public long getExp() { return exp; }
        public void setExp(long exp) { this.exp = exp; }
    }
}

