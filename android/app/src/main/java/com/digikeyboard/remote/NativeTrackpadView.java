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

public class NativeTrackpadView extends View {

    public interface Listener {
        void onMouseMove(int dx, int dy);
        void onMouseClick(String button);
        void onMouseScroll(int dy);
    }

    private Listener listener;
    private float sensitivity = 1.35f;

    private final Paint bgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint borderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint textPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint touchPaint = new Paint(Paint.ANTI_ALIAS_FLAG);

    private final RectF bounds = new RectF();

    // Multi-touch tracking
    private float lastX1, lastY1;
    private float lastX2, lastY2;
    private long downTime;
    private float downX1, downY1;
    private boolean isMultiTouch = false;
    private boolean hasMovedSignificantly = false;

    // Active touch points for visual glow
    private float activeX = -1, activeY = -1;

    public NativeTrackpadView(Context context) {
        super(context);
        init();
    }

    public NativeTrackpadView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    public NativeTrackpadView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init();
    }

    private void init() {
        bgPaint.setColor(Color.parseColor("#12161f"));
        bgPaint.setStyle(Paint.Style.FILL);

        borderPaint.setColor(Color.parseColor("#2a3240"));
        borderPaint.setStyle(Paint.Style.STROKE);
        borderPaint.setStrokeWidth(2f);

        textPaint.setColor(Color.parseColor("#505a69"));
        textPaint.setTextSize(26f);
        textPaint.setTextAlign(Paint.Align.CENTER);
        textPaint.setFakeBoldText(true);

        touchPaint.setColor(Color.parseColor("#388bfd"));
        touchPaint.setStyle(Paint.Style.FILL);
        touchPaint.setAlpha(60);
    }

    public void setListener(Listener listener) {
        this.listener = listener;
    }

    public void setSensitivity(float sensitivity) {
        this.sensitivity = sensitivity;
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        bounds.set(4, 4, w - 4, h - 4);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // Draw trackpad surface
        canvas.drawRoundRect(bounds, 16f, 16f, bgPaint);
        canvas.drawRoundRect(bounds, 16f, 16f, borderPaint);

        // Watermark instructions
        float centerX = getWidth() / 2f;
        float centerY = getHeight() / 2f + 8f;
        canvas.drawText("🖱️ Trackpad Laptop (1-Jari Gerak/Klik • 2-Jari Scroll/Klik Kanan)", centerX, centerY, textPaint);

        // Visual touch feedback
        if (activeX >= 0 && activeY >= 0) {
            canvas.drawCircle(activeX, activeY, 40f, touchPaint);
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        int action = event.getActionMasked();
        int pointerCount = event.getPointerCount();

        switch (action) {
            case MotionEvent.ACTION_DOWN:
                downTime = System.currentTimeMillis();
                downX1 = lastX1 = event.getX(0);
                downY1 = lastY1 = event.getY(0);
                activeX = downX1;
                activeY = downY1;
                isMultiTouch = false;
                hasMovedSignificantly = false;
                invalidate();
                return true;

            case MotionEvent.ACTION_POINTER_DOWN:
                isMultiTouch = true;
                if (pointerCount >= 2) {
                    lastX2 = event.getX(1);
                    lastY2 = event.getY(1);
                }
                invalidate();
                return true;

            case MotionEvent.ACTION_MOVE:
                activeX = event.getX(0);
                activeY = event.getY(0);

                if (pointerCount == 1 && !isMultiTouch) {
                    float x = event.getX(0);
                    float y = event.getY(0);
                    float dx = (x - lastX1) * sensitivity;
                    float dy = (y - lastY1) * sensitivity;

                    if (Math.abs(x - downX1) > 8 || Math.abs(y - downY1) > 8) {
                        hasMovedSignificantly = true;
                    }

                    if (listener != null && (Math.abs(dx) >= 0.5f || Math.abs(dy) >= 0.5f)) {
                        listener.onMouseMove(Math.round(dx), Math.round(dy));
                    }
                    lastX1 = x;
                    lastY1 = y;
                } else if (pointerCount >= 2) {
                    float y1 = event.getY(0);
                    float y2 = event.getY(1);
                    float avgDy = ((y1 - lastY1) + (y2 - lastY2)) / 2f;

                    if (Math.abs(avgDy) > 6) {
                        hasMovedSignificantly = true;
                        if (listener != null) {
                            listener.onMouseScroll(Math.round(-avgDy * 1.5f));
                        }
                    }
                    lastX1 = event.getX(0);
                    lastY1 = y1;
                    lastX2 = event.getX(1);
                    lastY2 = y2;
                }
                invalidate();
                return true;

            case MotionEvent.ACTION_POINTER_UP:
                if (pointerCount == 2 && !hasMovedSignificantly) {
                    long duration = System.currentTimeMillis() - downTime;
                    if (duration < 300) {
                        // 2-finger tap = Right Click
                        performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
                        if (listener != null) listener.onMouseClick("right");
                    }
                }
                invalidate();
                return true;

            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                activeX = -1;
                activeY = -1;
                long tapDuration = System.currentTimeMillis() - downTime;

                if (!isMultiTouch && !hasMovedSignificantly && tapDuration < 250) {
                    // 1-finger tap = Left Click
                    performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
                    if (listener != null) listener.onMouseClick("left");
                }

                invalidate();
                return true;
        }
        return super.onTouchEvent(event);
    }
}
