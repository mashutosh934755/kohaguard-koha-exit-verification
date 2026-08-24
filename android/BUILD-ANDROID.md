# Building the KohaGuard Android App

KohaGuard can be wrapped with Capacitor for Android. The web backend remains the source of truth.

## Prerequisites
- Node.js 22 (tested)
- npm/npx
- JDK 21 for current Capacitor Android builds
- Android SDK platform 36
- Android build-tools 35/36

## Create the project
```bash
mkdir kohaguard-android && cd kohaguard-android
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init "KohaGuard" "org.example.kohaguard" --web-dir=www
mkdir -p www
# Put the bundled KohaGuard frontend in www/
npx cap add android
npx cap sync android
```

## Camera permission
Ensure `android/app/src/main/AndroidManifest.xml` contains:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-feature android:name="android.hardware.camera" android:required="false" />
```

## Build
```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

npx cap sync android
cd android
./gradlew --stop || true
./gradlew --no-daemon clean assembleDebug
```

APK:
```text
android/app/build/outputs/apk/debug/app-debug.apk
```

## Production requirements
Do not ship a Play Store app that depends on cleartext HTTP or disabled TLS validation. Use a public/trusted or institutionally trusted HTTPS API endpoint, restrict CORS, protect analytics/admin endpoints, sign the release, and complete Android/Play privacy and data-safety declarations.

For Play Store distribution, build and sign an Android App Bundle (`.aab`) using your institution's secure signing process.
