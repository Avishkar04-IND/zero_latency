# Accessible Mobile Application — Smart Medicine Platform

> Primary Owner: **Member 4**

---

## Overview

The `mobile/` directory contains the Flutter Android application specifically designed for visually impaired and elderly users. It features screen-reader optimizations (TTS/STT), gesture navigation, haptic feedback cues, camera DataMatrix/QR code scanning, and speech integration with the shared web voice assistant.

---

## Directory Structure

```text
mobile/
├── lib/
│   ├── core/
│   │   ├── config/          # App constants & environment config
│   │   ├── constants/       # Global styling & layout tokens
│   │   ├── theme/           # High-contrast accessible theme
│   │   ├── accessibility/   # Screen reader, font sizing, semantics helpers
│   │   └── utils/           # General mobile utility functions
│   ├── models/              # Local data models
│   ├── services/
│   │   ├── api/             # Backend API client integration
│   │   ├── scanner/         # Mobile camera QR/DataMatrix scanner logic
│   │   ├── tts/             # Text-To-Speech engine service
│   │   ├── stt/             # Speech-To-Text voice input service
│   │   └── haptics/         # Vibration & tactile feedback patterns
│   ├── features/
│   │   ├── home/            # Home dashboard feature
│   │   ├── scanner/         # Audio-guided scanner UI
│   │   ├── medicine/        # Medicine info voice-reader screen
│   │   ├── history/         # Verification history & logs
│   │   ├── assistant/       # Voice assistant interface
│   │   └── settings/        # Accessibility settings UI
│   ├── widgets/             # Reusable accessible Flutter widgets
│   └── main.dart            # Flutter application entrypoint
├── test/                    # Widget and unit tests
├── android/                 # Android native configuration
├── assets/
│   ├── audio/               # Audio cues & sound feedback
│   └── images/              # High contrast icons & assets
├── pubspec.yaml             # Flutter pubspec dependencies manifest
└── README.md
```

---

## Responsibilities

* Flutter Android mobile application for accessibility
* Screen-reader optimization for visually impaired users
* DataMatrix and QR code camera scanning with voice cues
* Text-to-speech (TTS) medicine information reading
* Speech-to-text (STT) voice command navigation
* Haptic feedback (vibration patterns) for non-visual interaction
* Gesture-based simplified touch interface
* Consuming the shared Voice Assistant API

---

## Local Setup

1. Verify Flutter installation (`flutter doctor`).
2. Install pub packages:
   ```bash
   cd mobile
   flutter pub get
   ```
3. Run app on an Android emulator or attached physical device:
   ```bash
   flutter run
   ```
