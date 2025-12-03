package com.example.remoteled.ble;

import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCharacteristic;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.json.JSONObject;

import java.util.LinkedList;
import java.util.Queue;

/**
 * Singleton BLE Connection Manager with Write Queue
 * Maintains a single BLE connection shared across all activities
 * Handles BLE write operations sequentially to avoid race conditions
 */
public class BLEConnectionManager {
    private static final String TAG = "BLEConnectionManager";
    private static BLEConnectionManager instance;

    private BluetoothGatt bluetoothGatt;
    private BluetoothGattCharacteristic characteristic;
    private String bleKey;
    private boolean isConnected = false;

    // Write queue to handle sequential BLE operations
    private final Queue<String> writeQueue = new LinkedList<>();
    private boolean isWriting = false;
    private final Handler handler = new Handler(Looper.getMainLooper());

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

    /**
     * Called when a BLE write completes (from BluetoothGattCallback)
     */
    public void onWriteComplete() {
        isWriting = false;
        // Process next command in queue after a small delay
        handler.postDelayed(this::processNextWrite, 100);
    }

    /**
     * Process the next write command from the queue
     */
    private void processNextWrite() {
        synchronized (writeQueue) {
            if (isWriting || writeQueue.isEmpty()) {
                return;
            }

            String payload = writeQueue.poll();
            if (payload != null) {
                isWriting = true;
                executeWrite(payload);
            }
        }
    }

    /**
     * Execute the actual BLE write operation
     */
    private void executeWrite(String payload) {
        if (!isConnected()) {
            Log.w(TAG, "Not connected, cannot write: " + payload);
            isWriting = false;
            return;
        }

        try {
            Log.d(TAG, "Executing BLE write: " + payload);
            characteristic.setValue(payload.getBytes());
            boolean success = bluetoothGatt.writeCharacteristic(characteristic);

            if (!success) {
                Log.e(TAG, "writeCharacteristic returned false");
                isWriting = false;
                // Try next command after delay
                handler.postDelayed(this::processNextWrite, 100);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error writing characteristic: " + e.getMessage());
            isWriting = false;
            handler.postDelayed(this::processNextWrite, 100);
        }
    }

    /**
     * Queue a BLE command to be sent
     */
    private void queueCommand(String payload) {
        synchronized (writeQueue) {
            writeQueue.offer(payload);
            Log.d(TAG, "Queued command (queue size: " + writeQueue.size() + ")");
        }
        processNextWrite();
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
            Log.d(TAG, "Queueing BLE command: " + payload);
            queueCommand(payload);
        } catch (Exception e) {
            Log.e(TAG, "Error creating command: " + e.getMessage());
        }
    }
}
