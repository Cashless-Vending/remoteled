const HciSocket = require('hci-socket');
const NodeBleHost = require('ble-host');
const BleManager = NodeBleHost.BleManager;
const AdvertisingDataBuilder = NodeBleHost.AdvertisingDataBuilder;
const HciErrors = NodeBleHost.HciErrors;
const AttErrors = NodeBleHost.AttErrors;
const { v4: uuidv4 } = require('uuid');  // For generating random UUIDs
const { exec } = require('child_process');
const Gpio = require('onoff').Gpio;
const fs = require('fs');

//cat /sys/kernel/debug/gpio
const led = new Gpio(529, 'out');

var WEB_MESSAGE = "Setting up BLE..."
const QR_DATA_FILE = '/var/www/html/qr_data.json';

// Write QR data to file for web page to read
function updateQRData(message) {
    WEB_MESSAGE = message;
    const data = { message: message, timestamp: Date.now() };
    try {
        fs.writeFileSync(QR_DATA_FILE, JSON.stringify(data));
    } catch (err) {
        console.error('Error writing QR data file:', err);
    }
}

const deviceName = 'MyDevice';
var service = [];
var led_state = 'off';
const port = 5000;

var transport = new HciSocket(); // connects to the first hci device on the computer, for example hci0

var options = {
    // optional properties go here
};

// Function to generate deep link
function generateDeepLink(address, serviceUuid, charUuid, bleKey, deviceId) {
    const deepLink = deviceId
        ? `remoteled://connect/${address}/${serviceUuid}/${charUuid}/${bleKey}?deviceId=${deviceId}`
        : `remoteled://connect/${address}/${serviceUuid}/${charUuid}/${bleKey}`;
    updateQRData(deepLink);
    return deepLink;
}

function generate_16bit_uuid() {
    const hexString = Math.floor(Math.random() * 0x10000).toString(16).padStart(4, '0');
    return hexString;
}

function getBluetoothMacAddress() {
    return new Promise((resolve, reject) => {
        exec('hcitool dev', (error, stdout, stderr) => {
            if (error) {
                return reject(`Error executing command: ${error.message}`);
            }

            if (stderr) {
                return reject(`Error in execution: ${stderr}`);
            }

            // Extract MAC address using regular expression
            const macRegex = /hci0\s+([0-9A-F]{2}(:[0-9A-F]{2}){5})/i;
            const match = stdout.match(macRegex);

            if (match && match[1]) {
                resolve(match[1]); // Return MAC address as a string
            } else {
                reject('Bluetooth MAC Address not found');
            }
        });
    });
}

BleManager.create(transport, options, function(err, manager) {
    if (err) {
        console.error(err);
        return;
    }

    // Generate random UUIDs
    const bleShortServiceUuid = generate_16bit_uuid();
    const bleServiceUuid = `0000${bleShortServiceUuid}-0000-1000-8000-00805f9b34fb`;

    var notificationCharacteristic;

    manager.gattDb.setDeviceName(deviceName);
    
    const advDataBuffer = new AdvertisingDataBuilder()
        .addFlags(['leGeneralDiscoverableMode', 'brEdrNotSupported'])
        .addLocalName(/*isComplete*/ true, deviceName)
        .add128BitServiceUUIDs(/*isComplete*/ true, [bleServiceUuid])  // Use random service UUID
        .build();
    manager.setAdvertisingData(advDataBuffer);
    
    startAdv();

    function startAdv() {
        if(service.length>0)
        {
            manager.gattDb.removeService(service[0]);
        }
        
        const bleShortCharUuid = generate_16bit_uuid();
        const bleCharUuid = `0000${bleShortCharUuid}-0000-1000-8000-00805f9b34fb`;
        const bleKey = generate_16bit_uuid();
        service = [
            {
                uuid: bleServiceUuid,  // Use random service UUID
                characteristics: [
                    {
                        uuid: bleCharUuid,  // Use random characteristic UUID
                        properties: ['read', 'write'],
                        value: 'none', // could be a Buffer for a binary value
                        onWrite: function(connection, needsResponse, value, callback) {
                            console.log('A new value was written:', value);
                            const request = JSON.parse(value);
                            console.log(request);
                            if (request.bleKey === bleKey) {
                                console.log("BLE Key matches!");
                                // Check the command value to determine GPIO state
                                if (request.command === "ON") {
                                    led_state = 'on'
                                    led.writeSync(1); // Turn GPIO pin on (1)
                                    console.log("GPIO is ON");
                                } else if (request.command === "OFF") {
                                    led_state = 'off';
                                    led.writeSync(0); // Turn GPIO pin off (0)
                                    console.log("GPIO is OFF");
                                } else if (request.command === "CONNECT") {
                                    updateQRData("CONNECTED!");
                                    console.log("Varified Client Connected");
                                } else {
                                    console.log("Invalid command! Use 'ON' or 'OFF'");
                                }
                              } else {
                                console.log("BLE Key does not match.");
                              }
                            callback(AttErrors.SUCCESS); // actually only needs to be called when needsResponse is true
                        },
                        onRead: function(connection, callback) {
                            callback(AttErrors.SUCCESS, led_state);
                            console.log("CLIENT READ");
                        }
                    }
                ]
            }
        ]
        manager.gattDb.addServices(service);
    
        manager.startAdvertising({/*options*/}, connectCallback);
        getBluetoothMacAddress()
        .then(mac => {
            console.log(`Bluetooth MAC Address: ${mac}`);
            const bleAddress = mac;  // BLE address from connection
            const deepLink = generateDeepLink(bleAddress, bleShortServiceUuid, bleShortCharUuid, bleKey, process.env.DEVICE_ID);  // Generate deep link
            console.log('Generated Deep Link:', deepLink);
        })
        .catch(err => {
            console.error(err);
        });
    }

    function connectCallback(status, conn) {
        //console.log('Connection established!', conn);
        console.log('Connection established!');
        if (status != HciErrors.SUCCESS) {
            setTimeout(startAdv, 10000);  // Retry advertising after failure
            return;
        }

        conn.on('disconnect', startAdv); // Restart advertising after disconnect
    }
});
