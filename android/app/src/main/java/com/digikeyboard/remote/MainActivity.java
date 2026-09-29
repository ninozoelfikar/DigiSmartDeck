package com.digikeyboard.remote;

import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.os.Build;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "DigiKeyboardPrefs";
    private static final String KEY_SERVER_URL = "server_url";
    private static final String KEY_TRACKPAD_ON = "trackpad_on";
    private static final String KEY_LOCK_ON = "lock_on";
    private static final String KEY_HAPTIC_ON = "haptic_on";
    private static final String DEFAULT_URL = "http://192.168.8.100:8080";

    private SharedPreferences prefs;
    private WebSocketManager wsManager;
    private BluetoothHidHelper bluetoothHidHelper;

    private TextView badgeStatus;
    private TextView txtPing;
    private Button btnTogglePad;
    private Button btnToggleLock;
    private Button btnToggleHaptic;
    private Button btnBluetooth;
    private ImageButton btnSettings;

    private LinearLayout trackpadContainer;
    private NativeTrackpadView nativeTrackpad;
    private Button btnLeftClick;
    private Button btnRightClick;
    private NativeKeyboardView nativeKeyboard;

    private boolean isTrackpadVisible = true;
    private boolean isPersistentLock = true;
    private boolean isHapticOn = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Keep screen awake & true immersive sticky fullscreen
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        applyImmersiveFullscreen();

        setContentView(R.layout.activity_main);

        prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        isTrackpadVisible = prefs.getBoolean(KEY_TRACKPAD_ON, true);
        isPersistentLock = prefs.getBoolean(KEY_LOCK_ON, true);
        isHapticOn = prefs.getBoolean(KEY_HAPTIC_ON, true);

        initViews();
        setupListeners();
        setupWebSocket();
        setupBluetooth();
    }

    private void applyImmersiveFullscreen() {
        View decorView = getWindow().getDecorView();
        int flags = View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY;
        decorView.setSystemUiVisibility(flags);

        decorView.setOnSystemUiVisibilityChangeListener(visibility -> {
            if ((visibility & View.SYSTEM_UI_FLAG_FULLSCREEN) == 0) {
                decorView.setSystemUiVisibility(flags);
            }
        });
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            applyImmersiveFullscreen();
        }
    }

    private void initViews() {
        badgeStatus = findViewById(R.id.badgeStatus);
        txtPing = findViewById(R.id.txtPing);
        btnTogglePad = findViewById(R.id.btnTogglePad);
        btnToggleLock = findViewById(R.id.btnToggleLock);
        btnToggleHaptic = findViewById(R.id.btnToggleHaptic);
        btnBluetooth = findViewById(R.id.btnBluetooth);
        btnSettings = findViewById(R.id.btnSettings);

        trackpadContainer = findViewById(R.id.trackpadContainer);
        nativeTrackpad = findViewById(R.id.nativeTrackpad);
        btnLeftClick = findViewById(R.id.btnLeftClick);
        btnRightClick = findViewById(R.id.btnRightClick);
        nativeKeyboard = findViewById(R.id.nativeKeyboard);

        // Apply initial preferences
        trackpadContainer.setVisibility(isTrackpadVisible ? View.VISIBLE : View.GONE);
        btnTogglePad.setTextColor(isTrackpadVisible ? Color.parseColor("#58a6ff") : Color.parseColor("#8b949e"));

        nativeKeyboard.setPersistentLock(isPersistentLock);
        btnToggleLock.setText(isPersistentLock ? "🔒 Lock" : "🖐️ Hold");
        btnToggleLock.setTextColor(isPersistentLock ? Color.parseColor("#3fb950") : Color.parseColor("#8b949e"));

        nativeKeyboard.setHapticEnabled(isHapticOn);
        btnToggleHaptic.setText(isHapticOn ? "📳 On" : "📳 Off");
        btnToggleHaptic.setTextColor(isHapticOn ? Color.parseColor("#f0f6fc") : Color.parseColor("#8b949e"));
    }

    private void setupListeners() {
        // Toggle Trackpad
        btnTogglePad.setOnClickListener(v -> {
            isTrackpadVisible = !isTrackpadVisible;
            prefs.edit().putBoolean(KEY_TRACKPAD_ON, isTrackpadVisible).apply();
            trackpadContainer.setVisibility(isTrackpadVisible ? View.VISIBLE : View.GONE);
            btnTogglePad.setTextColor(isTrackpadVisible ? Color.parseColor("#58a6ff") : Color.parseColor("#8b949e"));
        });

        // Toggle Persistent Lock
        btnToggleLock.setOnClickListener(v -> {
            isPersistentLock = !isPersistentLock;
            prefs.edit().putBoolean(KEY_LOCK_ON, isPersistentLock).apply();
            nativeKeyboard.setPersistentLock(isPersistentLock);
            btnToggleLock.setText(isPersistentLock ? "🔒 Lock" : "🖐️ Hold");
            btnToggleLock.setTextColor(isPersistentLock ? Color.parseColor("#3fb950") : Color.parseColor("#8b949e"));
            Toast.makeText(this, isPersistentLock ? "Kunci Modifier: Aktif Terus" : "Kunci Modifier: Mode Tahan (Hold)", Toast.LENGTH_SHORT).show();
        });

        // Toggle Haptic
        btnToggleHaptic.setOnClickListener(v -> {
            isHapticOn = !isHapticOn;
            prefs.edit().putBoolean(KEY_HAPTIC_ON, isHapticOn).apply();
            nativeKeyboard.setHapticEnabled(isHapticOn);
            btnToggleHaptic.setText(isHapticOn ? "📳 On" : "📳 Off");
            btnToggleHaptic.setTextColor(isHapticOn ? Color.parseColor("#f0f6fc") : Color.parseColor("#8b949e"));
        });

        // Settings Dialog
        btnSettings.setOnClickListener(v -> showServerConfigDialog());

        // Trackpad mouse events
        nativeTrackpad.setListener(new NativeTrackpadView.Listener() {
            @Override
            public void onMouseMove(int dx, int dy) {
                sendWsMouseMove(dx, dy);
                if (bluetoothHidHelper != null && bluetoothHidHelper.isRegistered()) {
                    bluetoothHidHelper.sendMouseMove(dx, dy, 0);
                }
            }

            @Override
            public void onMouseClick(String button) {
                sendWsMouseClick(button);
                if (bluetoothHidHelper != null && bluetoothHidHelper.isRegistered()) {
                    int b = "right".equals(button) ? 2 : 1;
                    bluetoothHidHelper.sendMouseMove(0, 0, b);
                    try { Thread.sleep(30); } catch (Exception ignored) {}
                    bluetoothHidHelper.sendMouseMove(0, 0, 0);
                }
            }

            @Override
            public void onMouseScroll(int dy) {
                sendWsMouseScroll(dy);
            }
        });

        // Physical mouse buttons
        btnLeftClick.setOnClickListener(v -> {
            sendWsMouseClick("left");
            if (bluetoothHidHelper != null && bluetoothHidHelper.isRegistered()) {
                bluetoothHidHelper.sendMouseMove(0, 0, 1);
                try { Thread.sleep(30); } catch (Exception ignored) {}
                bluetoothHidHelper.sendMouseMove(0, 0, 0);
            }
        });

        btnRightClick.setOnClickListener(v -> {
            sendWsMouseClick("right");
            if (bluetoothHidHelper != null && bluetoothHidHelper.isRegistered()) {
                bluetoothHidHelper.sendMouseMove(0, 0, 2);
                try { Thread.sleep(30); } catch (Exception ignored) {}
                bluetoothHidHelper.sendMouseMove(0, 0, 0);
            }
        });

        // Native Keyboard key events
        nativeKeyboard.setListener((type, key, character, modifiers) -> {
            sendWsKeyEvent(type, key, character, modifiers);

            if (bluetoothHidHelper != null && bluetoothHidHelper.isRegistered() && "keypress".equals(type)) {
                boolean shift = modifiers.optBoolean("shift", false);
                boolean ctrl = modifiers.optBoolean("ctrl", false);
                boolean alt = modifiers.optBoolean("alt", false);
                boolean cmd = modifiers.optBoolean("cmd", false);
                bluetoothHidHelper.sendKey(key, shift, ctrl, alt, cmd);
            }
        });
    }

    private void setupWebSocket() {
        wsManager = new WebSocketManager();
        wsManager.setListener(new WebSocketManager.Listener() {
            @Override
            public void onConnected() {
                badgeStatus.setText("🟢 Terhubung");
                badgeStatus.setTextColor(Color.parseColor("#3fb950"));
                badgeStatus.setBackgroundColor(Color.parseColor("#1f4068"));
            }

            @Override
            public void onDisconnected(String reason) {
                badgeStatus.setText("🔴 Terputus");
                badgeStatus.setTextColor(Color.parseColor("#f85149"));
                badgeStatus.setBackgroundColor(Color.parseColor("#21262d"));
                txtPing.setText("-- ms");
            }

            @Override
            public void onPingUpdated(long latencyMs) {
                txtPing.setText(latencyMs + " ms");
            }

            @Override
            public void onCapsState(boolean isCapsOn) {
                nativeKeyboard.setHostCapsState(isCapsOn);
            }
        });

        String savedUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL);
        wsManager.connect(savedUrl);
    }

    private void setupBluetooth() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            bluetoothHidHelper = new BluetoothHidHelper(this);
            if (bluetoothHidHelper.isSupported()) {
                btnBluetooth.setVisibility(View.VISIBLE);
                btnBluetooth.setOnClickListener(v -> {
                    if (bluetoothHidHelper.isRegistered()) {
                        bluetoothHidHelper.unregister();
                        btnBluetooth.setText("📶 BT");
                        btnBluetooth.setTextColor(Color.parseColor("#8b949e"));
                        Toast.makeText(this, "Bluetooth HID Dinonaktifkan", Toast.LENGTH_SHORT).show();
                    } else {
                        bluetoothHidHelper.register();
                        btnBluetooth.setText("📶 BT Aktif");
                        btnBluetooth.setTextColor(Color.parseColor("#3fb950"));
                        Toast.makeText(this, "Bluetooth HID Siap Dipasangkan!", Toast.LENGTH_SHORT).show();
                    }
                });
            } else {
                btnBluetooth.setVisibility(View.GONE);
            }
        } else {
            btnBluetooth.setVisibility(View.GONE);
        }
    }

    private void sendWsKeyEvent(String type, String key, String character, JSONObject modifiers) {
        if (wsManager == null || !wsManager.isConnected()) return;
        try {
            JSONObject obj = new JSONObject();
            obj.put("type", type);
            obj.put("key", key);
            if (character != null) obj.put("char", character);
            obj.put("modifiers", modifiers);
            obj.put("device_name", "Android Native (" + Build.MODEL + ")");
            wsManager.send(obj.toString());
        } catch (Exception ignored) {}
    }

    private void sendWsMouseMove(int dx, int dy) {
        if (wsManager == null || !wsManager.isConnected()) return;
        try {
            JSONObject obj = new JSONObject();
            obj.put("type", "mousemove");
            obj.put("dx", dx);
            obj.put("dy", dy);
            wsManager.send(obj.toString());
        } catch (Exception ignored) {}
    }

    private void sendWsMouseClick(String button) {
        if (wsManager == null || !wsManager.isConnected()) return;
        try {
            JSONObject obj = new JSONObject();
            obj.put("type", "mouseclick");
            obj.put("button", button);
            wsManager.send(obj.toString());
        } catch (Exception ignored) {}
    }

    private void sendWsMouseScroll(int dy) {
        if (wsManager == null || !wsManager.isConnected()) return;
        try {
            JSONObject obj = new JSONObject();
            obj.put("type", "mousescroll");
            obj.put("dx", 0);
            obj.put("dy", dy);
            wsManager.send(obj.toString());
        } catch (Exception ignored) {}
    }

    private void showServerConfigDialog() {
        LayoutInflater inflater = LayoutInflater.from(this);
        View dialogView = inflater.inflate(R.layout.dialog_server_config, null);

        EditText etServerUrl = dialogView.findViewById(R.id.etServerUrl);
        Button btnSave = dialogView.findViewById(R.id.btnConnect);
        Button btnCancel = dialogView.findViewById(R.id.btnCancel);

        String currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL);
        etServerUrl.setText(currentUrl);

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setView(dialogView)
                .setCancelable(true)
                .create();

        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        }

        btnSave.setOnClickListener(v -> {
            String newUrl = etServerUrl.getText().toString().trim();
            if (!newUrl.isEmpty()) {
                if (!newUrl.startsWith("http://") && !newUrl.startsWith("https://")) {
                    newUrl = "http://" + newUrl;
                }
                prefs.edit().putString(KEY_SERVER_URL, newUrl).apply();
                wsManager.connect(newUrl);
                Toast.makeText(this, "Menyambungkan ke: " + newUrl, Toast.LENGTH_SHORT).show();
            }
            dialog.dismiss();
            applyImmersiveFullscreen();
        });

        btnCancel.setOnClickListener(v -> {
            dialog.dismiss();
            applyImmersiveFullscreen();
        });

        dialog.show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (wsManager != null) {
            wsManager.disconnect();
        }
        if (bluetoothHidHelper != null) {
            bluetoothHidHelper.unregister();
        }
    }
}
