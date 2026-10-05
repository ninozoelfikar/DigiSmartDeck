package com.digikeyboard.remote;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.os.Build;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.view.inputmethod.InputMethodManager;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.Toast;
import android.content.Intent;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.media.AudioManager;
import android.os.Handler;
import android.os.Looper;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "DigiKeyboardPrefs";
    private static final String KEY_SERVER_URL = "server_url";
    private static final String DEFAULT_URL = "http://192.168.1.100:8080";
    private static final int REQUEST_CODE_PERMISSIONS = 2001;

    private WebView webView;
    private ImageButton btnServerSettings;
    private SharedPreferences prefs;
    private BluetoothHidHelper bluetoothHidHelper;
    private PermissionRequest pendingPermissionRequest;
    private SpeechRecognizer speechRecognizer;
    private Intent speechRecognizerIntent;
    private AudioManager audioManager;
    private Handler speechHandler = new Handler(Looper.getMainLooper());
    private boolean isAlwaysOnSpeech = true;
    private boolean isListeningActive = false;
    private boolean isMutedByBridge = false;
    private String currentSpeechLang = "id-ID";

    public class WebAppInterface {
        @android.webkit.JavascriptInterface
        public boolean isBluetoothAvailable() {
            return bluetoothHidHelper != null && bluetoothHidHelper.isSupported();
        }

        @android.webkit.JavascriptInterface
        public boolean hasAudioPermission() {
            return ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED;
        }

        @android.webkit.JavascriptInterface
        public boolean isNativeSpeechAvailable() {
            return SpeechRecognizer.isRecognitionAvailable(MainActivity.this);
        }

        @android.webkit.JavascriptInterface
        public void setAlwaysOnSpeech(boolean enable) {
            isAlwaysOnSpeech = enable;
        }

        @android.webkit.JavascriptInterface
        public boolean isAlwaysOnSpeech() {
            return isAlwaysOnSpeech;
        }

        @android.webkit.JavascriptInterface
        public void startNativeSpeech(String lang) {
            startNativeSpeechWithOptions(lang, isAlwaysOnSpeech);
        }

        @android.webkit.JavascriptInterface
        public void startNativeSpeechWithOptions(String lang, boolean alwaysOn) {
            runOnUiThread(() -> {
                if (ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                    ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.RECORD_AUDIO}, REQUEST_CODE_PERMISSIONS);
                    return;
                }
                isAlwaysOnSpeech = alwaysOn;
                isListeningActive = true;
                currentSpeechLang = (lang != null && !lang.isEmpty()) ? lang : "id-ID";

                muteChime();
                if (speechRecognizer == null) {
                    initSpeechRecognizer();
                }
                if (speechRecognizer != null) {
                    speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, currentSpeechLang);
                    try {
                        speechRecognizer.startListening(speechRecognizerIntent);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
        }

        @android.webkit.JavascriptInterface
        public void stopNativeSpeech() {
            runOnUiThread(() -> {
                isListeningActive = false;
                if (speechHandler != null) {
                    speechHandler.removeCallbacksAndMessages(null);
                }
                if (speechRecognizer != null) {
                    try {
                        speechRecognizer.stopListening();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
                unmuteChimeDelayed(150);
            });
        }

        @android.webkit.JavascriptInterface
        public void cancelNativeSpeech() {
            runOnUiThread(() -> {
                isListeningActive = false;
                if (speechHandler != null) {
                    speechHandler.removeCallbacksAndMessages(null);
                }
                if (speechRecognizer != null) {
                    try {
                        speechRecognizer.cancel();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
                unmuteChimeDelayed(150);
            });
        }

        @android.webkit.JavascriptInterface
        public void requestAudioPermission() {
            runOnUiThread(() -> {
                if (ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                    ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.RECORD_AUDIO}, REQUEST_CODE_PERMISSIONS);
                }
            });
        }

        @android.webkit.JavascriptInterface
        public void enableBluetoothHid() {
            runOnUiThread(() -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    if (ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                        ActivityCompat.requestPermissions(MainActivity.this, new String[]{
                            Manifest.permission.BLUETOOTH_CONNECT,
                            Manifest.permission.BLUETOOTH_SCAN,
                            Manifest.permission.BLUETOOTH_ADVERTISE
                        }, REQUEST_CODE_PERMISSIONS);
                        return;
                    }
                }
                if (bluetoothHidHelper != null) bluetoothHidHelper.register();
            });
        }

        @android.webkit.JavascriptInterface
        public void sendBluetoothKey(String key, boolean shift, boolean ctrl, boolean alt, boolean cmd) {
            if (bluetoothHidHelper != null) {
                bluetoothHidHelper.sendKey(key, shift, ctrl, alt, cmd);
            }
        }

        @android.webkit.JavascriptInterface
        public void sendBluetoothMouseMove(int dx, int dy, int button) {
            if (bluetoothHidHelper != null) {
                bluetoothHidHelper.sendMouseMove(dx, dy, button);
            }
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 1. Kunci layar ke Landscape (Mendatar) & jaga layar tetap menyala
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        setContentView(R.layout.activity_main);

        prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        webView = findViewById(R.id.webView);
        btnServerSettings = findViewById(R.id.btnServerSettings);

        // Inisialisasi Bluetooth HID Helper
        bluetoothHidHelper = new BluetoothHidHelper(this);
        bluetoothHidHelper.setStatusListener((status, isConnected) -> runOnUiThread(() -> {
            Toast.makeText(MainActivity.this, status, Toast.LENGTH_SHORT).show();
            if (webView != null) {
                webView.evaluateJavascript("if (window.onBluetoothStatus) window.onBluetoothStatus('" + status + "', " + isConnected + ");", null);
            }
        }));

        // 2. Konfigurasi Layar Penuh Murni (Immersive Sticky Mode - Bebas Popup Chrome)
        applyImmersiveStickyMode();

        // 3. Konfigurasi WebView berperforma tinggi
        setupWebView();
        webView.addJavascriptInterface(new WebAppInterface(), "DigiAndroidBridge");

        // Periksa & minta izin runtime Android (Audio Mic & Bluetooth)
        checkAndRequestPermissions();

        // 4. Tombol pengaturan server
        btnServerSettings.setOnClickListener(v -> showServerConfigDialog());

        // 5. Muat URL Server tersimpan atau minta input pertama kali
        String savedUrl = prefs.getString(KEY_SERVER_URL, null);
        if (savedUrl != null && !savedUrl.trim().isEmpty()) {
            loadServerUrl(savedUrl);
        } else {
            showServerConfigDialog();
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            applyImmersiveStickyMode();
        }
    }

    /**
     * Mode Layar Penuh Imersif Sejati Android (Menyembunyikan Navigation Bar & Status Bar permanen)
     * Tidak akan memicu peringatan/toast "Swipe to exit" dari Chrome!
     */
    private void applyImmersiveStickyMode() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            getWindow().getAttributes().layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            WindowInsetsController controller = getWindow().getInsetsController();
            if (controller != null) {
                controller.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                controller.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            }
        } else {
            View decorView = getWindow().getDecorView();
            decorView.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
            );
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        settings.setCacheMode(WebSettings.LOAD_NO_CACHE);

        // Optimasi sentuhan & rendering
        webView.setHapticFeedbackEnabled(true);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        webView.setBackgroundColor(Color.parseColor("#0d1117"));

        // Cegah keyboard virtual HP bawaan muncul menutupi DigiSmartDeck
        webView.setOnTouchListener((v, event) -> {
            InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
            if (imm != null) {
                imm.hideSoftInputFromWindow(v.getWindowToken(), 0);
            }
            return false;
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(() -> {
                    boolean audioNeeded = false;
                    for (String res : request.getResources()) {
                        if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(res)) {
                            audioNeeded = true;
                            break;
                        }
                    }

                    if (audioNeeded && ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                        pendingPermissionRequest = request;
                        ActivityCompat.requestPermissions(
                            MainActivity.this,
                            new String[]{Manifest.permission.RECORD_AUDIO},
                            REQUEST_CODE_PERMISSIONS
                        );
                    } else {
                        request.grant(request.getResources());
                    }
                });
            }

            @Override
            public void onPermissionRequestCanceled(PermissionRequest request) {
                super.onPermissionRequestCanceled(request);
                pendingPermissionRequest = null;
            }
        });
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                super.onReceivedError(view, request, error);
                if (request.isForMainFrame()) {
                    showConnectionErrorPage();
                }
            }
        });
    }

    private void loadServerUrl(String rawUrl) {
        String cleanUrl = rawUrl.trim();
        if (!cleanUrl.startsWith("http://") && !cleanUrl.startsWith("https://")) {
            if (!cleanUrl.contains(":")) {
                cleanUrl = "http://" + cleanUrl + ":8080";
            } else {
                cleanUrl = "http://" + cleanUrl;
            }
        }
        prefs.edit().putString(KEY_SERVER_URL, cleanUrl).apply();
        webView.clearCache(true);
        webView.loadUrl(cleanUrl);
    }

    private void showServerConfigDialog() {
        LayoutInflater inflater = LayoutInflater.from(this);
        View dialogView = inflater.inflate(R.layout.dialog_server_config, null);

        EditText etServerUrl = dialogView.findViewById(R.id.etServerUrl);
        Button btnCancel = dialogView.findViewById(R.id.btnCancel);
        Button btnConnect = dialogView.findViewById(R.id.btnConnect);

        String currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL);
        etServerUrl.setText(currentUrl);
        etServerUrl.setSelection(etServerUrl.getText().length());

        AlertDialog dialog = new AlertDialog.Builder(this)
            .setView(dialogView)
            .setCancelable(true)
            .create();

        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        }

        btnCancel.setOnClickListener(v -> dialog.dismiss());

        btnConnect.setOnClickListener(v -> {
            String inputUrl = etServerUrl.getText().toString();
            if (inputUrl.trim().isEmpty()) {
                Toast.makeText(this, "Masukkan alamat IP server PC Anda", Toast.LENGTH_SHORT).show();
                return;
            }
            dialog.dismiss();
            loadServerUrl(inputUrl);
            applyImmersiveStickyMode();
        });

        dialog.show();
    }

    private void showConnectionErrorPage() {
        String currentUrl = prefs.getString(KEY_SERVER_URL, "");
        String errorHtml = "<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            + "<style>body{background:#0d1117;color:#e6edf3;font-family:sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center;padding:20px;}"
            + "h2{color:#f85149;margin-bottom:8px;}p{color:#8b949e;font-size:14px;line-height:1.5;max-width:400px;}"
            + "button{background:#0969da;color:#fff;border:none;padding:10px 20px;border-radius:6px;font-size:14px;cursor:pointer;margin-top:16px;font-weight:600;}"
            + "</style></head><body>"
            + "<h2>Gagal Terhubung ke PC</h2>"
            + "<p>Tidak dapat tersambung ke <b>" + currentUrl + "</b>.<br>"
            + "Pastikan PC dan HP Anda terhubung ke <b>Wi-Fi yang sama</b> dan aplikasi server di PC sedang aktif.</p>"
            + "<button onclick='location.reload()'>Coba Lagi</button>"
            + "</body></html>";
        webView.loadDataWithBaseURL(null, errorHtml, "text/html", "UTF-8", null);
    }

    @Override
    public void onBackPressed() {
        // Tampilkan konfirmasi keluar atau ganti server
        new AlertDialog.Builder(this)
            .setTitle("DigiSmartDeck")
            .setMessage("Apakah Anda ingin keluar dari aplikasi atau mengganti alamat server PC?")
            .setPositiveButton("Ganti Server", (d, w) -> showServerConfigDialog())
            .setNegativeButton("Keluar", (d, w) -> finish())
            .setNeutralButton("Tetap Pakai", null)
            .show();
    }

    private void checkAndRequestPermissions() {
        List<String> needed = new ArrayList<>();
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            needed.add(Manifest.permission.RECORD_AUDIO);
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                needed.add(Manifest.permission.BLUETOOTH_CONNECT);
            }
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) {
                needed.add(Manifest.permission.BLUETOOTH_SCAN);
            }
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_ADVERTISE) != PackageManager.PERMISSION_GRANTED) {
                needed.add(Manifest.permission.BLUETOOTH_ADVERTISE);
            }
        }
        if (!needed.isEmpty()) {
            ActivityCompat.requestPermissions(this, needed.toArray(new String[0]), REQUEST_CODE_PERMISSIONS);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            boolean audioGranted = ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED;
            if (pendingPermissionRequest != null) {
                if (audioGranted) {
                    pendingPermissionRequest.grant(pendingPermissionRequest.getResources());
                } else {
                    pendingPermissionRequest.deny();
                }
                pendingPermissionRequest = null;
            }
        }
    }

    private void muteChime() {
        try {
            if (audioManager == null) {
                audioManager = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
            }
            if (audioManager != null && !isMutedByBridge) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    audioManager.adjustStreamVolume(AudioManager.STREAM_NOTIFICATION, AudioManager.ADJUST_MUTE, 0);
                    audioManager.adjustStreamVolume(AudioManager.STREAM_SYSTEM, AudioManager.ADJUST_MUTE, 0);
                } else {
                    audioManager.setStreamMute(AudioManager.STREAM_NOTIFICATION, true);
                    audioManager.setStreamMute(AudioManager.STREAM_SYSTEM, true);
                }
                isMutedByBridge = true;
            }
        } catch (Throwable ignored) {}
    }

    private void unmuteChimeDelayed(long delayMs) {
        if (speechHandler == null) return;
        speechHandler.postDelayed(() -> {
            try {
                if (audioManager != null && isMutedByBridge) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                        audioManager.adjustStreamVolume(AudioManager.STREAM_NOTIFICATION, AudioManager.ADJUST_UNMUTE, 0);
                        audioManager.adjustStreamVolume(AudioManager.STREAM_SYSTEM, AudioManager.ADJUST_UNMUTE, 0);
                    } else {
                        audioManager.setStreamMute(AudioManager.STREAM_NOTIFICATION, false);
                        audioManager.setStreamMute(AudioManager.STREAM_SYSTEM, false);
                    }
                    isMutedByBridge = false;
                }
            } catch (Throwable ignored) {}
        }, delayMs);
    }

    private void scheduleSpeechRestart(long delayMs) {
        if (!isListeningActive || !isAlwaysOnSpeech) return;
        if (speechHandler == null) return;
        speechHandler.removeCallbacksAndMessages(null);
        speechHandler.postDelayed(() -> {
            if (!isListeningActive || !isAlwaysOnSpeech) return;
            runOnUiThread(() -> {
                try {
                    muteChime();
                    if (speechRecognizer == null) {
                        initSpeechRecognizer();
                    }
                    if (speechRecognizer != null && speechRecognizerIntent != null) {
                        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, currentSpeechLang);
                        speechRecognizer.startListening(speechRecognizerIntent);
                    }
                } catch (Exception e) {
                    if (isListeningActive && isAlwaysOnSpeech) {
                        speechHandler.postDelayed(() -> scheduleSpeechRestart(250), 150);
                    }
                }
            });
        }, delayMs);
    }

    private void initSpeechRecognizer() {
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            return;
        }
        if (speechRecognizer != null) {
            try {
                speechRecognizer.destroy();
            } catch (Exception ignored) {}
            speechRecognizer = null;
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && SpeechRecognizer.isOnDeviceRecognitionAvailable(this)) {
            speechRecognizer = SpeechRecognizer.createOnDeviceSpeechRecognizer(this);
        } else {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this);
        }

        speechRecognizerIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3);
        speechRecognizerIntent.putExtra("android.speech.extra.DICTATION_MODE", true);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 3000L);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 2500L);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS, 1500L);

        speechRecognizer.setRecognitionListener(new RecognitionListener() {
            @Override
            public void onReadyForSpeech(Bundle params) {
                runOnUiThread(() -> {
                    if (webView != null) {
                        webView.evaluateJavascript("if (window.onNativeSpeechStart) window.onNativeSpeechStart();", null);
                    }
                });
            }

            @Override
            public void onBeginningOfSpeech() {}

            @Override
            public void onRmsChanged(float rmsdB) {}

            @Override
            public void onBufferReceived(byte[] buffer) {}

            @Override
            public void onEndOfSpeech() {
                runOnUiThread(() -> {
                    if (webView != null) {
                        webView.evaluateJavascript("if (window.onNativeSpeechEnd) window.onNativeSpeechEnd();", null);
                    }
                });
            }

            @Override
            public void onError(int error) {
                if (isListeningActive && isAlwaysOnSpeech) {
                    if (error == SpeechRecognizer.ERROR_NO_MATCH ||
                        error == SpeechRecognizer.ERROR_SPEECH_TIMEOUT ||
                        error == SpeechRecognizer.ERROR_RECOGNIZER_BUSY ||
                        error == SpeechRecognizer.ERROR_NETWORK_TIMEOUT) {
                        scheduleSpeechRestart(120);
                        return;
                    }
                }

                isListeningActive = false;
                unmuteChimeDelayed(100);
                runOnUiThread(() -> {
                    if (webView != null) {
                        webView.evaluateJavascript("if (window.onNativeSpeechError) window.onNativeSpeechError(" + error + ");", null);
                    }
                });
            }

            @Override
            public void onResults(Bundle results) {
                if (results != null) {
                    ArrayList<String> matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                    if (matches != null && !matches.isEmpty()) {
                        String text = matches.get(0);
                        runOnUiThread(() -> {
                            if (webView != null) {
                                String escaped = text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ");
                                webView.evaluateJavascript("if (window.onNativeSpeechResult) window.onNativeSpeechResult('" + escaped + "');", null);
                            }
                        });
                    }
                }

                if (isListeningActive && isAlwaysOnSpeech) {
                    scheduleSpeechRestart(100);
                } else {
                    isListeningActive = false;
                    unmuteChimeDelayed(100);
                }
            }

            @Override
            public void onPartialResults(Bundle partialResults) {
                if (partialResults != null) {
                    ArrayList<String> matches = partialResults.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                    if (matches != null && !matches.isEmpty()) {
                        String text = matches.get(0);
                        runOnUiThread(() -> {
                            if (webView != null) {
                                String escaped = text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ");
                                webView.evaluateJavascript("if (window.onNativeSpeechPartial) window.onNativeSpeechPartial('" + escaped + "');", null);
                            }
                        });
                    }
                }
            }

            @Override
            public void onEvent(int eventType, Bundle params) {}
        });
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (isListeningActive) {
            isListeningActive = false;
            if (speechHandler != null) {
                speechHandler.removeCallbacksAndMessages(null);
            }
            if (speechRecognizer != null) {
                try {
                    speechRecognizer.cancel();
                } catch (Exception ignored) {}
            }
            unmuteChimeDelayed(0);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        isListeningActive = false;
        if (speechHandler != null) {
            speechHandler.removeCallbacksAndMessages(null);
        }
        unmuteChimeDelayed(0);
        if (bluetoothHidHelper != null) {
            bluetoothHidHelper.unregister();
        }
        if (speechRecognizer != null) {
            speechRecognizer.destroy();
            speechRecognizer = null;
        }
    }
}
