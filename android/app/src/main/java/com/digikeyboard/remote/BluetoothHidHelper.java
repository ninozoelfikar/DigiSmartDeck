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
 * Menyamarkan HP menjadi Keyboard & Mouse Bluetooth fisik asli tanpa perlu aplikasi di PC.
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
        // Letters a-z & A-Z
        for (int i = 0; i < 26; i++) {
            char c = (char) ('a' + i);
            SCAN_CODES.put(String.valueOf(c), (byte) (0x04 + i));
            SCAN_CODES.put(String.valueOf((char) ('A' + i)), (byte) (0x04 + i));
        }
        // Numbers 1-9 & 0
        for (int i = 1; i <= 9; i++) {
            SCAN_CODES.put(String.valueOf(i), (byte) (0x1e + i - 1));
        }
        SCAN_CODES.put("0", (byte) 0x27);

        // Control & Editing keys
        SCAN_CODES.put("enter", (byte) 0x28);
        SCAN_CODES.put("return", (byte) 0x28);
        SCAN_CODES.put("esc", (byte) 0x29);
        SCAN_CODES.put("escape", (byte) 0x29);
        SCAN_CODES.put("backspace", (byte) 0x2a);
        SCAN_CODES.put("tab", (byte) 0x2b);
        SCAN_CODES.put("space", (byte) 0x2c);
        SCAN_CODES.put("caps_lock", (byte) 0x39);
        SCAN_CODES.put("capslock", (byte) 0x39);

        // Symbols row & punctuation
        SCAN_CODES.put("-", (byte) 0x2d);
        SCAN_CODES.put("_", (byte) 0x2d);
        SCAN_CODES.put("=", (byte) 0x2e);
        SCAN_CODES.put("+", (byte) 0x2e);
        SCAN_CODES.put("[", (byte) 0x2f);
        SCAN_CODES.put("{", (byte) 0x2f);
        SCAN_CODES.put("]", (byte) 0x30);
        SCAN_CODES.put("}", (byte) 0x30);
        SCAN_CODES.put("\\", (byte) 0x31);
        SCAN_CODES.put("|", (byte) 0x31);
        SCAN_CODES.put(";", (byte) 0x33);
        SCAN_CODES.put(":", (byte) 0x33);
        SCAN_CODES.put("'", (byte) 0x34);
        SCAN_CODES.put("\"", (byte) 0x34);
        SCAN_CODES.put("`", (byte) 0x35);
        SCAN_CODES.put("~", (byte) 0x35);
        SCAN_CODES.put(",", (byte) 0x36);
        SCAN_CODES.put("<", (byte) 0x36);
        SCAN_CODES.put(".", (byte) 0x37);
        SCAN_CODES.put(">", (byte) 0x37);
        SCAN_CODES.put("/", (byte) 0x38);
        SCAN_CODES.put("?", (byte) 0x38);

        // Function keys F1 - F12
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

        // Navigation cluster
        SCAN_CODES.put("print_screen", (byte) 0x46);
        SCAN_CODES.put("prtsc", (byte) 0x46);
        SCAN_CODES.put("scroll_lock", (byte) 0x47);
        SCAN_CODES.put("pause", (byte) 0x48);
        SCAN_CODES.put("insert", (byte) 0x49);
        SCAN_CODES.put("home", (byte) 0x4a);
        SCAN_CODES.put("page_up", (byte) 0x4b);
        SCAN_CODES.put("pageup", (byte) 0x4b);
        SCAN_CODES.put("delete", (byte) 0x4c);
        SCAN_CODES.put("del", (byte) 0x4c);
        SCAN_CODES.put("end", (byte) 0x4d);
        SCAN_CODES.put("page_down", (byte) 0x4e);
        SCAN_CODES.put("pagedown", (byte) 0x4e);
        SCAN_CODES.put("right", (byte) 0x4f);
        SCAN_CODES.put("left", (byte) 0x50);
        SCAN_CODES.put("down", (byte) 0x51);
        SCAN_CODES.put("up", (byte) 0x52);

        // Numpad
        SCAN_CODES.put("num_lock", (byte) 0x53);
        SCAN_CODES.put("kp_divide", (byte) 0x54);
        SCAN_CODES.put("kp_multiply", (byte) 0x55);
        SCAN_CODES.put("kp_subtract", (byte) 0x56);
        SCAN_CODES.put("kp_add", (byte) 0x57);
        SCAN_CODES.put("kp_enter", (byte) 0x58);
        for (int i = 1; i <= 9; i++) {
            SCAN_CODES.put("kp_" + i, (byte) (0x59 + i - 1));
            SCAN_CODES.put("numpad_" + i, (byte) (0x59 + i - 1));
        }
        SCAN_CODES.put("kp_0", (byte) 0x62);
        SCAN_CODES.put("numpad_0", (byte) 0x62);
        SCAN_CODES.put("kp_decimal", (byte) 0x63);
        SCAN_CODES.put("kp_dot", (byte) 0x63);
    }

    private final Context context;
    private BluetoothHidDevice hidDevice;
    private BluetoothDevice connectedHostDevice;
    private boolean isRegistered = false;
    private byte currentModifierByte = 0;
    private byte currentMouseButton = 0;

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

    public boolean isConnected() {
        return connectedHostDevice != null;
    }

    public String getConnectedDeviceName() {
        if (connectedHostDevice != null) {
            try {
                return connectedHostDevice.getName();
            } catch (SecurityException e) {
                return "PC Host";
            }
        }
        return null;
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
                    statusListener.onStatusChanged(registered ? "Bluetooth HID Aktif. Siap dipasangkan dari PC/Laptop." : "Pendaftaran HID gagal", false);
                }
            }

            @Override
            public void onConnectionStateChanged(BluetoothDevice device, int state) {
                if (state == BluetoothProfile.STATE_CONNECTED) {
                    connectedHostDevice = device;
                    String devName = "PC";
                    try {
                        devName = device.getName();
                    } catch (SecurityException ignored) {}
                    if (statusListener != null) {
                        statusListener.onStatusChanged("Terhubung ke " + devName, true);
                    }
                } else if (state == BluetoothProfile.STATE_DISCONNECTED) {
                    connectedHostDevice = null;
                    currentModifierByte = 0;
                    currentMouseButton = 0;
                    if (statusListener != null) {
                        statusListener.onStatusChanged("Terputus dari PC", false);
                    }
                }
            }
        };

        hidDevice.registerApp(sdp, null, null, Executors.newSingleThreadExecutor(), callback);
    }

    private byte computeModifier(boolean shift, boolean ctrl, boolean alt, boolean cmd) {
        byte mod = 0;
        if (ctrl) mod |= 0x01;
        if (shift) mod |= 0x02;
        if (alt) mod |= 0x04;
        if (cmd) mod |= 0x08;
        return mod;
    }

    @SuppressLint("MissingPermission")
    public void sendKey(String key, boolean shift, boolean ctrl, boolean alt, boolean cmd) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        String lowerKey = (key != null) ? key.toLowerCase().trim() : "";
        byte modifierByte = computeModifier(shift, ctrl, alt, cmd);

        // Auto-shift for uppercase or shifted symbols
        if (key != null && key.length() == 1) {
            char ch = key.charAt(0);
            if (Character.isUpperCase(ch) || "~!@#$%^&*()_+{}|:\"<>?".indexOf(ch) >= 0) {
                modifierByte |= 0x02;
            }
        }

        byte scanCode = SCAN_CODES.containsKey(lowerKey) ? SCAN_CODES.get(lowerKey) : 0;
        if (scanCode == 0) return;

        // Press report
        byte[] pressReport = new byte[]{modifierByte, 0, scanCode, 0, 0, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 1, pressReport);

        // Micro delay agar host OS membaca scan code
        try {
            Thread.sleep(12);
        } catch (InterruptedException ignored) {}

        // Release report (pertahankan modifier jika ada)
        byte[] releaseReport = new byte[]{currentModifierByte, 0, 0, 0, 0, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 1, releaseReport);
    }

    @SuppressLint("MissingPermission")
    public void sendKeyDown(String key, boolean shift, boolean ctrl, boolean alt, boolean cmd) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        String lowerKey = (key != null) ? key.toLowerCase().trim() : "";

        // Check if key is modifier itself
        if (lowerKey.equals("ctrl") || lowerKey.equals("control") || lowerKey.equals("ctrl_l")) {
            currentModifierByte |= 0x01;
        } else if (lowerKey.equals("shift") || lowerKey.equals("shift_l")) {
            currentModifierByte |= 0x02;
        } else if (lowerKey.equals("alt") || lowerKey.equals("alt_l")) {
            currentModifierByte |= 0x04;
        } else if (lowerKey.equals("win") || lowerKey.equals("cmd") || lowerKey.equals("super") || lowerKey.equals("meta")) {
            currentModifierByte |= 0x08;
        }

        byte mod = (byte) (currentModifierByte | computeModifier(shift, ctrl, alt, cmd));
        byte scanCode = SCAN_CODES.containsKey(lowerKey) ? SCAN_CODES.get(lowerKey) : 0;

        byte[] pressReport = new byte[]{mod, 0, scanCode, 0, 0, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 1, pressReport);
    }

    @SuppressLint("MissingPermission")
    public void sendKeyUp(String key, boolean shift, boolean ctrl, boolean alt, boolean cmd) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        String lowerKey = (key != null) ? key.toLowerCase().trim() : "";

        // Release modifier if key is modifier
        if (lowerKey.equals("ctrl") || lowerKey.equals("control") || lowerKey.equals("ctrl_l")) {
            currentModifierByte &= ~0x01;
        } else if (lowerKey.equals("shift") || lowerKey.equals("shift_l")) {
            currentModifierByte &= ~0x02;
        } else if (lowerKey.equals("alt") || lowerKey.equals("alt_l")) {
            currentModifierByte &= ~0x04;
        } else if (lowerKey.equals("win") || lowerKey.equals("cmd") || lowerKey.equals("super") || lowerKey.equals("meta")) {
            currentModifierByte &= ~0x08;
        }

        byte mod = (byte) (currentModifierByte | computeModifier(shift, ctrl, alt, cmd));
        byte[] releaseReport = new byte[]{mod, 0, 0, 0, 0, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 1, releaseReport);
    }

    @SuppressLint("MissingPermission")
    public void sendMouseMove(int dx, int dy, int button) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        byte btnByte = (button >= 0) ? (byte) (button & 0x07) : currentMouseButton;
        byte bX = (byte) Math.max(-127, Math.min(127, dx));
        byte bY = (byte) Math.max(-127, Math.min(127, dy));

        byte[] mouseReport = new byte[]{btnByte, bX, bY, 0};
        hidDevice.sendReport(connectedHostDevice, 2, mouseReport);
    }

    @SuppressLint("MissingPermission")
    public void sendMouseClick(int button) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        byte btnByte = (byte) (button & 0x07);
        // Press
        byte[] pressReport = new byte[]{btnByte, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 2, pressReport);

        try {
            Thread.sleep(12);
        } catch (InterruptedException ignored) {}

        // Release
        byte[] releaseReport = new byte[]{0, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 2, releaseReport);
    }

    @SuppressLint("MissingPermission")
    public void sendMouseDown(int button) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        currentMouseButton |= (byte) (button & 0x07);
        byte[] pressReport = new byte[]{currentMouseButton, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 2, pressReport);
    }

    @SuppressLint("MissingPermission")
    public void sendMouseUp(int button) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        currentMouseButton &= ~(byte) (button & 0x07);
        byte[] releaseReport = new byte[]{currentMouseButton, 0, 0, 0};
        hidDevice.sendReport(connectedHostDevice, 2, releaseReport);
    }

    @SuppressLint("MissingPermission")
    public void sendMouseScroll(int dy) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.P || hidDevice == null || connectedHostDevice == null) {
            return;
        }

        byte scrollByte = (byte) Math.max(-127, Math.min(127, dy));
        byte[] scrollReport = new byte[]{currentMouseButton, 0, 0, scrollByte};
        hidDevice.sendReport(connectedHostDevice, 2, scrollReport);
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
