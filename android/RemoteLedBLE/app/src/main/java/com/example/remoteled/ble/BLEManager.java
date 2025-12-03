package com.example.remoteled.ble;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothProfile;
import android.content.Context;
import android.util.Log;

import org.json.JSONObject;

/**
 * BLE Manager for communicating with Pi
 * Handles LED control commands via BLE
 */
public class BLEManager {
    private static final String TAG = "BLEManager";

    private Context context;
    private String macAddress;
    private String serviceUUID;
    private String characteristicUUID;
    private String bleKey;

    private BluetoothGatt bluetoothGatt;
    private BluetoothGattCharacteristic ledCharacteristic;
    private boolean isConnected = false;

    public interface ConnectionCallback {
        void onConnected();
        void onDisconnected();
        void onError(String error);
    }

    public BLEManager(Context context, String macAddress, String serviceUUID,
                      String characteristicUUID, String bleKey) {
        this.context = context;
        this.macAddress = macAddress;
        this.serviceUUID = serviceUUID;
        this.characteristicUUID = characteristicUUID;
        this.bleKey = bleKey;
    }

    public void connect(ConnectionCallback callback) {
        BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        if (adapter == null) {
            callback.onError("Bluetooth not supported");
            return;
        }

        BluetoothDevice device = adapter.getRemoteDevice(macAddress);
        if (device == null) {
            callback.onError("Device not found");
            return;
        }

        Log.d(TAG, "Connecting to Pi at " + macAddress);

        bluetoothGatt = device.connectGatt(context, false, new BluetoothGattCallback() {
            @Override
            public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
                if (newState == BluetoothProfile.STATE_CONNECTED) {
                    Log.d(TAG, "Connected to Pi, discovering services...");
                    isConnected = true;
                    gatt.discoverServices();
                } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                    Log.d(TAG, "Disconnected from Pi");
                    isConnected = false;
                    callback.onDisconnected();
                }
            }

            @Override
            public void onServicesDiscovered(BluetoothGatt gatt, int status) {
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    ledCharacteristic = gatt.getService(java.util.UUID.fromString(serviceUUID))
                            .getCharacteristic(java.util.UUID.fromString(characteristicUUID));
                    if (ledCharacteristic != null) {
                        Log.d(TAG, "LED characteristic found");
                        callback.onConnected();
                    } else {
                        Log.e(TAG, "LED characteristic not found");
                        callback.onError("LED characteristic not found");
                    }
                }
            }
        });
    }

    public void disconnect() {
        if (bluetoothGatt != null) {
            bluetoothGatt.disconnect();
            bluetoothGatt.close();
            bluetoothGatt = null;
        }
        isConnected = false;
    }

    public boolean isConnected() {
        return isConnected;
    }

    /**
     * Send LED blink command
     */
    public void sendBlinkCommand(String color) {
        sendCommand("BLINK", color, 100, 0.5);
    }

    /**
     * Send LED solid ON command
     */
    public void sendOnCommand(String color) {
        sendCommand("ON", color, 0, 0);
    }

    /**
     * Send LED OFF command
     */
    public void sendOffCommand() {
        sendCommand("OFF", "red", 0, 0);
    }

    private void sendCommand(String command, String color, int times, double interval) {
        if (!isConnected || ledCharacteristic == null) {
            Log.w(TAG, "Not connected, cannot send command");
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

            String payload = json.toString();
            Log.d(TAG, "Sending BLE command: " + payload);

            ledCharacteristic.setValue(payload.getBytes());
            bluetoothGatt.writeCharacteristic(ledCharacteristic);
        } catch (Exception e) {
            Log.e(TAG, "Error sending command: " + e.getMessage());
        }
    }
}
