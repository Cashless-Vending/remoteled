package com.example.remoteled;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import java.util.Arrays;
import android.Manifest;
import androidx.annotation.NonNull;




import androidx.appcompat.app.AppCompatActivity;

import android.util.Log;
import android.view.View;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.remoteled.databinding.ActivityMainBinding;
import com.google.android.material.floatingactionbutton.FloatingActionButton;

import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import java.nio.charset.StandardCharsets;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {

    private ActivityMainBinding binding;
    private static final String TAG = "RemoteLED";
    private static final int REQUEST_ENABLE_BT = 1;
    private static final int PERMISSION_REQUEST_CODE = 100;

    private BluetoothAdapter bluetoothAdapter;
    private BluetoothGatt bluetoothGatt;
    private BluetoothGattCharacteristic characteristic;

    private TextView connectionStatus; // TextView to show connection status
    FrameLayout toggleBox;
    ImageView toggleImage;
    private boolean isON = false;
    String bleKey;
    String scannedDeviceId; // optional from QR deep link
    FloatingActionButton disconnectButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        connectionStatus = findViewById(R.id.connectionStatus);
        toggleBox = findViewById(R.id.toggleBox);
        toggleImage = findViewById(R.id.toggleImage);
        disconnectButton = findViewById(R.id.disconnect);

        // TEMPORARY: Check if it's an HTTP/HTTPS URL first, skip BLE setup
        Intent intent = getIntent();
        if (intent != null && intent.getAction() != null && intent.getAction().equals(Intent.ACTION_VIEW)) {
            Uri data = intent.getData();
            if (data != null && ("https".equals(data.getScheme()) || "http".equals(data.getScheme()))) {
                // It's an HTTP/HTTPS URL - bypass BLE and open in browser directly
                Log.d(TAG, "BYPASS: HTTP/HTTPS URL detected, opening browser without BLE");
                Toast.makeText(this, "Opening detail page...", Toast.LENGTH_SHORT).show();
                Intent browserIntent = new Intent(Intent.ACTION_VIEW, data);
                startActivity(browserIntent);
                finish();
                return; // Exit early, don't request BLE permissions
            }
        }

        checkAndRequestPermissions();

        toggleBox.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isON) {
                    // Change to night mode
                    toggleBox.setBackgroundColor(ContextCompat.getColor(MainActivity.this, R.color.nightBackground));
                    toggleImage.setImageResource(R.drawable.moon_image);
                    switchOff();
                } else {
                    // Change to day mode
                    toggleBox.setBackgroundColor(ContextCompat.getColor(MainActivity.this, R.color.darkBackground));
                    toggleImage.setImageResource(R.drawable.sun_image);
                    switchOn();
                }
                isON = !isON; // Toggle the mode
            }
        });
        disconnectButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (ActivityCompat.checkSelfPermission(MainActivity.this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                    // TODO: Consider calling
                    //    ActivityCompat#requestPermissions
                    // here to request the missing permissions, and then overriding
                    //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                    //                                          int[] grantResults)
                    // to handle the case where the user grants the permission. See the documentation
                    // for ActivityCompat#requestPermissions for more details.
                    return;
                }
                bluetoothGatt.disconnect();
            }
        });
    }

    private void checkAndRequestPermissions() {
        // List of permissions required for Bluetooth operations
        String[] permissions;

        // Different permissions are required based on Android version
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            // Android 12+ requires BLUETOOTH_SCAN and BLUETOOTH_CONNECT
            permissions = new String[]{
                    Manifest.permission.BLUETOOTH_SCAN,
                    Manifest.permission.BLUETOOTH_CONNECT,
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
            };
        } else {
            // Older versions only need classic Bluetooth and location permissions
            permissions = new String[]{
                    Manifest.permission.BLUETOOTH,
                    Manifest.permission.BLUETOOTH_ADMIN,
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
            };
        }

        // Check if permissions are already granted
        if (!hasPermissions(permissions)) {
            // Request the missing permissions
            ActivityCompat.requestPermissions(this, permissions, PERMISSION_REQUEST_CODE);
        } else {
            // Permissions are already granted, proceed with your Bluetooth operations
            Log.d(TAG, "Permissions already granted.");
            initializeBluetooth();
        }
    }

    private void initializeBluetooth() {
        BluetoothManager bluetoothManager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
        bluetoothAdapter = bluetoothManager.getAdapter();
        if (!bluetoothAdapter.isEnabled()) {
            // Bluetooth is not enabled, prompt the user to turn it on
            Log.d(TAG, "Bluetooth is off, requesting to turn it on...");
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                // TODO: Consider calling
                //    ActivityCompat#requestPermissions
                // here to request the missing permissions, and then overriding
                //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                //                                          int[] grantResults)
                // to handle the case where the user grants the permission. See the documentation
                // for ActivityCompat#requestPermissions for more details.
                return;
            }
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }else{
            initializeGattConnection();
        }
    }

    private boolean hasPermissions(String[] permissions) {
        for (String permission : permissions) {
            if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }
        return true;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean allGranted = true;

            // Check if all permissions are granted
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }

            if (allGranted) {
                // All permissions are granted, initialize Bluetooth operations
                Log.d(TAG, "All permissions granted.");
                initializeBluetooth();
            } else {
                // Some permissions are denied
                Log.e(TAG, "Some permissions are denied. Bluetooth functionality may not work.");
            }
        }
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_ENABLE_BT) {
            if (resultCode == RESULT_OK) {
                // Bluetooth is now enabled, initialize GATT connection
                Log.d(TAG, "Bluetooth enabled successfully, initializing GATT connection...");
                initializeGattConnection();
            } else {
                // User denied the request to enable Bluetooth
                Log.e(TAG, "Bluetooth enabling failed or user denied the request.");
            }
        }
    }
    private void initializeGattConnection() {
        // Check if the app was opened via a deep link
        Intent intent = getIntent();
        if (intent != null && intent.getAction() != null && intent.getAction().equals(Intent.ACTION_VIEW)) {
            Uri data = intent.getData();
            if (data != null) {
                String scheme = data.getScheme();
                String macAddress = null;
                String serviceUUID = null;
                String characteristicUUID = null;

                // Handle HTTPS URLs: https://your-api.com/detail?machineId=XXX&mac=YYY&service=7514&char=DE40&key=9F64
                if ("https".equals(scheme) || "http".equals(scheme)) {
                    Log.d(TAG, "Processing HTTPS deep link: " + data.toString());

                    // Parse query parameters
                    macAddress = data.getQueryParameter("mac");
                    String shortServiceUUID = data.getQueryParameter("service");
                    String shortCharUUID = data.getQueryParameter("char");
                    bleKey = data.getQueryParameter("key");
                    String machineId = data.getQueryParameter("machineId");

                    // Convert short UUIDs to full format
                    if (shortServiceUUID != null) {
                        serviceUUID = "0000" + shortServiceUUID + "-0000-1000-8000-00805f9b34fb";
                    }
                    if (shortCharUUID != null) {
                        characteristicUUID = "0000" + shortCharUUID + "-0000-1000-8000-00805f9b34fb";
                    }

                    // Store machineId if provided
                    if (machineId != null && !machineId.isEmpty()) {
                        scannedDeviceId = machineId;
                    }

                    Log.d(TAG, "Parsed HTTPS URL - MAC: " + macAddress + ", Service: " + serviceUUID + ", Char: " + characteristicUUID + ", Key: " + bleKey);
                }
                // Handle legacy remoteled:// URLs: remoteled://connect/{mac}/{service}/{char}/{key}
                else if ("remoteled".equals(scheme)) {
                    Log.d(TAG, "Processing remoteled:// deep link: " + data.toString());

                    macAddress = data.getPathSegments().get(0);
                    serviceUUID = "0000" + data.getPathSegments().get(1) + "-0000-1000-8000-00805f9b34fb";
                    characteristicUUID = "0000" + data.getPathSegments().get(2) + "-0000-1000-8000-00805f9b34fb";
                    bleKey = data.getPathSegments().get(3);

                    // Optional deviceId query parameter from QR
                    String qpDeviceId = data.getQueryParameter("deviceId");
                    if (qpDeviceId != null && !qpDeviceId.isEmpty()) {
                        scannedDeviceId = qpDeviceId;
                    }

                    Log.d(TAG, "Parsed remoteled URL - MAC: " + macAddress + ", Service: " + serviceUUID + ", Char: " + characteristicUUID + ", Key: " + bleKey);
                }

                // TEMPORARY: Bypass BLE connection, just open the URL in browser
                // TODO: Re-enable BLE connection after testing API endpoint
                if ("https".equals(scheme) || "http".equals(scheme)) {
                    Log.d(TAG, "BYPASS MODE: Opening URL in browser instead of BLE connection");
                    Toast.makeText(this, "Opening detail page...", Toast.LENGTH_SHORT).show();

                    // Open the URL in browser
                    Intent browserIntent = new Intent(Intent.ACTION_VIEW, data);
                    startActivity(browserIntent);
                    finish(); // Close MainActivity
                } else {
                    // For remoteled:// scheme, still try BLE connection
                    if (macAddress != null && serviceUUID != null && characteristicUUID != null && bleKey != null) {
                        connectToDevice(macAddress, UUID.fromString(serviceUUID), UUID.fromString(characteristicUUID));
                    } else {
                        Log.e(TAG, "Missing required BLE parameters from deep link");
                        Toast.makeText(this, "Invalid QR code format", Toast.LENGTH_SHORT).show();
                    }
                }
            }
        }
    }

    private void connectToDevice(String macAddress, UUID serviceUUID, UUID characteristicUUID) {
        BluetoothDevice device = bluetoothAdapter.getRemoteDevice(macAddress);
        if (device == null) {
            Log.e(TAG, "Device not found. Unable to connect.");
            Toast.makeText(this,"Device Not Found!",Toast.LENGTH_SHORT).show();
            updateConnectionStatus("Device not found");
            return;
        }

        updateConnectionStatus("Connecting to device...");

        if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.
            return;
        }
        bluetoothGatt = device.connectGatt(this, false, new BluetoothGattCallback() {
            @Override
            public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
                Log.d(TAG,"BLE State Changed"+newState);
                if (newState == BluetoothGatt.STATE_CONNECTED) {
                    Log.i(TAG, "Connected to GATT server.");
                    updateConnectionStatus("Connected to device");
                    if (ActivityCompat.checkSelfPermission(MainActivity.this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                        // TODO: Consider calling
                        //    ActivityCompat#requestPermissions
                        // here to request the missing permissions, and then overriding
                        //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                        //                                          int[] grantResults)
                        // to handle the case where the user grants the permission. See the documentation
                        // for ActivityCompat#requestPermissions for more details.
                        return;
                    }
                    bluetoothGatt.discoverServices();
                } else if (newState == BluetoothGatt.STATE_DISCONNECTED) {
                    Log.i(TAG, "Disconnected from GATT server.");
                    updateConnectionStatus("Disconnected from device");
                    bluetoothGatt.close();
                    MainActivity.this.finishAndRemoveTask();
                }
            }

            @Override
            public void onServicesDiscovered(BluetoothGatt gatt, int status) {
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    BluetoothGattService service = bluetoothGatt.getService(serviceUUID);
                    if (service != null) {
                        characteristic = service.getCharacteristic(characteristicUUID);
                        Log.i(TAG, "Characteristic found.");
                        updateConnectionStatus("Characteristic found");
                        enableControlButtons(true); // handshake complete
                        // If we came from QR and have a deviceId, navigate into app flow
                        if (scannedDeviceId != null && !scannedDeviceId.isEmpty()) {
                            runOnUiThread(() -> {
                                Intent i = new Intent(MainActivity.this, ProductSelectionActivity.class);
                                i.putExtra("DEVICE_ID", scannedDeviceId);
                                startActivity(i);
                                finish();
                            });
                        }
                        if (ActivityCompat.checkSelfPermission(MainActivity.this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                            // TODO: Consider calling
                            //    ActivityCompat#requestPermissions
                            // here to request the missing permissions, and then overriding
                            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                            //                                          int[] grantResults)
                            // to handle the case where the user grants the permission. See the documentation
                            // for ActivityCompat#requestPermissions for more details.
                            return;
                        }
                        bluetoothGatt.readCharacteristic(characteristic);
                    } else {
                        updateConnectionStatus("Service not found");
                    }
                }
            }

            @Override
            public void onCharacteristicRead(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
                Log.e(TAG,"CHAR READ");
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    byte[] data = characteristic.getValue();
                    String led_state = new String(data, StandardCharsets.UTF_8);
                    Log.d(TAG,led_state);
                    if(led_state.equals("on"))
                    {
                        isON = true;
                        toggleBox.setBackgroundColor(ContextCompat.getColor(MainActivity.this, R.color.darkBackground));
                        toggleImage.setImageResource(R.drawable.sun_image);
                    }else if(led_state.equals("off")){
                        isON=false;
                        toggleBox.setBackgroundColor(ContextCompat.getColor(MainActivity.this, R.color.nightBackground));
                        toggleImage.setImageResource(R.drawable.moon_image);
                    }
                    connect_ack();
                    Log.i(TAG, "Characteristic read successfully: " + Arrays.toString(data));
                }
            }
        });
    }

    private void sendCommand(String command) {
        if (characteristic != null) {
            String jsonPayload = "{\"command\": \"" + command + "\",\"bleKey\":\""+bleKey+"\"}";
            byte[] data = jsonPayload.getBytes(StandardCharsets.UTF_8);
            characteristic.setValue(data);
            if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                // TODO: Consider calling
                //    ActivityCompat#requestPermissions
                // here to request the missing permissions, and then overriding
                //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                //                                          int[] grantResults)
                // to handle the case where the user grants the permission. See the documentation
                // for ActivityCompat#requestPermissions for more details.
                return;
            }
            boolean success = bluetoothGatt.writeCharacteristic(characteristic);

            if (success) {
                Log.i(TAG, "Command sent: " + command);
            } else {
                Log.e(TAG, "Failed to send command.");
            }
        } else {
            Log.e(TAG, "Characteristic is not initialized.");
        }
    }

    public void switchOn() {
        sendCommand("ON");
    }

    public void switchOff() {
        sendCommand("OFF");
    }

    public void connect_ack() { sendCommand("CONNECT"); }

    private void updateConnectionStatus(String status) {
        runOnUiThread(() -> connectionStatus.setText("Status: " + status));
    }

    private void enableControlButtons(boolean enable) {
        runOnUiThread(() -> {
            toggleBox.setVisibility(View.VISIBLE);
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (bluetoothGatt != null) {
            if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                // TODO: Consider calling
                //    ActivityCompat#requestPermissions
                // here to request the missing permissions, and then overriding
                //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                //                                          int[] grantResults)
                // to handle the case where the user grants the permission. See the documentation
                // for ActivityCompat#requestPermissions for more details.
                return;
            }
            bluetoothGatt.close();
            bluetoothGatt = null;
        }
    }
}