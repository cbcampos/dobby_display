#!/bin/bash
# Build script for Dobby Display Android App
# Run this on your Mac

set -e

echo "🍎 Setting up Android build environment..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Android SDK command line tools
echo "📦 Installing Android SDK..."
brew install android-commandlinetools

# Set up Android environment
export ANDROID_HOME=~/Library/Android/sdk
export ANDROID_SDK_ROOT=~/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Create SDK directory if it doesn't exist
mkdir -p "$ANDROID_HOME"

# Accept licenses
yes | sdkmanager --licenses 2>/dev/null || true

# Install required SDK components
echo "📦 Installing Android SDK components..."
echo "   SDK will be installed to: $ANDROID_HOME"
sdkmanager --sdk_root="$ANDROID_HOME" "platforms;android-34" "build-tools;34.0.0" "platform-tools"

# Clone the repo if not already
cd ~
rm -rf dobby_display
git clone https://github.com/cbcampos/dobby_display.git
cd dobby_display

# Create local.properties file with SDK path in the CORRECT location
echo "📝 Creating local.properties..."
echo "sdk.dir=$ANDROID_HOME" > android/DobbyDisplay/local.properties

# Clear ALL Gradle caches to avoid version conflicts
rm -rf ~/.gradle/caches/ 2>/dev/null || true
rm -rf ~/.gradle/wrapper/ 2>/dev/null || true

cd android/DobbyDisplay

# Build the APK
echo "🔨 Building APK..."
./gradlew assembleDebug

# Find the APK
APK=$(find . -name "*.apk" -type f | head -1)
echo ""
echo "✅ Build complete!"
echo "📱 APK location: $APK"
echo ""
echo "To install on your Duet:"
echo "1. Transfer the APK to the Duet"
echo "2. Enable 'Install from unknown sources' in Chrome OS settings"
echo "3. Open the APK and install"
echo "4. Launch 'Dobby Display'"
