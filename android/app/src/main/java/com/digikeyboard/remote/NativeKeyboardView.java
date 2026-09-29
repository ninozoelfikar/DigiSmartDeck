package com.digikeyboard.remote;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.HapticFeedbackConstants;
import android.view.MotionEvent;
import android.view.View;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class NativeKeyboardView extends View {

    public interface KeyEventListener {
        void onKeyAction(String type, String key, String character, JSONObject modifiers);
    }

    public static class KeyDef {
        public String keyId;
        public String mainLabel;
        public String shiftLabel;
        public float weight;
        public boolean isSpecial;
        public boolean isEnter;
        public boolean isSpace;
        public RectF bounds = new RectF();
        public boolean isPressed = false;
        public boolean isLatched = false;

        public KeyDef(String keyId, String main, String shift, float weight) {
            this(keyId, main, shift, weight, false, false, false);
        }

        public KeyDef(String keyId, String main, String shift, float weight, boolean isSpecial, boolean isEnter, boolean isSpace) {
            this.keyId = keyId;
            this.mainLabel = main;
            this.shiftLabel = shift;
            this.weight = weight;
            this.isSpecial = isSpecial;
            this.isEnter = isEnter;
            this.isSpace = isSpace;
        }
    }

    private final List<List<KeyDef>> rows = new ArrayList<>();
    private final Map<Integer, KeyDef> activePointers = new HashMap<>();

    private KeyEventListener listener;
    private boolean persistentLock = true;
    private boolean hapticEnabled = true;

    // Modifiers state
    private boolean modShift = false;
    private boolean modCtrl = false;
    private boolean modAlt = false;
    private boolean modCmd = false;
    private boolean modCaps = false;

    // Paints
    private final Paint keyBgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint keySpecialBgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint keyEnterBgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint keyPressedBgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint keyLatchedBgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint keyBorderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint keyLatchedBorderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint mainTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint subTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    public NativeKeyboardView(Context context) {
        super(context);
        init();
    }

    public NativeKeyboardView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public NativeKeyboardView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        keyBgPaint.setColor(Color.parseColor("#21262d"));
        keySpecialBgPaint.setColor(Color.parseColor("#1b2028"));
        keyEnterBgPaint.setColor(Color.parseColor("#1f4068"));
        keyPressedBgPaint.setColor(Color.parseColor("#1f6feb"));
        keyLatchedBgPaint.setColor(Color.parseColor("#238636"));

        keyBorderPaint.setColor(Color.parseColor("#30363d"));
        keyBorderPaint.setStyle(Paint.Style.STROKE);
        keyBorderPaint.setStrokeWidth(2f);

        keyLatchedBorderPaint.setColor(Color.parseColor("#3fb950"));
        keyLatchedBorderPaint.setStyle(Paint.Style.STROKE);
        keyLatchedBorderPaint.setStrokeWidth(3f);

        mainTextPaint.setColor(Color.parseColor("#f0f6fc"));
        mainTextPaint.setTextAlign(Paint.Align.CENTER);
        mainTextPaint.setFakeBoldText(true);

        subTextPaint.setColor(Color.parseColor("#58a6ff"));
        subTextPaint.setTextAlign(Paint.Align.LEFT);

        buildLayout();
    }

    private void buildLayout() {
        rows.clear();

        // ── ROW 1: Esc, ~, 1-0, -, =, Backspace ──
        List<KeyDef> r1 = new ArrayList<>();
        r1.add(new KeyDef("esc", "Esc", null, 1.1f, true, false, false));
        r1.add(new KeyDef("grave", "`", "~", 1.0f));
        r1.add(new KeyDef("1", "1", "!", 1.0f));
        r1.add(new KeyDef("2", "2", "@", 1.0f));
        r1.add(new KeyDef("3", "3", "#", 1.0f));
        r1.add(new KeyDef("4", "4", "$", 1.0f));
        r1.add(new KeyDef("5", "5", "%", 1.0f));
        r1.add(new KeyDef("6", "6", "^", 1.0f));
        r1.add(new KeyDef("7", "7", "&", 1.0f));
        r1.add(new KeyDef("8", "8", "*", 1.0f));
        r1.add(new KeyDef("9", "9", "(", 1.0f));
        r1.add(new KeyDef("0", "0", ")", 1.0f));
        r1.add(new KeyDef("minus", "-", "_", 1.0f));
        r1.add(new KeyDef("equal", "=", "+", 1.0f));
        r1.add(new KeyDef("backspace", "⌫", null, 1.7f, true, false, false));
        rows.add(r1);

        // ── ROW 2: Tab, QWERTY, [, ], \ ──
        List<KeyDef> r2 = new ArrayList<>();
        r2.add(new KeyDef("tab", "Tab ⇥", null, 1.4f, true, false, false));
        r2.add(new KeyDef("q", "Q", null, 1.0f));
        r2.add(new KeyDef("w", "W", null, 1.0f));
        r2.add(new KeyDef("e", "E", null, 1.0f));
        r2.add(new KeyDef("r", "R", null, 1.0f));
        r2.add(new KeyDef("t", "T", null, 1.0f));
        r2.add(new KeyDef("y", "Y", null, 1.0f));
        r2.add(new KeyDef("u", "U", null, 1.0f));
        r2.add(new KeyDef("i", "I", null, 1.0f));
        r2.add(new KeyDef("o", "O", null, 1.0f));
        r2.add(new KeyDef("p", "P", null, 1.0f));
        r2.add(new KeyDef("bracketleft", "[", "{", 1.0f));
        r2.add(new KeyDef("bracketright", "]", "}", 1.0f));
        r2.add(new KeyDef("backslash", "\\", "|", 1.2f));
        rows.add(r2);

        // ── ROW 3: Caps, ASDFGHJKL, ;, ', Enter ──
        List<KeyDef> r3 = new ArrayList<>();
        r3.add(new KeyDef("caps_lock", "Caps ⇪", null, 1.7f, true, false, false));
        r3.add(new KeyDef("a", "A", null, 1.0f));
        r3.add(new KeyDef("s", "S", null, 1.0f));
        r3.add(new KeyDef("d", "D", null, 1.0f));
        r3.add(new KeyDef("f", "F", null, 1.0f));
        r3.add(new KeyDef("g", "G", null, 1.0f));
        r3.add(new KeyDef("h", "H", null, 1.0f));
        r3.add(new KeyDef("j", "J", null, 1.0f));
        r3.add(new KeyDef("k", "K", null, 1.0f));
        r3.add(new KeyDef("l", "L", null, 1.0f));
        r3.add(new KeyDef("semicolon", ";", ":", 1.0f));
        r3.add(new KeyDef("apostrophe", "'", "\"", 1.0f));
        r3.add(new KeyDef("enter", "Enter ↵", null, 2.0f, false, true, false));
        rows.add(r3);

        // ── ROW 4: Shift, ZXCVBNM, ,, ., /, ▲, Shift ──
        List<KeyDef> r4 = new ArrayList<>();
        r4.add(new KeyDef("shift", "Shift ⇧", null, 2.1f, true, false, false));
        r4.add(new KeyDef("z", "Z", null, 1.0f));
        r4.add(new KeyDef("x", "X", null, 1.0f));
        r4.add(new KeyDef("c", "C", null, 1.0f));
        r4.add(new KeyDef("v", "V", null, 1.0f));
        r4.add(new KeyDef("b", "B", null, 1.0f));
        r4.add(new KeyDef("n", "N", null, 1.0f));
        r4.add(new KeyDef("m", "M", null, 1.0f));
        r4.add(new KeyDef("comma", ",", "<", 1.0f));
        r4.add(new KeyDef("dot", ".", ">", 1.0f));
        r4.add(new KeyDef("slash", "/", "?", 1.0f));
        r4.add(new KeyDef("up", "▲", null, 1.0f, true, false, false));
        r4.add(new KeyDef("shift", "Shift ⇧", null, 1.5f, true, false, false));
        rows.add(r4);

        // ── ROW 5: Ctrl, Win, Alt, Space, Alt, ◀, ▼, ▶ ──
        List<KeyDef> r5 = new ArrayList<>();
        r5.add(new KeyDef("ctrl", "Ctrl", null, 1.3f, true, false, false));
        r5.add(new KeyDef("win", "⊞ Win", null, 1.2f, true, false, false));
        r5.add(new KeyDef("alt", "Alt", null, 1.2f, true, false, false));
        r5.add(new KeyDef("space", "Space", null, 6.2f, false, false, true));
        r5.add(new KeyDef("alt", "Alt", null, 1.2f, true, false, false));
        r5.add(new KeyDef("left", "◀", null, 1.0f, true, false, false));
        r5.add(new KeyDef("down", "▼", null, 1.0f, true, false, false));
        r5.add(new KeyDef("right", "▶", null, 1.0f, true, false, false));
        rows.add(r5);
    }

    public void setListener(KeyEventListener listener) {
        this.listener = listener;
    }

    public void setPersistentLock(boolean persistentLock) {
        this.persistentLock = persistentLock;
    }

    public void setHapticEnabled(boolean hapticEnabled) {
        this.hapticEnabled = hapticEnabled;
    }

    public void setHostCapsState(boolean isCapsOn) {
        this.modCaps = isCapsOn;
        for (List<KeyDef> r : rows) {
            for (KeyDef k : r) {
                if ("caps_lock".equals(k.keyId)) {
                    k.isLatched = isCapsOn;
                }
            }
        }
        invalidate();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        calculateKeyBounds(w, h);
    }

    private void calculateKeyBounds(int viewW, int viewH) {
        if (rows.isEmpty() || viewW <= 0 || viewH <= 0) return;

        float gap = 4f;
        float paddingX = 6f;
        float paddingY = 4f;

        float availableH = viewH - (paddingY * 2) - (gap * (rows.size() - 1));
        float rowH = availableH / rows.size();

        float curY = paddingY;
        for (List<KeyDef> row : rows) {
            float totalWeight = 0;
            for (KeyDef k : row) totalWeight += k.weight;

            float availableW = viewW - (paddingX * 2) - (gap * (row.size() - 1));
            float unitW = availableW / totalWeight;

            float curX = paddingX;
            for (KeyDef k : row) {
                float kw = k.weight * unitW;
                k.bounds.set(curX, curY, curX + kw, curY + rowH);
                curX += kw + gap;
            }
            curY += rowH + gap;
        }

        // Adjust text size based on key dimensions
        mainTextPaint.setTextSize(rowH * 0.38f);
        subTextPaint.setTextSize(rowH * 0.22f);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        boolean isUpper = (modCaps ^ modShift);

        for (List<KeyDef> row : rows) {
            for (KeyDef k : row) {
                // Select background paint
                Paint bg = keyBgPaint;
                if (k.isPressed) {
                    bg = keyPressedBgPaint;
                } else if (k.isLatched) {
                    bg = keyLatchedBgPaint;
                } else if (k.isEnter) {
                    bg = keyEnterBgPaint;
                } else if (k.isSpecial) {
                    bg = keySpecialBgPaint;
                }

                // Draw keycap
                canvas.drawRoundRect(k.bounds, 8f, 8f, bg);
                canvas.drawRoundRect(k.bounds, 8f, 8f, k.isLatched ? keyLatchedBorderPaint : keyBorderPaint);

                // Draw shift sub-label if present
                if (k.shiftLabel != null) {
                    canvas.drawText(k.shiftLabel, k.bounds.left + 8f, k.bounds.top + (k.bounds.height() * 0.35f), subTextPaint);
                }

                // Determine display label
                String label = k.mainLabel;
                if (label.length() == 1 && Character.isLetter(label.charAt(0))) {
                    label = isUpper ? label.toUpperCase() : label.toLowerCase();
                } else if (modShift && k.shiftLabel != null) {
                    label = k.shiftLabel;
                }

                // Draw center label
                float textY = k.bounds.centerY() - ((mainTextPaint.descent() + mainTextPaint.ascent()) / 2f);
                if (k.shiftLabel != null) {
                    textY += k.bounds.height() * 0.12f;
                }
                canvas.drawText(label, k.bounds.centerX(), textY, mainTextPaint);
            }
        }
    }

    private KeyDef findKeyAt(float x, float y) {
        for (List<KeyDef> row : rows) {
            for (KeyDef k : row) {
                if (k.bounds.contains(x, y)) return k;
            }
        }
        return null;
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        int action = event.getActionMasked();
        int index = event.getActionIndex();
        int pointerId = event.getPointerId(index);

        switch (action) {
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_POINTER_DOWN: {
                KeyDef k = findKeyAt(event.getX(index), event.getY(index));
                if (k != null) {
                    activePointers.put(pointerId, k);
                    handleKeyDown(k);
                }
                invalidate();
                return true;
            }

            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_POINTER_UP: {
                KeyDef k = activePointers.remove(pointerId);
                if (k != null) {
                    handleKeyUp(k);
                }
                invalidate();
                return true;
            }

            case MotionEvent.ACTION_CANCEL: {
                for (KeyDef k : activePointers.values()) {
                    handleKeyUp(k);
                }
                activePointers.clear();
                invalidate();
                return true;
            }
        }
        return super.onTouchEvent(event);
    }

    private void handleKeyDown(KeyDef k) {
        k.isPressed = true;
        if (hapticEnabled) {
            performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
        }

        boolean isModifier = isModifierKey(k.keyId);

        if (isModifier) {
            if (persistentLock) {
                k.isLatched = !k.isLatched;
                syncModifierState(k.keyId, k.isLatched);
            } else {
                syncModifierState(k.keyId, true);
            }
            sendKeyEvent("keydown", k);
        } else {
            sendKeyEvent("keypress", k);
        }
    }

    private void handleKeyUp(KeyDef k) {
        k.isPressed = false;
        boolean isModifier = isModifierKey(k.keyId);

        if (isModifier) {
            if (!persistentLock) {
                syncModifierState(k.keyId, false);
                sendKeyEvent("keyup", k);
            }
        } else {
            sendKeyEvent("keyup", k);
            // If shift was temporary in 1-shot mode, release it
            if (!persistentLock && modShift) {
                modShift = false;
                syncAllModifierKeys();
            }
        }
    }

    private boolean isModifierKey(String keyId) {
        return "shift".equals(keyId) || "ctrl".equals(keyId) || "alt".equals(keyId) || "win".equals(keyId) || "caps_lock".equals(keyId);
    }

    private void syncModifierState(String keyId, boolean active) {
        switch (keyId) {
            case "shift": modShift = active; break;
            case "ctrl": modCtrl = active; break;
            case "alt": modAlt = active; break;
            case "win": modCmd = active; break;
            case "caps_lock": modCaps = active; break;
        }
        syncAllModifierKeys();
    }

    private void syncAllModifierKeys() {
        for (List<KeyDef> row : rows) {
            for (KeyDef k : row) {
                switch (k.keyId) {
                    case "shift": k.isLatched = modShift; break;
                    case "ctrl": k.isLatched = modCtrl; break;
                    case "alt": k.isLatched = modAlt; break;
                    case "win": k.isLatched = modCmd; break;
                    case "caps_lock": k.isLatched = modCaps; break;
                }
            }
        }
    }

    private void sendKeyEvent(String type, KeyDef k) {
        if (listener == null) return;

        try {
            JSONObject mods = new JSONObject();
            mods.put("shift", modShift);
            mods.put("ctrl", modCtrl);
            mods.put("alt", modAlt);
            mods.put("cmd", modCmd);
            mods.put("caps_lock", modCaps);

            String character = null;
            if ("keypress".equals(type)) {
                if (k.mainLabel.length() == 1 && Character.isLetter(k.mainLabel.charAt(0))) {
                    boolean isUpper = (modCaps ^ modShift);
                    character = isUpper ? k.mainLabel.toUpperCase() : k.mainLabel.toLowerCase();
                } else if (modShift && k.shiftLabel != null) {
                    character = k.shiftLabel;
                } else if ("space".equals(k.keyId)) {
                    character = " ";
                } else if (k.mainLabel.length() == 1) {
                    character = k.mainLabel;
                }
            }

            listener.onKeyAction(type, k.keyId, character, mods);
        } catch (Exception ignored) {}
    }

    public JSONObject getCurrentModifiers() {
        try {
            JSONObject mods = new JSONObject();
            mods.put("shift", modShift);
            mods.put("ctrl", modCtrl);
            mods.put("alt", modAlt);
            mods.put("cmd", modCmd);
            mods.put("caps_lock", modCaps);
            return mods;
        } catch (Exception e) {
            return new JSONObject();
        }
    }
}
