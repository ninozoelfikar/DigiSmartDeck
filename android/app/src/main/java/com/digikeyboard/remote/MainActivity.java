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
import android.util.Log;
import android.webkit.ConsoleMessage;
import android.webkit.JsResult;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
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
import androidx.core.content.FileProvider;

import android.net.Uri;
import android.provider.Settings;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "DigiKeyboardPrefs";
    private static final String KEY_SERVER_URL = "server_url";
    private static final String DEFAULT_URL = "http://192.168.8.102:8080";
    private static final int REQUEST_CODE_PERMISSIONS = 2001;
    private static final int REQUEST_CODE_INSTALL_PERMISSION = 3001;

    private WebView webView;
    private SharedPreferences prefs;
    private BluetoothHidHelper bluetoothHidHelper;
    private PermissionRequest pendingPermissionRequest;
    private SpeechRecognizer speechRecognizer;
    private Intent speechRecognizerIntent;
    private AudioManager audioManager;
    private Handler speechHandler = new Handler(Looper.getMainLooper());
    private final Handler muteHandler = new Handler(Looper.getMainLooper());
    private boolean isAlwaysOnSpeech = true;
    private boolean isListeningActive = false;
    private boolean isMutedByBridge = false;
    private int speechQuickFailStreak = 0;
    private long speechSessionStartMs = 0L;
    private String currentSpeechLang = "id-ID";

    private File pendingApkToInstall = null;
    private final ExecutorService downloadExecutor = Executors.newSingleThreadExecutor();

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
            try {
                return SpeechRecognizer.isRecognitionAvailable(MainActivity.this);
            } catch (Exception e) {
                return false;
            }
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
                speechQuickFailStreak = 0;
                currentSpeechLang = (lang != null && !lang.isEmpty()) ? lang : "id-ID";
                startListeningNow(150, false);
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
                restoreBeepStreams();
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
                restoreBeepStreams();
            });
        }

        @android.webkit.JavascriptInterface
        public void openServerSettings() {
            runOnUiThread(() -> showServerConfigDialog());
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

        @android.webkit.JavascriptInterface
        public boolean isNativeApp() {
            return true;
        }

        @android.webkit.JavascriptInterface
        public String getInstalledVersionName() {
            try {
                return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
            } catch (Exception e) {
                return "1.0.0";
            }
        }

        @android.webkit.JavascriptInterface
        public int getInstalledVersionCode() {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                    return (int) getPackageManager().getPackageInfo(getPackageName(), 0).getLongVersionCode();
                } else {
                    return getPackageManager().getPackageInfo(getPackageName(), 0).versionCode;
                }
            } catch (Exception e) {
                return 10000;
            }
        }

        @android.webkit.JavascriptInterface
        public void downloadAndInstallUpdate(String downloadUrl, String targetVersion) {
            final String rawUrl = (downloadUrl != null && !downloadUrl.trim().isEmpty()) ? downloadUrl.trim() : "/download/apk";
            final String finalUrl = resolveFullUrl(rawUrl);
            downloadExecutor.execute(() -> startApkDownload(finalUrl, targetVersion));
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

        // 4. Muat URL Server tersimpan atau minta input pertama kali
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
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(false);
        settings.setDisplayZoomControls(false);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        }

        // Hardware acceleration & rendering
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null);
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
            public boolean onConsoleMessage(ConsoleMessage consoleMessage) {
                Log.d("DigiSmartDeck", consoleMessage.message() + " [" + consoleMessage.sourceId() + ":" + consoleMessage.lineNumber() + "]");
                return true;
            }

            @Override
            public boolean onJsAlert(WebView view, String url, String message, JsResult result) {
                new AlertDialog.Builder(MainActivity.this)
                    .setTitle("DigiSmartDeck")
                    .setMessage(message)
                    .setPositiveButton(android.R.string.ok, (d, w) -> result.confirm())
                    .setCancelable(false)
                    .show();
                return true;
            }

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
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                super.onReceivedError(view, request, error);
                if (request != null && request.isForMainFrame()) {
                    showConnectionErrorPage();
                }
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                super.onReceivedError(view, errorCode, description, failingUrl);
                showConnectionErrorPage();
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

        btnCancel.setOnClickListener(v -> {
            dialog.dismiss();
            String saved = prefs.getString(KEY_SERVER_URL, null);
            if (saved == null || saved.trim().isEmpty()) {
                showConnectionErrorPage();
            }
        });

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
        String currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL);
        String errorHtml = "<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            + "<style>body{background:#0d1117;color:#e6edf3;font-family:sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center;padding:24px;box-sizing:border-box;}"
            + "h2{color:#f85149;margin-bottom:8px;}p{color:#8b949e;font-size:14px;line-height:1.5;max-width:440px;margin-bottom:20px;}"
            + ".btn-wrap{display:flex;gap:12px;flex-wrap:wrap;justify-content:center;}"
            + "button{border:none;padding:11px 22px;border-radius:8px;font-size:14px;cursor:pointer;font-weight:600;}"
            + ".btn-pri{background:#0969da;color:#fff;}"
            + ".btn-sec{background:#21262d;color:#c9d1d9;border:1px solid #30363d;}"
            + "</style></head><body>"
            + "<h2>Gagal Terhubung ke PC</h2>"
            + "<p>Tidak dapat tersambung ke <b>" + currentUrl + "</b>.<br>"
            + "Pastikan PC dan HP Anda terhubung ke <b>Wi-Fi yang sama</b> dan aplikasi server di PC sedang aktif.</p>"
            + "<div class='btn-wrap'>"
            + "<button class='btn-sec' onclick='if(window.DigiAndroidBridge)DigiAndroidBridge.openServerSettings();'>Ganti Server IP</button>"
            + "<button class='btn-pri' onclick='location.reload()'>Coba Lagi</button>"
            + "</div>"
            + "</body></html>";
        webView.loadDataWithBaseURL("http://localhost:8080/", errorHtml, "text/html", "UTF-8", null);
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

    // ─── Peredam chime Google SpeechRecognizer ───
    private AudioManager getAudio() {
        if (audioManager == null) {
            audioManager = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
        }
        return audioManager;
    }

    @SuppressWarnings("deprecation")
    private void setStreamMuted(int stream, boolean mute) {
        AudioManager am = getAudio();
        if (am == null) return;
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                am.adjustStreamVolume(stream, mute ? AudioManager.ADJUST_MUTE : AudioManager.ADJUST_UNMUTE, 0);
            } else {
                am.setStreamMute(stream, mute);
            }
        } catch (Exception ignored) {
        }
    }

    private void muteBeepStreams() {
        muteHandler.removeCallbacksAndMessages(null);
        if (!isMutedByBridge) {
            setStreamMuted(AudioManager.STREAM_NOTIFICATION, true);
            setStreamMuted(AudioManager.STREAM_SYSTEM, true);
            isMutedByBridge = true;
        }
    }

    private void restoreBeepStreams() {
        muteHandler.removeCallbacksAndMessages(null);
        if (isMutedByBridge) {
            setStreamMuted(AudioManager.STREAM_NOTIFICATION, false);
            setStreamMuted(AudioManager.STREAM_SYSTEM, false);
            isMutedByBridge = false;
        }
    }

    private void notifyJsSegmentRestart() {
        if (webView != null) {
            webView.evaluateJavascript("if (window.onNativeSpeechRestart) window.onNativeSpeechRestart();", null);
        }
    }

    private void startListeningNow(long delayMs, boolean recreate) {
        if (!isListeningActive) return;
        if (speechHandler == null) return;
        speechHandler.removeCallbacksAndMessages(null);
        speechHandler.postDelayed(() -> {
            if (!isListeningActive) return;
            try {
                if (recreate || speechRecognizer == null) {
                    initSpeechRecognizer();
                }
                if (speechRecognizer == null || speechRecognizerIntent == null) {
                    // Layanan belum siap; coba lagi dengan jeda lebih panjang.
                    speechHandler.postDelayed(() -> startListeningNow(0, true), 800);
                    return;
                }
                speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, currentSpeechLang);
                speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, currentSpeechLang);
                muteBeepStreams();
                speechRecognizer.cancel();
                speechRecognizer.startListening(speechRecognizerIntent);
            } catch (Exception e) {
                if (isListeningActive) {
                    speechHandler.postDelayed(() -> startListeningNow(0, true), 400);
                }
            }
        }, delayMs);
    }

    private void scheduleSpeechRestart(long delayMs, boolean recreate) {
        if (!isListeningActive || !isAlwaysOnSpeech) return;
        startListeningNow(delayMs, recreate);
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

        try {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this);
        } catch (Exception e) {
            e.printStackTrace();
            return;
        }

        speechRecognizerIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, getPackageName());
        speechRecognizerIntent.putExtra("android.speech.extra.DICTATION_MODE", true);
        // Jendela hening diperpanjang agar jeda berpikir tidak langsung memotong sesi.
        // Sebagian versi layanan Google mengabaikan nilai ini; restart otomatis di bawah
        // tetap menjaga mic terus aktif.
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 6000L);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 5000L);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS, 10000L);

        speechRecognizer.setRecognitionListener(new RecognitionListener() {
            @Override
            public void onReadyForSpeech(Bundle params) {
                speechSessionStartMs = System.currentTimeMillis();
                runOnUiThread(() -> {
                    if (webView != null) {
                        webView.evaluateJavascript("if (window.onNativeSpeechStart) window.onNativeSpeechStart();", null);
                    }
                });
            }

            @Override
            public void onBeginningOfSpeech() {
                speechQuickFailStreak = 0;
            }

            @Override
            public void onRmsChanged(float rmsdB) {}

            @Override
            public void onBufferReceived(byte[] buffer) {}

            @Override
            public void onEndOfSpeech() {
                muteBeepStreams();
                runOnUiThread(() -> {
                    if (webView != null) {
                        webView.evaluateJavascript("if (window.onNativeSpeechEnd) window.onNativeSpeechEnd();", null);
                    }
                });
            }

            @Override
            public void onError(int error) {
                // 9 = izin ditolak, 12/13 = bahasa tidak didukung/tidak tersedia.
                boolean fatal = error == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS
                    || error == 12 || error == 13;

                if (isListeningActive && isAlwaysOnSpeech && !fatal) {
                    long sessionAge = System.currentTimeMillis() - speechSessionStartMs;
                    boolean silenceTimeout = error == SpeechRecognizer.ERROR_NO_MATCH
                        || error == SpeechRecognizer.ERROR_SPEECH_TIMEOUT;

                    if (silenceTimeout && sessionAge > 2000) {
                        speechQuickFailStreak = 0;
                    } else {
                        speechQuickFailStreak++;
                    }

                    // BUSY, CLIENT, SERVER, AUDIO, SERVER_DISCONNECTED(11): engine perlu dibuat ulang.
                    boolean recreate = error == SpeechRecognizer.ERROR_RECOGNIZER_BUSY
                        || error == SpeechRecognizer.ERROR_CLIENT
                        || error == SpeechRecognizer.ERROR_SERVER
                        || error == SpeechRecognizer.ERROR_AUDIO
                        || error == 11
                        || speechQuickFailStreak >= 3;

                    long delay;
                    if (error == 10) {
                        delay = 2000L; // ERROR_TOO_MANY_REQUESTS
                    } else if (speechQuickFailStreak <= 2) {
                        delay = 60L;
                    } else {
                        delay = Math.min(150L << Math.min(speechQuickFailStreak - 2, 4), 2400L);
                    }

                    muteBeepStreams();
                    runOnUiThread(MainActivity.this::notifyJsSegmentRestart);
                    scheduleSpeechRestart(delay, recreate);
                    return;
                }

                isListeningActive = false;
                muteBeepStreams();
                muteHandler.removeCallbacksAndMessages(null);
                muteHandler.postDelayed(MainActivity.this::restoreBeepStreams, 1000);
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
                        speechQuickFailStreak = 0;
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
                    muteBeepStreams();
                    scheduleSpeechRestart(40, false);
                } else {
                    isListeningActive = false;
                    muteBeepStreams();
                    muteHandler.removeCallbacksAndMessages(null);
                    muteHandler.postDelayed(MainActivity.this::restoreBeepStreams, 1200);
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
            if (webView != null) {
                webView.evaluateJavascript("if (window.onNativeSpeechError) window.onNativeSpeechError(-1);", null);
            }
        }
        restoreBeepStreams();
    }

    private String resolveFullUrl(String url) {
        if (url == null || url.trim().isEmpty()) {
            url = "/download/apk";
        }
        if (url.startsWith("http://") || url.startsWith("https://")) {
            return url;
        }
        String serverUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL);
        if (serverUrl.endsWith("/")) {
            serverUrl = serverUrl.substring(0, serverUrl.length() - 1);
        }
        if (!url.startsWith("/")) {
            url = "/" + url;
        }
        return serverUrl + url;
    }

    private void startApkDownload(String downloadUrl, String targetVersion) {
        HttpURLConnection connection = null;
        InputStream input = null;
        FileOutputStream output = null;
        try {
            runOnUiThread(() -> {
                if (webView != null) {
                    webView.evaluateJavascript("if (window.onUpdateDownloadStart) window.onUpdateDownloadStart();", null);
                }
            });

            URL url = new URL(downloadUrl);
            connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(15000);
            connection.setReadTimeout(45000);
            connection.setInstanceFollowRedirects(true);
            connection.connect();

            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                throw new Exception("HTTP status " + responseCode);
            }

            long fileLength = -1;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                fileLength = connection.getContentLengthLong();
            }
            if (fileLength <= 0) {
                fileLength = connection.getContentLength();
            }

            File cacheDir = getExternalCacheDir();
            if (cacheDir == null) {
                cacheDir = getCacheDir();
            }
            File apkFile = new File(cacheDir, "DigiSmartDeck-update.apk");
            if (apkFile.exists()) {
                apkFile.delete();
            }

            input = connection.getInputStream();
            output = new FileOutputStream(apkFile);

            byte[] buffer = new byte[8192];
            long total = 0;
            int count;
            long lastReportTime = 0;

            while ((count = input.read(buffer)) != -1) {
                total += count;
                output.write(buffer, 0, count);

                long now = System.currentTimeMillis();
                if (now - lastReportTime > 250 || (fileLength > 0 && total == fileLength)) {
                    lastReportTime = now;
                    int progress = (fileLength > 0) ? (int) ((total * 100) / fileLength) : -1;
                    final int fProg = progress;
                    final long fTotal = total;
                    final long fLen = fileLength;
                    runOnUiThread(() -> {
                        if (webView != null) {
                            webView.evaluateJavascript("if (window.onUpdateDownloadProgress) window.onUpdateDownloadProgress(" + fProg + ", " + fTotal + ", " + fLen + ");", null);
                        }
                    });
                }
            }
            output.flush();

            final File finalApkFile = apkFile;
            runOnUiThread(() -> {
                if (webView != null) {
                    webView.evaluateJavascript("if (window.onUpdateDownloadComplete) window.onUpdateDownloadComplete();", null);
                }
                promptInstallApk(finalApkFile);
            });

        } catch (Exception e) {
            final String errorMsg = (e.getMessage() != null) ? e.getMessage().replace("'", "\\'") : "Download error";
            runOnUiThread(() -> {
                if (webView != null) {
                    webView.evaluateJavascript("if (window.onUpdateDownloadError) window.onUpdateDownloadError('" + errorMsg + "');", null);
                }
                Toast.makeText(MainActivity.this, "Gagal mengunduh pembaruan: " + e.getMessage(), Toast.LENGTH_LONG).show();
            });
        } finally {
            try {
                if (output != null) output.close();
                if (input != null) input.close();
                if (connection != null) connection.disconnect();
            } catch (Exception ignored) {}
        }
    }

    private void promptInstallApk(File apkFile) {
        if (apkFile == null || !apkFile.exists()) {
            Toast.makeText(this, "File paket instalasi tidak ditemukan.", Toast.LENGTH_SHORT).show();
            return;
        }
        pendingApkToInstall = apkFile;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            if (!getPackageManager().canRequestPackageInstalls()) {
                Toast.makeText(this, "Izinkan instalasi pembaruan aplikasi untuk DigiSmartDeck", Toast.LENGTH_LONG).show();
                try {
                    Intent intent = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES);
                    intent.setData(Uri.parse("package:" + getPackageName()));
                    startActivityForResult(intent, REQUEST_CODE_INSTALL_PERMISSION);
                } catch (Exception e) {
                    Intent intent = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES);
                    startActivityForResult(intent, REQUEST_CODE_INSTALL_PERMISSION);
                }
                return;
            }
        }

        try {
            Uri apkUri = FileProvider.getUriForFile(
                MainActivity.this,
                getPackageName() + ".fileprovider",
                apkFile
            );

            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setDataAndType(apkUri, "application/vnd.android.package-archive");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Exception e) {
            Log.e("DigiSmartDeck", "Gagal membuka installer APK", e);
            Toast.makeText(MainActivity.this, "Gagal membuka installer APK: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CODE_INSTALL_PERMISSION) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                if (getPackageManager().canRequestPackageInstalls()) {
                    if (pendingApkToInstall != null && pendingApkToInstall.exists()) {
                        promptInstallApk(pendingApkToInstall);
                    }
                } else {
                    Toast.makeText(this, "Izin instalasi pembaruan belum diberikan.", Toast.LENGTH_SHORT).show();
                }
            }
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        isListeningActive = false;
        if (speechHandler != null) {
            speechHandler.removeCallbacksAndMessages(null);
        }
        restoreBeepStreams();
        if (downloadExecutor != null) {
            downloadExecutor.shutdownNow();
        }
        if (bluetoothHidHelper != null) {
            bluetoothHidHelper.unregister();
        }
        if (speechRecognizer != null) {
            speechRecognizer.destroy();
            speechRecognizer = null;
        }
    }
}
