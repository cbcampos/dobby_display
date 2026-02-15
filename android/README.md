# Dobby Display Android App

A simple Android WebView app that displays the Dobby Dashboard with audio autoplay enabled.

## Key Features
- Loads `http://100.105.30.20:5000` in a fullscreen WebView
- Audio autoplay enabled (`MediaPlaybackRequiresUserGesture=false`)
- Screen stays on (prevents sleep)
- Back button returns to dashboard instead of closing app

## Build

### Prerequisites
- Android Studio OR
- Command line with Gradle + Android SDK

### Build from command line
```bash
cd android/DobbyDisplay
./gradlew assembleDebug
```

### Output
APK will be at: `app/build/outputs/apk/debug/app-debug.apk`

## Install on Duet
1. Transfer the APK to the Duet (via USB, Google Drive, or network)
2. Enable "Install from unknown sources" in Chrome OS settings
3. Open the APK and install
4. Launch "Dobby Display" app

## Configuration
To change the display URL, edit:
`app/src/main/java/com/dobby/display/MainActivity.java`

Change this line:
```java
webView.loadUrl("http://100.105.30.20:5000");
```
to your desired URL.
