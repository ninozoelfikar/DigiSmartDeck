package com.digikeyboard.remote;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;
import org.json.JSONObject;

import java.net.URI;

public class WebSocketManager {

    private static final String TAG = "DigiWS";

    public interface Listener {
        void onConnected();
        void onDisconnected(String reason);
        void onPingUpdated(long latencyMs);
        void onCapsState(boolean isCapsOn);
    }

    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private WebSocketClient client;
    private Listener listener;
    private String currentServerUrl;
    private boolean isIntentionalClose = false;
    private final Handler reconnectHandler = new Handler(Looper.getMainLooper());
    private final Handler pingHandler = new Handler(Looper.getMainLooper());

    private final Runnable pingRunnable = new Runnable() {
        @Override
        public void run() {
            if (isConnected()) {
                try {
                    JSONObject ping = new JSONObject();
                    ping.put("type", "ping");
                    ping.put("t", System.currentTimeMillis());
                    send(ping.toString());
                } catch (Exception ignored) {}
                pingHandler.postDelayed(this, 2000);
            }
        }
    };

    private final Runnable reconnectRunnable = new Runnable() {
        @Override
        public void run() {
            if (!isIntentionalClose && !isConnected() && currentServerUrl != null) {
                Log.d(TAG, "Mencoba rekoneksi ke: " + currentServerUrl);
                connect(currentServerUrl);
            }
        }
    };

    public void setListener(Listener listener) {
        this.listener = listener;
    }

    public synchronized void connect(String httpOrWsUrl) {
        disconnect();
        isIntentionalClose = false;

        String wsUrl = httpOrWsUrl.trim();
        if (wsUrl.startsWith("http://")) {
            wsUrl = "ws://" + wsUrl.substring(7);
        } else if (wsUrl.startsWith("https://")) {
            wsUrl = "wss://" + wsUrl.substring(8);
        } else if (!wsUrl.startsWith("ws://") && !wsUrl.startsWith("wss://")) {
            wsUrl = "ws://" + wsUrl;
        }

        if (!wsUrl.endsWith("/ws")) {
            if (wsUrl.endsWith("/")) {
                wsUrl += "ws";
            } else {
                wsUrl += "/ws";
            }
        }

        currentServerUrl = wsUrl;
        Log.d(TAG, "Menghubungkan ke WebSocket: " + currentServerUrl);

        try {
            URI uri = URI.create(currentServerUrl);
            client = new WebSocketClient(uri) {
                @Override
                public void onOpen(ServerHandshake handshakedata) {
                    Log.i(TAG, "WebSocket Terhubung!");
                    mainHandler.post(() -> {
                        if (listener != null) listener.onConnected();
                        pingHandler.removeCallbacks(pingRunnable);
                        pingHandler.post(pingRunnable);
                    });
                }

                @Override
                public void onMessage(String message) {
                    try {
                        JSONObject json = new JSONObject(message);
                        String type = json.optString("type");

                        if ("pong".equals(type)) {
                            long sentTime = json.optLong("t", 0);
                            if (sentTime > 0) {
                                long latency = Math.max(1, System.currentTimeMillis() - sentTime);
                                mainHandler.post(() -> {
                                    if (listener != null) listener.onPingUpdated(latency);
                                });
                            }
                            if (json.has("caps_lock")) {
                                boolean caps = json.optBoolean("caps_lock", false);
                                mainHandler.post(() -> {
                                    if (listener != null) listener.onCapsState(caps);
                                });
                            }
                        } else if ("caps_state".equals(type)) {
                            boolean caps = json.optBoolean("caps_lock", false);
                            mainHandler.post(() -> {
                                if (listener != null) listener.onCapsState(caps);
                            });
                        }
                    } catch (Exception e) {
                        Log.e(TAG, "Gagal memproses pesan WS: " + e.getMessage());
                    }
                }

                @Override
                public void onClose(int code, String reason, boolean remote) {
                    Log.w(TAG, "WebSocket Ditutup: " + reason + " (code: " + code + ")");
                    mainHandler.post(() -> {
                        pingHandler.removeCallbacks(pingRunnable);
                        if (listener != null) listener.onDisconnected(reason);
                        if (!isIntentionalClose) {
                            reconnectHandler.removeCallbacks(reconnectRunnable);
                            reconnectHandler.postDelayed(reconnectRunnable, 2500);
                        }
                    });
                }

                @Override
                public void onError(Exception ex) {
                    Log.e(TAG, "WebSocket Error: " + ex.getMessage());
                }
            };

            client.setConnectionLostTimeout(6);
            client.connect();
        } catch (Exception e) {
            Log.e(TAG, "Gagal inisialisasi WebSocket: " + e.getMessage());
            mainHandler.post(() -> {
                if (listener != null) listener.onDisconnected(e.getMessage());
                if (!isIntentionalClose) {
                    reconnectHandler.removeCallbacks(reconnectRunnable);
                    reconnectHandler.postDelayed(reconnectRunnable, 3000);
                }
            });
        }
    }

    public synchronized void send(String payload) {
        if (isConnected()) {
            try {
                client.send(payload);
            } catch (Exception e) {
                Log.e(TAG, "Gagal mengirim data WS: " + e.getMessage());
            }
        }
    }

    public synchronized boolean isConnected() {
        return client != null && client.isOpen();
    }

    public synchronized void disconnect() {
        isIntentionalClose = true;
        reconnectHandler.removeCallbacks(reconnectRunnable);
        pingHandler.removeCallbacks(pingRunnable);
        if (client != null) {
            try {
                client.close();
            } catch (Exception ignored) {}
            client = null;
        }
    }
}
