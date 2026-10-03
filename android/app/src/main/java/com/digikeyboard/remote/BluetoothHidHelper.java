package com.digikeyboard.remote;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothHidDevice;
import android.bluetooth.BluetoothHidDeviceAppQosSettings;
import android.bluetooth.BluetoothHidDeviceAppSdpSettings;
import android.bluetooth.BluetoothProfile;
import android.content.Context;
import android.os.Build;
import android.util.Log;

import androidx.annotation.RequiresApi;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executors;

/**
 * Bluetooth HID Helper untuk Android 9.0 (API 28) ke atas.
 * Menyamarkan HP menjadi Keyboard & Mouse Bluetooth fisik asli.
 */
public class BluetoothHidHelper {

    private static final String TAG = "DigiBluetoothHid";
    private static final String APP_NAME = "DigiSmartDeck HID";
    private static final String PROVIDER = "DigiSmartDeck";

    private static final byte[] HID_REPORT_DESCRIPTOR = new byte[]{
        // Keyboard (Report ID 1)
        (byte) 0x05, (byte) 0x01,
        (byte) 0x09, (byte) 0x06,
        (byte) 0xa1, (byte) 0x01,
        (byte) 0x85, (byte) 0x01,
        (byte) 0x05, (byte) 0x07,
        (byte) 0x19, (byte) 0xe0,
        (byte) 0x29, (byte) 0xe7,
        (byte) 0x15, (byte) 0x00,
        (byte) 0x25, (byte) 0x01,
        (byte) 0x75, (byte) 0x01,
        (byte) 0x95, (byte) 0x08,
        (byte) 0x81, (byte) 0x02,
        (byte) 0x95, (byte) 0x01,
        (byte) 0x75, (byte) 0x08,
        (byte) 0x81, (byte) 0x03,
        (byte) 0x95, (byte) 0x06,
        (byte) 0x75, (byte) 0x08,
        (byte) 0x15, (byte) 0x00,
        (byte) 0x25, (byte) 0x65,
        (byte) 0x05, (byte) 0x07,
        (byte) 0x19, (byte) 0x00,
        (byte) 0x29, (byte) 0x65,
        (byte) 0x81, (byte) 0x00,
        (byte) 0xc0,

        // Mouse (Report ID 2)
        (byte) 0x05, (byte) 0x01,
        (byte) 0x09, (byte) 0x02,
        (byte) 0xa1, (byte) 0x01,
        (byte) 0x85, (byte) 0x02,
        (byte) 0x09, (byte) 0x01,
        (byte) 0xa1, (byte) 0x00,
        (byte) 0x05, (byte) 0x09,
        (byte) 0x19, (byte) 0x01,
        (byte) 0x29, (byte) 0x03,
        (byte) 0x15, (byte) 0x00,
        (byte) 0x25, (byte) 0x01,
        (byte) 0x75, (byte) 0x01,
        (byte) 0x95, (byte) 0x03,
        (byte) 0x81, (byte) 0x02,
        (byte) 0x75, (byte) 0x05,
        (byte) 0x95, (byte) 0x01,
        (byte) 0x81, (byte) 0x03,
        (byte) 0x05, (byte) 0x01,
        (byte) 0x09, (byte) 0x30,
        (byte) 0x09, (byte) 0x31,
        (byte) 0x09, (byte) 0x38,
        (byte) 0x15, (byte) 0x81,
        (byte) 0x25, (byte) 0x7f,
        (byte) 0x75, (byte) 0x08,
        (byte) 0x95, (byte) 0x03,
        (byte) 0x81, (byte) 0x06,
        (byte) 0xc0,
        (byte) 0xc0
    };

    private static final Map<String, Byte> SCAN_CODES = new HashMap<>();

    static {
        // Letters A-Z
        for (int i = 0; i < 26; i++) {
            char c = (char) ('a' + i);
            SCAN_CODES.put(String.valueOf(c), (byte) (0x04 + i));
            SCAN_CODES.put(String.valueOf((char) ('A' + i)), (byte) (0x04 + i));
        }
        // Numbers 1-0
        for (int i = 1; i <= 9; i++) {
            SCAN_CODES.put(String.valueOf(i), (byte) (0x1e + i - 1));
        }
        SCAN_CODES.put("0", (byte) 0x27);

        // Special keys
        SCAN_CODES.put("enter", (byte) 0x28);
        SCAN_CODES.put("return", (byte) 0x28);
        SCAN_CODES.put("esc", (byte) 0x29);
        SCAN_CODES.put("backspace", (byte) 0x2a);
        SCAN_CODES.put("tab", (byte) 0x2b);
        SCAN_CODES.put("space", (byte) 0x2c);
        SCAN_CODES.put("caps_lock", (byte) 0x39);
        SCAN_CODES.put("f1", (byte) 0x3a);
        SCAN_CODES.put("f2", (byte) 0x3b);
        SCAN_CODES.put("f3", (byte) 0x3c);
        SCAN_CODES.put("f4", (byte) 0x3d);
        SCAN_CODES.put("f5", (byte) 0x3e);
        SCAN_CODES.put("f6", (byte) 0x3f);
        SCAN_CODES.put("f7", (byte) 0x40);
        SCAN_CODES.put("f8", (byte) 0x41);
        SCAN_CODES.put("f9", (byte) 0x42);
        SCAN_CODES.put("f10", (byte) 0x43);
        SCAN_CODES.put("f11", (byte) 0x44);
        SCAN_CODES.put("f12", (byte) 0x45);
        SCAN_CODES.put("right", (byte) 0x4f);
        SCAN_CODES.put("left", (byte) 0x50);
        SCAN_CODES.put("down", (byte) 0x51);
        SCAN_CODES.put("up", (byte) 0x52);
    }

    private final Context context;
    private BluetoothHidDevice hidDevice;
    private BluetoothDevice connectedHostDevice;
    private boolean isRegistered = false;

    public interface StatusListener {
        void onStatusChanged(String status, boolean isConnected);
    }

    private StatusListener statusListener;

    public BluetoothHidHelper(Context context) {
        this.context = context;
    }

    public void setStatusListener(StatusListener listener) {
        this.statusListener = listener;
    }

    public boolean isSupported() {
        return Build.VERSION.SDK_INT >= Build.VERSION_CODES.P;
    }

    @SuppressLint("MissingPermission")
    public void register() {
        if (!isSupported()) {
            if (statusListener != null) {
                statusListener.onStatusChanged("Fitur Bluetooth HID membutuhkan Android 9 (Pie) ke atas.", false);
            }
            return;
        }

        BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
        if (adapter == null || !adapter.isEnabled()) {
            if (statusListener != null) {
                statusListener.onStatusChanged("Bluetooth mati. Harap nyalakan Bluetooth HP.", false);
            }
            return;
        }

        adapter.getProfileProxy(context, new BluetoothProfile.ServiceListener() {
            @Override
            public void onServiceConnected(int profile, BluetoothProfile proxy) {
                if (profile == BluetoothProfile.HID_DEVICE) {
                    hidDevice = (BluetoothHidDevice) proxy;
                    registerApp();
                }
            }

            @Override
            public void onServiceDisconnected(int profile) {
                if (profile == BluetoothProfile.HID_DEVICE) {
                    hidDevice = null;
                    isRegistered = false;
                }
            }
        }, BluetoothProfile.HID_DEVICE);
    }

    @RequiresApi(api = Build.VERSION_CODES.P)
    @SuppressLint("MissingPermission")
    private void registerApp() {
        if (hidDevice == null) return;

        BluetoothHidDeviceAppSdpSettings sdp = new BluetoothHidDeviceAppSdpSettings(
            APP_NAME,
            "DigiSmartDeck Remote Hardware Controller",
            PROVIDER,
            BluetoothHidDevice.SUBCLASS1_COMBO,
            HID_REPORT_DESCRIPTOR
        );

        BluetoothHidDevice.Callback callback = new BluetoothHidDevice.Callback() {
            @Override
            public void onAppStatusChanged(BluetoothDevice pluggedDevice, boolean registered) {
                isRegistered = registered;
                Log.d(TAG, "App status changed, registered=" + registered);
                if (statusListener != null) {
                    statusListener.onStatusChanged(registered ? "Bluetooth HID Aktif. Menunggu pairing dari PC..." : "Pendaftaran HID gagal", false);
                }
            }

            @Override
            public void onConnectionStateChanged(BluetoothDevice device, int state) {
                if (state == BluetoothProfile.STATE_CONNECTED) {
                    connectedHostDevice = device;
                    if (statusListener != null) {
                        statusListener.onStatusChanged("🟢 Terhubung ke " + device.getName(), true);
                    }
                } else if (state == BluetoothProfile.STATE_DISCONNECTED) {
                    connectedHostDevice = null;
                    if (statusListener != null) {
                        statusListener.onStatusChanged("🟡 Terputus dari PC", false);
                    }
                }
            }
        };

        hidDevice.registerApp(sdp, null, null, Executors.newSingleThreadExecutor(), callback);
    }

    @SuppressLint("MissingPermission")
    public void sendKey(String key, boolean shift, boolean ctrl, boolean alt, boolean cmd) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        byte modifierByte = 0;
        if (ctrl) modifierByte |= 0x01;
        if (shift) modifierByte |= 0x02;
        if (alt) modifierByte |= 0x04;
        if (cmd) modifierByte |= 0x08;

        byte scanCode = SCAN_CODES.containsKey(key) ? SCAN_CODES.get(key) : 0;
        if (scanCode == 0) return;

        // Press report
        byte[] pressReport = new byte[]{modifierByte, 0, scanCode, 0, 0, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 1, pressReport);

        // Release report
        byte[] releaseReport = new byte[]{0, 0, 0, 0, 0, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 1, releaseReport);
    }

    @SuppressLint("MissingPermission")
    public void sendMouseMove(int dx, int dy, int button) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        byte btnByte = (byte) (button & 0x07);
        byte bX = (byte) Math.max(-127, Math.min(127, dx));
        byte bY = (byte) Math.max(-127, Math.min(127, dy));

        byte[] mouseReport = new byte[]{btnByte, bX, bY, 0};
        hidDevice.sendReport(connectedHostDevice, 2, mouseReport);
    }

    @SuppressLint("MissingPermission")
    public void unregister() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P && hidDevice != null && isRegistered) {
            try {
                hidDevice.unregisterApp();
            } catch (Exception e) {
                Log.e(TAG, "Error unregistering app", e);
            }
        }
    }
}
