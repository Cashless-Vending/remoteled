package com.example.remoteled.ble;

import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCharacteristic;
import android.util.Log;

import org.json.JSONObject;

/**
 * Singleton BLE Connection Manager
 * Maintains a single BLE connection shared across all activities
 */
public class BLEConnectionManager {
    private static final String TAG = "BLEConnectionManager";
    private static BLEConnectionManager instance;

    private BluetoothGatt bluetoothGatt;
    private BluetoothGattCharacteristic characteristic;
    private String bleKey;
    private boolean isConnected = false;

    private BLEConnectionManager() {}

    public static synchronized BLEConnectionManager getInstance() {
        if (instance == null) {
            instance = new BLEConnectionManager();
        }
        return instance;
    }

    public void initialize(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, String bleKey) {
        this.bluetoothGatt = gatt;
        this.characteristic = characteristic;
        this.bleKey = bleKey;
        this.isConnected = true;
        Log.d(TAG, "BLE connection initialized in singleton");
    }

    public boolean isConnected() {
        return isConnected && bluetoothGatt != null && characteristic != null;
    }

    public void disconnect() {
        if (bluetoothGatt != null) {
            bluetoothGatt.disconnect();
            bluetoothGatt.close();
            bluetoothGatt = null;
        }
        characteristic = null;
        isConnected = false;
        Log.d(TAG, "BLE disconnected");
    }

    // LED Control Methods
    public void sendBlinkCommand(String color) {
        // Blink continuously until explicitly stopped
        // 9999 times = effectively infinite blinking
        sendCommand("BLINK", color, 9999, 0.5, 0);
    }

    public void sendOnCommand(String color) {
        sendCommand("ON", color, 0, 0, 0);
    }

    public void sendOnCommand(String color, int durationSeconds) {
        sendCommand("ON", color, 0, 0, durationSeconds);
    }

    public void sendOffCommand() {
        // Turn off ALL LEDs with single command
        // Pi side handles turning off all colors
        sendCommand("OFF", "all", 0, 0, 0);
    }

    private void sendCommand(String command, String color, int times, double interval, int duration) {
        if (!isConnected()) {
            Log.w(TAG, "Not connected, cannot send command: " + command);
            return;
        }

        try {
            JSONObject json = new JSONObject();
            json.put("command", command);
            json.put("color", color);
            json.put("bleKey", bleKey);
            if (times > 0) {
                json.put("times", times);
                json.put("interval", interval);
            }
            if (duration > 0) {
                json.put("duration", duration);
            }

            String payload = json.toString();
            Log.d(TAG, "Sending BLE command: " + payload);

            characteristic.setValue(payload.getBytes());
            bluetoothGatt.writeCharacteristic(characteristic);
        } catch (Exception e) {
            Log.e(TAG, "Error sending command: " + e.getMessage());
        }
    }
}
