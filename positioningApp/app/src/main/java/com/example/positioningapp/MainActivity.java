package com.example.positioningapp;

import android.Manifest;
import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.le.AdvertiseData;
import android.bluetooth.le.AdvertisingSet;
import android.bluetooth.le.AdvertisingSetCallback;
import android.bluetooth.le.AdvertisingSetParameters;
import android.bluetooth.le.BluetoothLeAdvertiser;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.util.Base64;
import android.util.Log;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

//import com.android.volley.RequestQueue;
//import com.android.volley.toolbox.Volley;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;


public class MainActivity extends AppCompatActivity
{

    private static String DEVNAME = null;
    private static String MAC_ADDR = null;

    //xml init
    private TextView detect;
    private Button play;
    private TextView problem;
    private TextView time;
    private TextView x_acc_view;
    private TextView y_acc_view;
    private TextView z_acc_view;

    //Node-RED vars
    private Thread noderedThread;
    private String IP_ADDR = "192.168.1.134";
    private Timer t;
    private static final long POST_INTERVAL = 1000; //ms

    //BLE vars
    BluetoothAdapter bluetoothAdapter;
    private Queue<Map<String, Object>> bleDetectedDevices;
    private int MANUFACTURER_ID = 15;

    //Advertising
    private Thread advertisingThread;
    private BluetoothLeAdvertiser advertiser;
    private AdvertisingSetParameters parameters;
    private AdvertiseData data;
    private AdvertisingSetCallback callback;

    //Scanning
    private Thread scanningThread;
    private BluetoothLeScanner scanner;
    private ScanCallback scanCallback;
    private ScanSettings scanSettings;

    //file vars
    final int REQUEST_PERMISSION_CODE = 1000;
    String extStore = Environment.getExternalStorageDirectory().getPath();

    //Audio Recording
    private Thread recorderThread;
    private AudioRecord recorder;
    private int bufferSize;
    private byte[] recordData;
    private static final int RECORDER_SAMPLERATE = 32000;
    private static final int RECORDER_CHANNELS = AudioFormat.CHANNEL_IN_MONO;
    private static final int RECORDER_AUDIO_ENCODING = AudioFormat.ENCODING_PCM_8BIT;
    public static Queue<Map<String, Object>> recordingData;
    private static final int RECORDING_INTERVAL = 5000; //ms
    private static final long RECORDING_DURATION = 250; //ms
    File audioFile;


    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode == RESULT_OK) {
            Log.d("Bluetooth: ", "Enabled succesfully!");
        }
    }

    @RequiresApi(api = Build.VERSION_CODES.O)
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (!checkPermissionFromDevice()) {
            RequestPermission();
        }

        bleDetectedDevices = new LinkedList<Map<String, Object>>();
        recordingData = new LinkedList<Map<String, Object>>();

        detect = findViewById(R.id.detection);
        problem = findViewById(R.id.problem);
        play = findViewById(R.id.play);
        time = findViewById(R.id.time);
        x_acc_view = findViewById(R.id.x_acc_view);
        y_acc_view = findViewById(R.id.y_acc_view);
        z_acc_view = findViewById(R.id.z_acc_view);

        problem.setText("problem");
        detect.setText("detect");
        time.setText("time");

        AudioRecorderThread();

        initializeBluetoothConfig();
        BLEAdvertisingThread();
        BLEScanningThread();
        nodeREDThread();

        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

    }

    private void AudioRecorderThread() {
        recorderThread = new Thread(new Runnable() {
            @Override
            public void run() {
                t = new Timer();
                t.schedule(new TimerTask() {
                    @RequiresApi(api = Build.VERSION_CODES.O)
                    @Override
                    public void run() {
                        initializeAudioRecorder();
                    }
                }, 0, RECORDING_INTERVAL);
            }
        }, "Media recording thread");
        recorderThread.start();
    }

    @RequiresApi(api = Build.VERSION_CODES.O)
    private void initializeAudioRecorder() {
        audioFile = new File(extStore, "audioRecorded");

        bufferSize = AudioRecord.getMinBufferSize(RECORDER_SAMPLERATE, RECORDER_CHANNELS, RECORDER_AUDIO_ENCODING);

        recorder = new AudioRecord.Builder()
                .setAudioSource(MediaRecorder.AudioSource.MIC)
                .setAudioFormat(new AudioFormat.Builder()
                        .setEncoding(RECORDER_AUDIO_ENCODING)
                        .setSampleRate(RECORDER_SAMPLERATE)
                        .setChannelMask(RECORDER_CHANNELS)
                        .build())
                .setBufferSizeInBytes(RECORDER_SAMPLERATE * 2)
                .build();

        startRecording();
    }

    private void startRecording() {

        if (recorder.getState() == AudioRecord.STATE_INITIALIZED) {
            recorder.startRecording();
            Log.i("info", "recording started!");

            boolean isRecording = true;
            long init_time = System.currentTimeMillis();
            while (isRecording){
                long curr_time = System.currentTimeMillis();
                if (curr_time - init_time > RECORDING_DURATION){
                    isRecording = false;
                }
                byte[] audioData = new byte[bufferSize];
                int read_bytes = recorder.read(audioData, 0, bufferSize);
                Log.i("test", "read bytes from audioData: "+read_bytes);
                writeAudioDataToFile(audioData, read_bytes);
                audioData = null;
            }
            stopRecording();
        }
        /*Timer timer = new Timer();
        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                stopRecording();
            }
        }, RECORDING_DURATION);*/
    }

    private void writeAudioDataToFile(byte[] audioData, int length) {
        FileOutputStream fos = null;
        try {
            fos = new FileOutputStream(audioFile, true);
            fos.write(audioData, 0, length);
            fos.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void stopRecording() {
        recorder.stop();
        recorder.release();
        recorder = null;

        encodeAudioDataFromFile();
    }

    private void encodeAudioDataFromFile() {
        //Encode audio data from file and store into recordingData

        int file_size = (int) audioFile.length();
        byte[] buff = new byte[file_size];

        FileInputStream fis = null;
        try {
            fis = new FileInputStream(audioFile);
            fis.read(buff,0,file_size);
        } catch (IOException e) {
            e.printStackTrace();
        }
        String b64 = Base64.encodeToString(buff, Base64.DEFAULT);

        //insert raw audio data in a queue to be sent to Node-RED later
        HashMap<String, Object> element = new HashMap<>();
        element.put("timestamp", System.currentTimeMillis());
        element.put("recorderDevice", DEVNAME);
        element.put("audioData", b64);
        recordingData.add(element);

        Log.d("test", "file size: "+String.valueOf(file_size));

        //Delete audio file
        boolean ret = audioFile.delete();
        Log.i("test", "audioFile deleted?: "+ret);
    }

    private void nodeREDThread() {
        noderedThread = new Thread(new Runnable() {
            @Override
            public void run() {
                t = new Timer();
                t.schedule(new TimerTask() {
                    @Override
                    public void run() {
                        try {
                            sendDataToNodeRED();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                }, 0, POST_INTERVAL);
            }
        }, "BLE advertising thread");
        noderedThread.start();
    }

    private byte[] getCurrentTimestampByteArray(){
        long unixTime = System.currentTimeMillis();

        byte[] productionDate = new byte[]{
                (byte) (unixTime >> 40),
                (byte) (unixTime >> 32),
                (byte) (unixTime >> 24),
                (byte) (unixTime >> 16),
                (byte) (unixTime >> 8),
                (byte) unixTime

        };
        return productionDate;
    }

    private long getCurrentTimestampLong (byte[] ts_b){
        if (ts_b == null){
            return -1;
        }
        else {
            return ((long) (ts_b[0] & 0xFF) << 40) |
                    ((long) (ts_b[1] & 0xFF) << 32) |
                    ((long) (ts_b[2] & 0xFF) << 24) |
                    ((long) (ts_b[3] & 0xFF) << 16) |
                    ((long) (ts_b[4] & 0xFF) << 8) |
                    ((long) (ts_b[5] & 0xFF));
        }
    }

    @SuppressLint("NewApi")
    private void initializeBluetoothConfig() {
        bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        //Enables bluetooth if disabled
        if (!bluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            final int REQUEST_ENABLE_BT = 1;
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }
        try {
            DEVNAME = getAdvertisingDeviceName();
            MAC_ADDR = getMacAddress();
        } catch (IOException e) {
            e.printStackTrace();
        }

        bluetoothAdapter.setName(DEVNAME);
    }

    private void BLEAdvertisingThread() {
        advertisingThread = new Thread(new Runnable() {
            @Override
            public void run() {
                setBLEAdvertising();
            }
        }, "BLE advertising thread");

        advertisingThread.start();
    }

    private void BLEScanningThread() {
        scanningThread = new Thread(new Runnable() {
            @Override
            public void run() {
                setBLEScanning();
            }
        }, "BLE scanning thread");

        scanningThread.start();
    }

    @SuppressLint("NewApi")
    private void setBLEAdvertising(){

        advertiser = bluetoothAdapter.getBluetoothLeAdvertiser();

        parameters = (new AdvertisingSetParameters.Builder())
                .setLegacyMode(true) // No cambiar a false! Si no, deja de funcionar.
                .setConnectable(false)
                .setInterval(160) //Advertising interval: 160 = 100ms
                .setTxPowerLevel(AdvertisingSetParameters.TX_POWER_MAX)
                .build();

       /* byte[] productionDate = new byte[4];

        productionDate = getCurrentTimestampByteArray();*/

        data = (new AdvertiseData.Builder()).setIncludeDeviceName(true).setIncludeTxPowerLevel(true).build();//addManufacturerData(MANUFACTURER_ID, productionDate).build();

        callback = new AdvertisingSetCallback() {

            @Override
            //AdvertisingSet started
            public void onAdvertisingSetStarted(AdvertisingSet advertisingSet, int txPower, int status) {
                Log.i("test", "onAdvertisingSetStarted(): txPower:" + txPower + " , status: "
                        + status);

               /* byte[] timestamp;
                timestamp = getCurrentTimestampByteArray();*/

                data = (new AdvertiseData.Builder()).setIncludeDeviceName(true).setIncludeTxPowerLevel(true).build();//addManufacturerData(MANUFACTURER_ID, timestamp).build();
                advertisingSet.setAdvertisingData(data);
            }

            @Override
            //advertising changed to enable or disable
            public void onAdvertisingEnabled(AdvertisingSet advertisingSet, boolean enable, int status) {
                Log.i("test", "onAdvertisingEnabled(): enable:" + enable + " , status: " + status);
                if (!enable){
                    /*byte[] timestamp;
                    timestamp = getCurrentTimestampByteArray();*/
                    data = (new AdvertiseData.Builder()).setIncludeDeviceName(true).setIncludeTxPowerLevel(true).build();//addManufacturerData(MANUFACTURER_ID, timestamp).build();
                    advertisingSet.setAdvertisingData(data);
                }
            }

            @Override
            //Advertising data has been set
            public void onAdvertisingDataSet(AdvertisingSet advertisingSet, int status) {
                Log.i("test", "onAdvertisingDataSet(): status:"
                        + status);
                advertisingSet.enableAdvertising(true,30,0);
            }


            @Override
            public void onAdvertisingSetStopped(AdvertisingSet advertisingSet) {
               Log.i("test", "onAdvertisingSetStopped()");
            }
        };
        advertiser.startAdvertisingSet(parameters, data, null, null, null, 30, 0, callback);

    }

    @SuppressLint("NewApi")
    private void setBLEScanning() {
        scanner = bluetoothAdapter.getBluetoothLeScanner();
        scanSettings = (new ScanSettings.Builder())
                .setCallbackType(ScanSettings.CALLBACK_TYPE_ALL_MATCHES)
                .setMatchMode(ScanSettings.MATCH_MODE_AGGRESSIVE)
                .setScanMode( ScanSettings.SCAN_MODE_LOW_LATENCY)
                .setNumOfMatches(ScanSettings.MATCH_NUM_ONE_ADVERTISEMENT)
                .build();
        scanCallback = new ScanCallback() {
            @SuppressLint("LongLogTag")
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                //super.onScanResult(callbackType, result);

                String advDevname = result.getDevice().getName();


                if (isValidBLEdevName(advDevname)/* && timeToUpdateValue(dstDevName, dstDevRSSI)*/){
                    //lo añadimos al Map para ser enviado posteriormente a NodeRED
                    int advDeviceRSSI = result.getRssi();
                    byte[] timestamp = result.getScanRecord().getManufacturerSpecificData(MANUFACTURER_ID);
                    long long_timestamp = getCurrentTimestampLong(timestamp);

                    //If packet contains a "timestamp" field in data, add it to detected devices.
                    if (long_timestamp != -1) {

                        HashMap<String, Object> packet = new HashMap<>();

                        packet.put("scanDevice", DEVNAME);
                        packet.put("timestamp", long_timestamp);
                        packet.put("advDevice", advDevname);
                        packet.put("advDeviceRSSI", advDeviceRSSI);

                        bleDetectedDevices.add(packet);
                    }

                   /* x_acc_view.setText(advDevname);
                    y_acc_view.setText(String.valueOf(advDeviceRSSI));
                    z_acc_view.setText("");*/
                    Log.d("Scanned results", "time: "+long_timestamp+ " Name: "+advDevname+" RSSI: "+advDeviceRSSI);
                }
            }

            @Override
            public void onBatchScanResults(List<ScanResult> results) {
                super.onBatchScanResults(results);
            }

            @Override
            public void onScanFailed(int errorCode) {
                super.onScanFailed(errorCode);
            }
        };

        scanner.startScan(null,  scanSettings, scanCallback);
        Log.d("startScan!", "OK!");
    }

    /** Checks if the scanned device is a valid one
     * 
     * @param srcDevName
     * @return whether the device is valid or not
     */
    private boolean isValidBLEdevName(String srcDevName) {
        if (srcDevName == null) return false;
        else return srcDevName.matches("TARGETDEV-\\w{6}"); //|| srcDevName.matches("ANC-\\w{4}");
    }

    /** Gets or generates a device name for advertising
     *
     * @return the device name.
     */
    @RequiresApi(api = Build.VERSION_CODES.KITKAT)
    private String getAdvertisingDeviceName() throws IOException {
        File file = new File(this.getFilesDir(), "devName");

        if (file.exists()){//if the file already exists, get the device name.

            FileInputStream fis = this.openFileInput("devName");
            InputStreamReader inputStreamReader =
                    new InputStreamReader(fis, StandardCharsets.UTF_8);
            StringBuilder stringBuilder = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(inputStreamReader)) {
                return reader.readLine();
            } catch (IOException e) {
                // Error occurred when opening raw file for reading.
            } finally {
                String contents = stringBuilder.toString();
            }
        }
        else { //if the file doesn't exist yet

            String PREFIX = "TARGETDEV-";

            String NUMBER = "0123456789";
            String CHAR_LOWER = "abcdefghijklmnopqrstuvwxyz";
            String DATA_FOR_RANDOM_STRING = CHAR_LOWER + NUMBER;

            StringBuilder sb = new StringBuilder(6);
            Random random = new Random(System.currentTimeMillis());

            for (int i = 0; i < 6; i++) {

                // 0-62 (exclusive), random returns 0-61
                int rndCharAt = random.nextInt(DATA_FOR_RANDOM_STRING.length());
                char rndChar = DATA_FOR_RANDOM_STRING.charAt(rndCharAt);

                // debug
                System.out.format("%d\t:\t%c%n", rndCharAt, rndChar);

                sb.append(rndChar);
            }
            Log.d("STRING: ", PREFIX + sb.toString());
            String filename = "devName";
            String fileContents = PREFIX + sb.toString();
            try (FileOutputStream fos = this.openFileOutput(filename, Context.MODE_PRIVATE)) {
                fos.write(fileContents.getBytes());
            }
        }
        return null;
    }

    public void sendDataToNodeRED() throws IOException {

        String targetURL = "http://" + IP_ADDR + ":1880/posts";
        HttpURLConnection connection = null;

        //if there are data to be sent to NodeRED
        while (!bleDetectedDevices.isEmpty()) {

            try {
                //Get the head element of the queue
                Map<String, Object> packet = bleDetectedDevices.poll();

                //Build the HTTP request parameters
                StringBuilder postData = new StringBuilder();
                for (Map.Entry<String, Object> dataPair : packet.entrySet()) {
                    if (postData.length() != 0) postData.append('&');
                    postData.append(URLEncoder.encode(dataPair.getKey(), "UTF-8"));
                    postData.append('=');
                    postData.append(URLEncoder.encode(String.valueOf(dataPair.getValue()), "UTF-8"));
                }

                String urlParameters = postData.toString();
                //Create connection
                URL url = new URL(targetURL);
                connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type",
                        "application/x-www-form-urlencoded");
                connection.setRequestProperty("Content-Length",
                        Integer.toString(urlParameters.getBytes().length));
                connection.setRequestProperty("Content-Language", "en-US");

                connection.setUseCaches(false);
                connection.setDoOutput(true);

                //Send request
                DataOutputStream wr = new DataOutputStream(
                        connection.getOutputStream());
                wr.writeBytes(urlParameters);
                wr.close();

                //Get Response
                InputStream is = connection.getInputStream();
                BufferedReader rd = new BufferedReader(new InputStreamReader(is));
                StringBuilder response = new StringBuilder(); // or StringBuffer if Java version 5+
                String line;
                while ((line = rd.readLine()) != null) {
                    response.append(line);
                    response.append('\r');
                }
                rd.close();
                // return response.toString();

            } catch (Exception e) {
                e.printStackTrace();
                // return null;
            } finally {
                if (connection != null) {
                    connection.disconnect();
                }
            }
        }

        while (!recordingData.isEmpty()){
            Map<String, Object> audioClip = recordingData.poll();

            //Build the HTTP request parameters
            StringBuilder postData = new StringBuilder();
            for (Map.Entry<String, Object> dataPair : audioClip.entrySet()) {
                if (postData.length() != 0) postData.append('&');
                postData.append(URLEncoder.encode(dataPair.getKey(), "UTF-8"));
                postData.append('=');
                postData.append(URLEncoder.encode(String.valueOf(dataPair.getValue()), "UTF-8"));
            }

            String urlParameters = postData.toString();
            //Create connection
            URL url = new URL(targetURL);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type",
                    "application/x-www-form-urlencoded");
            connection.setRequestProperty("Content-Length",
                    Integer.toString(urlParameters.getBytes().length));
            connection.setRequestProperty("Content-Language", "en-US");

            connection.setUseCaches(false);
            connection.setDoOutput(true);

            //Send request
            DataOutputStream wr = new DataOutputStream(
                    connection.getOutputStream());
            wr.writeBytes(urlParameters);
            wr.close();

            //Get Response
            InputStream is = connection.getInputStream();
            BufferedReader rd = new BufferedReader(new InputStreamReader(is));
            StringBuilder response = new StringBuilder(); // or StringBuffer if Java version 5+
            String line;
            while ((line = rd.readLine()) != null) {
                response.append(line);
                response.append('\r');
            }
            rd.close();
            // return response.toString();
        }
    }

    public String getMacAddress(){
        try{
            List<NetworkInterface> networkInterfaceList = Collections.list(NetworkInterface.getNetworkInterfaces());
            String stringMac = "";
            for(NetworkInterface networkInterface : networkInterfaceList)
            {
                if(networkInterface.getName().equalsIgnoreCase("wlan0"));
                {
                    for(int i = 0 ;i <networkInterface.getHardwareAddress().length; i++){
                        String stringMacByte = Integer.toHexString(networkInterface.getHardwareAddress()[i]& 0xFF);
                        if(stringMacByte.length() == 1)
                        {
                            stringMacByte = "0" + stringMacByte;
                        }
                        stringMac = stringMac + stringMacByte.toUpperCase() + ":";
                    }
                    break;
                }
            }
            return stringMac;
        }catch (SocketException e)
        {
            e.printStackTrace();
        }
        return  "0";
    }


    private boolean checkPermissionFromDevice() {
        int result_from_storage_permission = ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE);
        int record_audio_result = ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO);
        int ble_result = ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH);
        int ble_admin_result = ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_ADMIN);
        int acces_fine_loc_result = ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION);
        int internet_permission = ContextCompat.checkSelfPermission(this, Manifest.permission.INTERNET);
        return  (result_from_storage_permission == PackageManager.PERMISSION_GRANTED) &&
                (record_audio_result == PackageManager.PERMISSION_GRANTED) &&
                (ble_result == PackageManager.PERMISSION_GRANTED) &&
                (ble_admin_result == PackageManager.PERMISSION_GRANTED) &&
                (acces_fine_loc_result == PackageManager.PERMISSION_GRANTED) &&
                (internet_permission == PackageManager.PERMISSION_GRANTED);
    }

    private void RequestPermission(){
        ActivityCompat.requestPermissions(this, new String[]{
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
                Manifest.permission.BLUETOOTH,
                Manifest.permission.BLUETOOTH_ADMIN,
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.INTERNET
        }, REQUEST_PERMISSION_CODE);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        switch (requestCode)
        {
            case REQUEST_PERMISSION_CODE:{
                if(grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED){
                    Toast.makeText(MainActivity.this, "Permission granted", Toast.LENGTH_SHORT).show();
                }
                else{
                    Toast.makeText(MainActivity.this, "Permission denied", Toast.LENGTH_SHORT).show();
                }
            }
            break;
        }

    }
}