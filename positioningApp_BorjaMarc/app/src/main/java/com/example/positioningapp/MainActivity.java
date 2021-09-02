package com.example.positioningapp;

import android.Manifest;
import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.le.AdvertiseData;
import android.bluetooth.le.AdvertisingSet;
import android.bluetooth.le.AdvertisingSetCallback;
import android.bluetooth.le.AdvertisingSetParameters;
import android.bluetooth.le.BluetoothLeAdvertiser;
import android.bluetooth.le.PeriodicAdvertisingParameters;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
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
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Random;


public class MainActivity extends AppCompatActivity
{


    private static String DEVNAME = null;
    private Button update;
    private EditText advInterval;

    //BLE vars
    BluetoothAdapter bluetoothAdapter;

    //Advertising
    private BluetoothLeAdvertiser advertiser;
    private AdvertisingSetParameters parameters;
    private PeriodicAdvertisingParameters periodic_parameters;
    private AdvertiseData data;
    private AdvertiseData periodic_data;
    private AdvertisingSetCallback callback;

    //file error statement
    final int REQUEST_PERMISSION_CODE = 1000;
    String extStore = Environment.getExternalStorageDirectory().getPath();

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

        update = findViewById(R.id.update);
        advInterval = findViewById(R.id.advInt_textNumber);

        initializeBluetoothConfig();
        setBLEAdvertising();

        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

    }

    private byte[] getCurrentTimestamp (){
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


    @SuppressLint("NewApi")
    private void initializeBluetoothConfig() {
        bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        // Check if all features are supported
        if (!bluetoothAdapter.isLe2MPhySupported()) {
            Log.e("error", "2M PHY not supported!");
            return;
        }
        if (!bluetoothAdapter.isLeExtendedAdvertisingSupported()) {
            Log.e("error", "LE Extended Advertising not supported!");
            return;
        }

        //Enables bluetooth if disabled
        if (!bluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            final int REQUEST_ENABLE_BT = 1;
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }
        try {
            DEVNAME = getAdvertisingDeviceName();
        } catch (IOException e) {
            e.printStackTrace();
        }

        boolean a = bluetoothAdapter.setName(DEVNAME);
        Log.d("ble adapter name set: ", String.valueOf(a));

    }

    //vars relating to BLE
    @RequiresApi(api = Build.VERSION_CODES.O)
    public void setBLEAdvertising(){

        advertiser = bluetoothAdapter.getBluetoothLeAdvertiser();


        parameters = (new AdvertisingSetParameters.Builder())
                .setLegacyMode(true) // No cambiar a false! Si no, deja de funcionar.
                .setScannable(true)
                .setConnectable(true)
                .setInterval(160) //Advertising interval ~ 100ms
                .setTxPowerLevel(AdvertisingSetParameters.TX_POWER_MAX)
                .build();

        /*periodic_parameters = (new PeriodicAdvertisingParameters.Builder())
                .setIncludeTxPower(true)
                .setInterval(80)
                .build();*/

        byte[] manufacturerData;
        QuuppaManufacturerData quuppa = new QuuppaManufacturerData();
        manufacturerData = quuppa.toBytes();

        //productionDate = getCurrentTimestamp();
        data = (new AdvertiseData.Builder())
                .setIncludeDeviceName(false)
                .setIncludeTxPowerLevel(false)
                .addManufacturerData(quuppa.getCompanyId(), manufacturerData)
                .build();

        callback = new AdvertisingSetCallback() {

            @Override
            //AdvertisingSet started
            public void onAdvertisingSetStarted(AdvertisingSet advertisingSet, int txPower, int status) {
                //Log.i("test", "onAdvertisingSetStarted(): txPower:" + txPower + " , status: "
                 //       + status);

                //byte[] timestamp = new byte[4];
                //timestamp = getCurrentTimestamp();

                //data = (new AdvertiseData.Builder()).setIncludeDeviceName(true).setIncludeTxPowerLevel(true).addManufacturerData(0x00C7, timestamp).build();
                //advertisingSet.setAdvertisingData(data);
            }

            @Override
            //advertising changed to enable or disable
            public void onAdvertisingEnabled(AdvertisingSet advertisingSet, boolean enable, int status) {
                //Log.i("test", "onAdvertisingEnabled(): enable:" + enable + " , status: "
                //        + status);
                /*if (!enable){
                    byte[] timestamp = new byte[4];
                    timestamp = getCurrentTimestamp();
                    data = (new AdvertiseData.Builder()).setIncludeDeviceName(true).setIncludeTxPowerLevel(true).addManufacturerData(0x00C7, timestamp).build();
                    advertisingSet.setAdvertisingData(data);
                }*/
            }

            @Override
            //Advertising data has been set
            public void onAdvertisingDataSet(AdvertisingSet advertisingSet, int status) {
                //Log.i("test", "onAdvertisingDataSet(): status:"
                //        + status);
                //advertisingSet.enableAdvertising(true,10,0);
            }


            @Override
            public void onAdvertisingSetStopped(AdvertisingSet advertisingSet) {
               // Log.i("test", "onAdvertisingSetStopped()");
            }
        };
        //periodic_data = (new AdvertiseData.Builder()).addManufacturerData(15, productionDate).build();
        //advertiser.startAdvertising(parameters, data, null, null, data, callback);
        advertiser.startAdvertisingSet(parameters, data, null, null, null, 0, 0, callback);

        update.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                int newAdvInt = Integer.parseInt(advInterval.getText().toString());
                advertiser.stopAdvertisingSet(callback);
                parameters = (new AdvertisingSetParameters.Builder())
                        .setLegacyMode(true) // No cambiar a false! Si no, deja de funcionar.
                        .setScannable(true)
                        .setConnectable(true)
                        .setInterval((int) (newAdvInt / 0.625)) //Advertising interval 160 = 100ms
                        .setTxPowerLevel(AdvertisingSetParameters.TX_POWER_MAX)
                        .build();
                advertiser.startAdvertisingSet(parameters, data, null, null, null, 0, 0, callback);
            }
        });
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
                String line = reader.readLine();
                return line;
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