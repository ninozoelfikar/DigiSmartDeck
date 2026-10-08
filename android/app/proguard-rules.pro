# ProGuard / R8 Obfuscation & Anti-Reverse Engineering Rules for DigiSmartDeck
-repackageclasses ''
-allowaccessmodification
-overloadaggressively

# Keep WebAppInterface methods accessible via JavaScript in WebView
-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# Keep MainActivity and Android components
-keep class com.digikeyboard.remote.MainActivity { *; }
-keep class com.digikeyboard.remote.BluetoothHidHelper { *; }
-keepclassmembers class com.digikeyboard.remote.MainActivity$WebAppInterface {
    public *;
}
