package com.example.remoteled.ble;

/**
 * BLE Configuration for connecting to Pi
 * These values match the Pi's BLE peripheral configuration
 */
public class BleConfig {
    // BLE Connection Parameters
    // TODO: Update MAC_ADDRESS with your Pi's Bluetooth MAC address
    // You can find it by running: hciconfig on the Pi
    public static final String MAC_ADDRESS = "00:00:00:00:00:00";  // PLACEHOLDER - UPDATE ME

    // BLE UUIDs (matches Pi configuration)
    public static final String SERVICE_UUID = "00007514-0000-1000-8000-00805f9b34fb";
    public static final String CHARACTERISTIC_UUID = "0000DE40-0000-1000-8000-00805f9b34fb";

    // BLE Authentication Key
    public static final String BLE_KEY = "9F64";

    // LED Colors
    public static final String COLOR_RED = "red";
    public static final String COLOR_YELLOW = "yellow";
    public static final String COLOR_GREEN = "green";
}
