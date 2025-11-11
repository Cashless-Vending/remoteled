package com.example.remoteled.network;

import com.example.remoteled.models.*;
import com.example.remoteled.models.requests.*;

import java.util.Map;

import retrofit2.Call;
import retrofit2.http.*;

public interface ApiService {
    
    // Device Endpoints
    @GET("devices/{device_id}")
    Call<Device> getDevice(@Path("device_id") String deviceId);
    
    @GET("devices/{device_id}/full")
    Call<DeviceWithServices> getDeviceWithServices(@Path("device_id") String deviceId);
    
    // Order Endpoints
    @POST("orders")
    Call<Order> createOrder(@Body CreateOrderRequest request);
    
    @GET("orders/{order_id}")
    Call<Order> getOrder(@Path("order_id") String orderId);

    @PATCH("orders/{order_id}/status")
    Call<Order> updateOrderStatus(
            @Path("order_id") String orderId,
            @Body OrderStatusUpdateRequest request
    );
    
    // Payment Endpoints
    @POST("payments/stripe/payment-and-trigger")
    Call<StripePaymentTriggerResponse> processStripePayment(
            @Body StripePaymentTriggerRequest request
    );
    
    // Authorization Endpoints
    @POST("authorizations")
    Call<Authorization> createAuthorization(@Body CreateAuthorizationRequest request);
    
    @GET("authorizations/order/{order_id}")
    Call<Authorization> getAuthorizationByOrder(@Path("order_id") String orderId);
    
    // Telemetry Endpoints
    @POST("devices/{device_id}/telemetry")
    Call<Map<String, Object>> sendTelemetry(
        @Path("device_id") String deviceId,
        @Body TelemetryRequest request
    );
    
    // Health Check
    @GET("health")
    Call<Map<String, Object>> healthCheck();
}




