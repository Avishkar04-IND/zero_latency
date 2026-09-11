import 'package:flutter/material.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../services/api/api_service.dart';
import '../../../shared/models/verification_model.dart';
import '../medicine/accessible_medicine_reader_screen.dart';
import '../gestures/accessible_gesture_controller.dart';

class AccessibleScannerScreen extends StatefulWidget {
  final TTSService ttsService;
  final ApiService apiService;

  const AccessibleScannerScreen({
    super.key,
    required this.ttsService,
    required this.apiService,
  });

  @override
  State<AccessibleScannerScreen> createState() => _AccessibleScannerScreenState();
}

class _AccessibleScannerScreenState extends State<AccessibleScannerScreen> {
  bool _isScanning = true;
  String _statusText = "Align medicine package code in center. Audio & haptics active.";

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      widget.ttsService.speak(
        "Camera Scanner active. Hold medicine package code in front of camera. Tap screen to trigger instant test scan.",
      );
      HapticsService.scanningTick();
    });
  }

  Future<void> _processScannedCode(String rawCode) async {
    if (!_isScanning) return;
    setState(() {
      _isScanning = false;
      _statusText = "Processing code... Please wait.";
    });

    HapticsService.capture();
    widget.ttsService.speak("Code captured. Verifying with server.");

    final result = await widget.apiService.verifyCode(rawCode);

    if (result.status == VerificationStatus.authentic) {
      await HapticsService.verifiedAuthentic();
    } else if (result.status == VerificationStatus.expired) {
      await HapticsService.expiredWarning();
    } else if (result.status == VerificationStatus.suspectedCounterfeit) {
      await HapticsService.suspiciousAlert();
    } else {
      await HapticsService.invalidCode();
    }

    if (!mounted) return;

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => AccessibleMedicineReaderScreen(
          verificationResult: result,
          ttsService: widget.ttsService,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onDoubleTapScan: () => _processScannedCode("DATAMATRIX-PAR650-BATCH101-SN9988"),
      onSwipeUpHome: () => Navigator.pop(context),
      onSwipeDownRepeat: () {
        widget.ttsService.speak(_statusText);
      },
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Voice-Guided Scanner'),
          backgroundColor: Colors.black,
        ),
        body: Column(
          children: [
            Expanded(
              flex: 3,
              child: Container(
                color: const Color(0xFF111111),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        width: 250,
                        height: 250,
                        decoration: BoxDecoration(
                          border: Border.all(color: const Color(0xFFFFD700), width: 6),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Icon(Icons.camera_alt, size: 80, color: Color(0xFFFFD700)),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'CAMERA VIEWPORT ACTIVE',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFFFFD700)),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Expanded(
              flex: 2,
              child: Container(
                padding: const EdgeInsets.all(20),
                color: Colors.black,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    Text(
                      _statusText,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 20, color: Colors.white, fontWeight: FontWeight.w600),
                    ),
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFFFD700),
                        foregroundColor: Colors.black,
                        minimumSize: const Size(double.infinity, 64),
                      ),
                      onPressed: () => _processScannedCode("DATAMATRIX-PAR650-BATCH101-SN9988"),
                      icon: const Icon(Icons.touch_app, size: 32),
                      label: const Text('SIMULATE CAMERA SCAN'),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
