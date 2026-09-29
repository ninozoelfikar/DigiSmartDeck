package com.digikeyboard.remote;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
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

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "DigiKeyboardPrefs";
    private static final String KEY_SERVER_URL = "server_url";
    private static final String DEFAULT_URL = "http://192.168.8.100:8080";

    private WebView webView;
    private ImageButton btnServerSettings;
    private SharedPreferences prefs;
    private BluetoothHidHelper bluetoothHidHelper;

    public class WebAppInterface {
        @android.webkit.JavascriptInterface
        public boolean isBluetoothAvailable() {
            return bluetoothHidHelper != null && bluetoothHidHelper.isSupported();
        }

        @android.webkit.JavascriptInterface
        public void enableBluetoothHid() {
            runOnUiThread(() -> {
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
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        // Optimasi sentuhan & rendering
        webView.setHapticFeedbackEnabled(true);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        webView.setBackgroundColor(Color.parseColor("#0d1117"));

        // Cegah keyboard virtual HP bawaan muncul menutupi DigiKeyboard
        webView.setOnTouchListener((v, event) -> {
            InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
            if (imm != null) {
                imm.hideSoftInputFromWindow(v.getWindowToken(), 0);
            }
            return false;
        });

        webView.setWebChromeClient(new WebChromeClient());
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
            .setTitle("DigiKeyboard")
            .setMessage("Apakah Anda ingin keluar dari aplikasi atau mengganti alamat server PC?")
            .setPositiveButton("Ganti Server", (d, w) -> showServerConfigDialog())
            .setNegativeButton("Keluar", (d, w) -> finish())
            .setNeutralButton("Tetap Pakai", null)
            .show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (bluetoothHidHelper != null) {
            bluetoothHidHelper.unregister();
        }
    }
}
