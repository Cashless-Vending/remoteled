package com.example.remoteled.network;

import com.example.remoteled.BuildConfig;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

import java.util.concurrent.TimeUnit;

public class RetrofitClient {
    private static RetrofitClient instance;
    private final ApiService apiService;
    private final Retrofit retrofit;
    
    // Base URL - can be configured
    private static String BASE_URL = "http://10.0.2.2:8000/";  // Emulator localhost
    // For physical device on same network, use: "http://YOUR_IP:8000/"
    
    private RetrofitClient() {
        // Logging interceptor for debugging
        HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
        loggingInterceptor.setLevel(HttpLoggingInterceptor.Level.BODY);
        
        // OkHttp client with timeouts
        OkHttpClient okHttpClient = new OkHttpClient.Builder()
                .addInterceptor(loggingInterceptor)
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();
        
        // Gson for JSON parsing
        Gson gson = new GsonBuilder()
                .setLenient()
                .create();
        
        // Retrofit instance
        retrofit = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(okHttpClient)
                .addConverterFactory(GsonConverterFactory.create(gson))
                .build();
        
        apiService = retrofit.create(ApiService.class);
    }
    
    public static synchronized RetrofitClient getInstance() {
        if (instance == null) {
            instance = new RetrofitClient();
        }
        return instance;
    }
    
    public ApiService getApiService() {
        return apiService;
    }
    
    public static void setBaseUrl(String url) {
        BASE_URL = url;
        instance = null;  // Reset instance to recreate with new URL
    }
    
    public static String getBaseUrl() {
        return BASE_URL;
    }
}




