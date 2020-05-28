package com.example.finalapp;

import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.le.AdvertiseData;
import android.bluetooth.le.AdvertisingSet;
import android.bluetooth.le.AdvertisingSetCallback;
import android.bluetooth.le.AdvertisingSetParameters;
import android.bluetooth.le.BluetoothLeAdvertiser;
import android.content.Context;
import android.content.pm.PackageManager;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaPlayer;
import android.media.MediaRecorder;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;


import com.android.volley.RequestQueue;
import com.android.volley.toolbox.Volley;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;


public class MainActivity extends AppCompatActivity implements MediaPlayer.OnCompletionListener, SensorEventListener
{

    private static String DEVNAME = null;
    //xml init
    private TextView detect;
    private Button play;
    private TextView problem;
    private TextView time;
    private TextView x_acc_view;
    private TextView y_acc_view;
    private TextView z_acc_view;


    //Record settings
    private static final String AUDIO_RECORDER_FILE_EXT_WAV = ".wav";
    private static final String AUDIO_RECORDER_FOLDER = "AudioRecorder";
    private static final int RECORDER_SAMPLERATE = 44100;
    private static final int RECORDER_CHANNELS = AudioFormat.CHANNEL_IN_MONO;
    private static final int RECORDER_AUDIO_ENCODING = AudioFormat.ENCODING_PCM_16BIT;
    private static final String IP_ADDR = "192.168.1.149"; //HAY QUE MODIFICAR LA DIRECCION IP CADA VEZ QUE SE CONECTAN LOS DISPOSITIVOS A LA RED LOCAL!
    private static final int POST_PERIOD = 100; //in ms


    private AudioRecord recorder = null;
    private int bufferSize = 0;
    private boolean isRecording = false;
    private byte [] recordData;
    private int frequency1 = 19000;
    private int frequency2 = 20000;
    private FFT a;
    private int NumSensorCalls = 0;

    //file error statement
    final int REQUEST_PERMISSION_CODE = 1000;
    String extStore = Environment.getExternalStorageDirectory().getPath();

    //fft part
    byte[] music;
    short[] music2Short;
    int boucle = 0;

    //play/stop part
    MediaPlayer mediaPlayer19;
    MediaPlayer mediaPlayer20;

    boolean Play;
    private Thread managementThread;
    private Thread orientationThread;

    private SensorManager sensorManager;
    private Sensor linearAccelerometer;
    private Sensor gravity;
    private Sensor geomagnetic;

    private final float[] accelerometerReading = new float[3];
    private final float[] magnetometerReading = new float[3];

    private final float[] rotationMatrix = new float[9];
    private final float[] orientationAngles = new float[3];


    private RequestQueue MyRequestQueue;
    private Map<String,Object> dataMapToNodeRED;

    private Timer t;

    long time_start;
    long time_end;
    long timer = 0;

    long INIT_TIME;
    private int num_measurements;
    private boolean definedAccel = false;
    private boolean definedMagnet = false;

    @RequiresApi(api = Build.VERSION_CODES.O)
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (!checkPermissionFromDevice()) {
            RequestPermission();
        }

        dataMapToNodeRED = new LinkedHashMap<>();

        setBleAdvertising();

        detect = findViewById(R.id.detection);
        problem = findViewById(R.id.problem);
        play = findViewById(R.id.play);
        time = findViewById(R.id.time);
        x_acc_view = findViewById(R.id.x_acc_view);
        y_acc_view = findViewById(R.id.y_acc_view);
        z_acc_view = findViewById(R.id.z_acc_view);
        Play = false;

        problem.setText("problem");
        detect.setText("detect");
        time.setText("time");

        mediaPlayer19 = new MediaPlayer();
        mediaPlayer19 = MediaPlayer.create(MainActivity.this, R.raw.short19khz);

        mediaPlayer20 = new MediaPlayer();
        mediaPlayer20 = MediaPlayer.create(MainActivity.this, R.raw.short20khz);

        mediaPlayer19.setOnCompletionListener(this);
        mediaPlayer20.setOnCompletionListener(this);

        //Tamaño del buffer donde se almacenará lo que se graba
        bufferSize = AudioRecord.getMinBufferSize(RECORDER_SAMPLERATE, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);
        recordData = new byte [bufferSize];

        startRecording();

        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }


        recordManagementThread();
// ################# CODIGO NUEVO ##################################

        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        linearAccelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);
        gravity = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        geomagnetic = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);

        sensorManager.registerListener(this, linearAccelerometer, SensorManager.SENSOR_DELAY_GAME);
        sensorManager.registerListener(this, gravity, SensorManager.SENSOR_DELAY_GAME);
        sensorManager.registerListener(this, geomagnetic, SensorManager.SENSOR_DELAY_GAME);

        INIT_TIME = System.nanoTime();
        num_measurements = 0;

        MyRequestQueue = Volley.newRequestQueue(this);

        //accelerometerThread(); //HAY UN BUCLE INFINITO! while(true)
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
        }, 0,POST_PERIOD);
// ################# FIN CODIGO NUEVO ##################################

        play.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Toast.makeText(MainActivity.this, "Playing", Toast.LENGTH_SHORT).show();
                Play=true;
                problem.setText("SENT 19 KHZ SIGNAL");
                time_start=System.currentTimeMillis();
                play19();
            }
        });
    }

    //vars relating to BLE
    @RequiresApi(api = Build.VERSION_CODES.O)
    public void setBleAdvertising(){

        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        try {
            DEVNAME = getAdvertisingDeviceName();
        } catch (IOException e) {
            e.printStackTrace();
        }

        dataMapToNodeRED.put("devname", DEVNAME);

        bluetoothAdapter.setName(DEVNAME);
        BluetoothLeAdvertiser advertiser = bluetoothAdapter.getBluetoothLeAdvertiser();

        AdvertisingSetParameters parameters = (new AdvertisingSetParameters.Builder())
                .setLegacyMode(true) // True by default, but set here as a reminder.
                .setConnectable(false)
                .setInterval(AdvertisingSetParameters.INTERVAL_LOW)
                .setTxPowerLevel(AdvertisingSetParameters.TX_POWER_HIGH)
                .build();

        AdvertiseData data = (new AdvertiseData.Builder()).setIncludeDeviceName(true).setIncludeTxPowerLevel(true).build();

        AdvertisingSetCallback callback = new AdvertisingSetCallback() {
            @Override
            public void onAdvertisingSetStarted(AdvertisingSet advertisingSet, int txPower, int status) {
                Log.i("test", "onAdvertisingSetStarted(): txPower:" + txPower + " , status: "
                        + status);
                //currentAdvertisingSet = advertisingSet;
            }

            @Override
            public void onAdvertisingDataSet(AdvertisingSet advertisingSet, int status) {

            }

            @Override
            public void onScanResponseDataSet(AdvertisingSet advertisingSet, int status) {

            }

            @Override
            public void onAdvertisingSetStopped(AdvertisingSet advertisingSet) {

            }
        };

        advertiser.startAdvertisingSet(parameters, data, null, null, null, callback);

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

    public void sendDataToNodeRED() throws IOException {
        /*
        HttpsTrustManager.allowAllSSL();

        String url = "http://192.168.0.130:1880/query";
        StringRequest MyStringRequest = new StringRequest(Request.Method.POST, url, new Response.Listener<String>() {
            @Override
            public void onResponse(String response) {
                Log.d("RESPONSE: ", response);
            }
        }, new Response.ErrorListener() { //Create an error listener to handle errors appropriately.
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
            }
        }){
           protected Map<String, String> getParams(){
                Map<String, String> MyData = new HashMap<>();
                MyData.put("devname", DEVNAME); //Add the data you want to send to the server.
                MyData.put("isMoving", s);
                return MyData;
           }

        };
        MyStringRequest.setRetryPolicy(new DefaultRetryPolicy(
                5000,
                DefaultRetryPolicy.DEFAULT_MAX_RETRIES,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));
        MyRequestQueue.add(MyStringRequest);
       */  //HECHO CON VOLLEY

        String targetURL = "http://"+IP_ADDR+":1880/query";
        HttpURLConnection connection = null;

        try {
            StringBuilder postData = new StringBuilder();
            for (Map.Entry<String,Object> dataMapToNodeRED : dataMapToNodeRED.entrySet()) {
                if (postData.length() != 0) postData.append('&');
                postData.append(URLEncoder.encode(dataMapToNodeRED.getKey(), "UTF-8"));
                postData.append('=');
                postData.append(URLEncoder.encode(String.valueOf(dataMapToNodeRED.getValue()), "UTF-8"));
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


    private void orientationThread() {
        orientationThread = new Thread(new Runnable() {
            @Override
            public void run() {

            }
        });
//
    }

    private void recordManagementThread() {
        managementThread = new Thread(new Runnable() {
            @Override
            public void run() {
                while (true) {
                    startCalculating();
                }
            }
        }, "Calculating thread");

        managementThread.start();
    }

    private String getFilename() throws IOException {
        String filepath = Environment.getExternalStorageDirectory().getPath();
        File file = new File(filepath, AUDIO_RECORDER_FOLDER);

        if (!file.exists()) {
            file.createNewFile();
        }

        return (extStore + "/" + "AudioRead" + AUDIO_RECORDER_FILE_EXT_WAV);
    }


    private void handleEmitter (){

        while (Play) { //this device sent the 19 khz signal

            while (!detection20(frequency2, a)) {
                //ES LA RESPUESTA DEL RECEPTOR. HAY QUE MOSTRAR EL TIEMPO.
                setUpdatedFFT();
            }

            float val20kHz = a.getFreq(frequency2);
            Log.d(String.valueOf(Log.DEBUG), "20khz: "+ val20kHz);

            time_end = System.currentTimeMillis();
            timer = time_end - time_start;
            Play = false;
            problem.setText("");
            problem.setText("RECEIVED 20 KHZ SIGNAL");
            Log.d("tiempoTotal", Long.toString(timer));
            //            sendDataToNodeRED(String.valueOf(timer));
            time.setText("time: " + timer + "ms");

            while (detection19(frequency1, a)) {

                playAudio();
                a = new FFT(1024, RECORDER_SAMPLERATE);
                a.noAverages();
                int rec = 0;
                if (isRecording) {
                    rec = recorder.read(recordData, 0, bufferSize);
                }

                if (rec != -1) {
                    ByteBuffer.wrap(recordData).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().get(music2Short);
                    a.forward(Tofloat(music2Short));
                }
            }
        }

    }

    @SuppressLint({"WrongConstant", "SetTextI18n"})
    private void startCalculating() {

        setUpdatedFFT();

        while (!detection19(frequency1, a) && !Play) {
            //ES LA PREGUNTA DEL EMISOR. HAY QUE RESPONDERLE CON 20KHZ
           setUpdatedFFT();
        }

        if (Play){
            handleEmitter();
        }

        else {
            float val19kHz = a.getFreq(frequency1);
            Log.d(String.valueOf(Log.DEBUG), "19khz: "+ val19kHz);

            problem.setText("RECEIVED 19 KHZ SIGNAL");
            problem.setText("SENT 20 KHZ SIGNAL");
            play20();

            while (detection20(frequency2, a)) {

               setUpdatedFFT();
            }
        }


    }

    private boolean detection19(int frequency, FFT a) {

        int aff = Math.round(a.getFreq(frequency));
        if (aff >= 100000) {
            return true;
        } else {
            return false;
        }
    }

    private boolean detection20(int frequency, FFT a) {

        int aff = Math.round(a.getFreq(frequency));
        if (aff >= 70000) {
            return true;
        }
        else {
            return false;
        }
    }

    private void startRecording() {
        //Inicializa la grabadora
        recorder = new AudioRecord(MediaRecorder.AudioSource.MIC,
                RECORDER_SAMPLERATE, RECORDER_CHANNELS, RECORDER_AUDIO_ENCODING, bufferSize);

        if (recorder.getState() == AudioRecord.STATE_INITIALIZED) {
            //Comienza a grabar
            recorder.startRecording();
        }

        isRecording = true;

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

    //Re-computes the frequency spectrum of the recorded signal at this precise moment.
    private void setUpdatedFFT (){
        playAudio();
        a = new FFT(1024, RECORDER_SAMPLERATE);
        a.noAverages();
        int rec = 0;
        if (isRecording) {
            rec = recorder.read(recordData, 0, bufferSize);
        }

        if (rec != -1) {
            ByteBuffer.wrap(recordData).order(ByteOrder.LITTLE_ENDIAN).asShortBuffer().get(music2Short);
            a.forward(Tofloat(music2Short));
        }
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

    public void playAudio() {

        if ( (bufferSize/2) % 2 != 0 ) {
            /*If minSize divided by 2 is odd, then subtract 1 and make it even*/
            music2Short     = new short [((bufferSize /2) - 1)/2];
            music           = new byte  [(bufferSize/2) - 1];
        }
        else {
            /* Else it is even already */
            music2Short     = new short [bufferSize/2]; //pour motorola sinon /4
            music           = new byte  [bufferSize];  //pour motorola sinon /2
        }

    }

    public float[] Tofloat(short[] s){
        int len = s.length;
        float[] f= new float[len];
        for (int i=0;i<len;i++){
            f[i]=s[i];
        }
        return f;
    }

    public void play19() {
        //problem.setText("is sending a 20khz signal");
        if (mediaPlayer19 != null) {
            mediaPlayer19.start();
        }
        else{
            mediaPlayer19 = new MediaPlayer();
            mediaPlayer19 = MediaPlayer.create(MainActivity.this, R.raw.short19khz);
            mediaPlayer19.start();
        }
    }

    public void play20() {

        if (mediaPlayer20 != null) {
            mediaPlayer20.start();

        }
        else{
            mediaPlayer20 = new MediaPlayer();
            mediaPlayer20 = MediaPlayer.create(MainActivity.this, R.raw.short20khz);
            mediaPlayer20.start();
        }
    }

    @Override
    public void onCompletion(MediaPlayer mp) {
        if (mp == mediaPlayer19){ //Ha acabado la señal de 19 khz
            //mediaPlayer19.release();
            //mediaPlayer19 = null;
            //mediaPlayer19 = new MediaPlayer();
            //mediaPlayer19.setOnCompletionListener(this);
            //mediaPlayer19 = MediaPlayer.create(MainActivity.this, R.raw.short19khz);
        }
        else if (mp == mediaPlayer20){  //Ha acabado la señal de 22 khz
            //mediaPlayer20.release();
            //mediaPlayer20 = null;
            //mediaPlayer20 = new MediaPlayer();
            //mediaPlayer20.setOnCompletionListener(this);
            //mediaPlayer20 = MediaPlayer.create(MainActivity.this, R.raw.short20khz);
        }
    }

    // Compute the three orientation angles based on the most recent readings from
    // the device's accelerometer and magnetometer.

    public void updateOrientationAngles() {

        // Update rotation matrix, which is needed to update orientation angles.
        if (definedAccel && definedMagnet) {
            SensorManager.getRotationMatrix(rotationMatrix, null,
                    accelerometerReading, magnetometerReading);

            // "mRotationMatrix" now has up-to-date information.

            SensorManager.getOrientation(rotationMatrix, orientationAngles);

            dataMapToNodeRED.put("x_ori", orientationAngles[0]);
            dataMapToNodeRED.put("y_ori", orientationAngles[1]);
            dataMapToNodeRED.put("z_ori", orientationAngles[2]);

            Log.d("x_ori", String.valueOf((orientationAngles[0]*180.0)/Math.PI));
            Log.d("y_ori", String.valueOf((orientationAngles[1]*180.0)/Math.PI));
            Log.d("z_ori", String.valueOf((orientationAngles[2]*180.0)/Math.PI));
        }

        // "mOrientationAngles" now has up-to-date information.
    }

    @Override
    public void onSensorChanged(SensorEvent event) {

        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER){
            definedAccel = true;
            System.arraycopy(event.values, 0, accelerometerReading,
                    0, accelerometerReading.length);
            updateOrientationAngles();
        }
        else if (event.sensor.getType() == Sensor.TYPE_MAGNETIC_FIELD) {
            definedMagnet = true;
            System.arraycopy(event.values, 0, magnetometerReading,
                    0, magnetometerReading.length);
            updateOrientationAngles();
        }
        else if (event.sensor.getType() == Sensor.TYPE_LINEAR_ACCELERATION) {
           /* mGravity = event.values.clone();
            // Shake detection
            double x = mGravity[0];
            double y = mGravity[1];
            double z = mGravity[2];
            mAccelLast = mAccelCurrent;
            mAccelCurrent = Math.sqrt(x * x + y * y + z * z);
            double delta = mAccelCurrent - mAccelLast;
            mAccel = mAccel * 0.9f + delta;

            if (hitCount <= SAMPLE_SIZE) {
                hitCount++;
                hitSum += Math.abs(mAccel);
            } else {
                hitResult = hitSum / SAMPLE_SIZE;

                Log.d("hitResult", String.valueOf(hitResult));

                if (hitResult > THRESHOLD) {
                    Log.d("motion", "Walking");
                    isMoving = "true";
                } else {
                    Log.d("motion", "Stop Walking");
                    isMoving = "false";
                }

                hitCount = 0;
                hitSum = 0;
                hitResult = 0;
            }*/


           float x_acc = Float.parseFloat(String.valueOf(event.values[0]));
           float y_acc = Float.parseFloat(String.valueOf(event.values[1]));
           float z_acc = Float.parseFloat(String.valueOf(event.values[2]));

           ++NumSensorCalls;

           if (NumSensorCalls > 6){
               x_acc_view.setText(String.valueOf(x_acc));
               y_acc_view.setText(String.valueOf(y_acc));
               z_acc_view.setText(String.valueOf(z_acc));
               NumSensorCalls = 0;
           }

           Log.i("sensor trigger: ", "OK");
           dataMapToNodeRED.put("x_acc", x_acc);
           dataMapToNodeRED.put("y_acc", y_acc);
           dataMapToNodeRED.put("z_acc", z_acc);

           ++num_measurements;
            long num = System.nanoTime();
            if (num - INIT_TIME > 100000000) {
                Log.d("num measurements 1s: ", String.valueOf(num_measurements) );
                INIT_TIME = System.nanoTime();
                num_measurements = 0;
            }

        }

    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {

    }
}