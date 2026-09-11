import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/api/api_service.dart';
import '../../../services/history/history_service.dart';
import '../../../shared/widgets/accessible_buttons.dart';
import '../../../shared/widgets/accessible_states.dart';
import '../gestures/accessible_gesture_controller.dart';
import '../medicine/accessible_verification_result_screen.dart';
import '../navigation/accessibility_router.dart';
import 'scanner_controller.dart';
import 'scanner_state.dart';
import 'scanner_overlay.dart';

class AccessibleScannerScreen extends StatefulWidget {
  final TTSService ttsService;
  final ApiService apiService;
  final HistoryService? historyService;

  const AccessibleScannerScreen({
    super.key,
    required this.ttsService,
    required this.apiService,
    this.historyService,
  });

  @override
  State<AccessibleScannerScreen> createState() => _AccessibleScannerScreenState();
}

class _AccessibleScannerScreenState extends State<AccessibleScannerScreen> {
  late ScannerController _controller;
  MobileScannerController? _mobileScannerController;

  @override
  void initState() {
    super.initState();
    _controller = ScannerController(
      ttsService: widget.ttsService,
      apiService: widget.apiService,
      historyService: widget.historyService,
    );

    _mobileScannerController = MobileScannerController(
      formats: const [
        BarcodeFormat.qrCode,
        BarcodeFormat.dataMatrix,
      ],
      detectionSpeed: DetectionSpeed.normal,
      facing: CameraFacing.back,
    );

    _controller.addListener(_onControllerStateChanged);
    _controller.initializeScanner();
  }

  void _onControllerStateChanged() {
    if (!mounted) return;

    final state = _controller.state;

    // Transition to Verification Result screen upon completion of verification
    if (state.status == ScannerStatus.verificationResult && state.verificationResult != null) {
      Navigator.pushReplacement(
        context,
        AccessibilityRouter.createAccessibleRoute(
          AccessibleVerificationResultScreen(
            result: state.verificationResult!,
            ttsService: widget.ttsService,
          ),
        ),
      );
    }
  }

  @override
  void dispose() {
    _controller.removeListener(_onControllerStateChanged);
    _controller.dispose();
    _mobileScannerController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ScannerState>(
      valueListenable: _controller,
      builder: (context, state, _) {
        return AccessibleGestureController(
          ttsService: widget.ttsService,
          onDoubleTapScan: () => _controller.onBarcodeDetected("MD110"),
          onSwipeUpHome: () => Navigator.pop(context),
          onTwoFingerTapHelp: () => AccessibilityRouter.navigateToHelp(context, widget.ttsService),
          child: Scaffold(
            backgroundColor: AccessibilityTheme.background,
            appBar: AppBar(
              title: const Text('Voice-Guided Scanner'),
              backgroundColor: AccessibilityTheme.background,
              leading: IconButton(
                icon: const Icon(Icons.arrow_back, size: 28, color: AccessibilityTheme.accessibilityHighlight),
                onPressed: () => Navigator.pop(context),
              ),
            ),
            body: _buildBodyForState(state),
          ),
        );
      },
    );
  }

  Widget _buildBodyForState(ScannerState state) {
    if (state.status == ScannerStatus.cameraPermissionDenied) {
      return _buildPermissionDeniedScreen();
    }

    if (state.status == ScannerStatus.verifying) {
      return const AccessibleLoadingState(message: 'Medicine code detected. Verifying with server...');
    }

    if (state.status == ScannerStatus.verificationError) {
      return AccessibleErrorState(
        message: state.errorMessage ?? 'Verification failed.',
        onRetry: () => _controller.initializeScanner(),
      );
    }

    return Stack(
      children: [
        // Camera Viewport
        Positioned.fill(
          child: MobileScanner(
            controller: _mobileScannerController,
            onDetect: (capture) {
              final barcodes = capture.barcodes;
              if (barcodes.isNotEmpty) {
                final barcode = barcodes.first;
                final rawValue = barcode.rawValue ?? '';
                if (rawValue.isNotEmpty) {
                  _controller.onBarcodeDetected(rawValue, codeFormat: barcode.format.name);
                }
              }
            },
          ),
        ),

        // Accessible High-Contrast Reticle & Controls Overlay
        Positioned.fill(
          child: ScannerOverlay(
            state: state,
            onToggleTorch: () async {
              await _mobileScannerController?.toggleTorch();
              _controller.toggleTorch();
            },
            onSimulateScan: () => _controller.onBarcodeDetected("MD110"),
            onHelp: () => AccessibilityRouter.navigateToHelp(context, widget.ttsService),
          ),
        ),
      ],
    );
  }

  Widget _buildPermissionDeniedScreen() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.videocam_off, size: 80, color: AccessibilityTheme.error),
            const SizedBox(height: 20),
            const Text(
              'CAMERA ACCESS REQUIRED',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AccessibilityTheme.error),
            ),
            const SizedBox(height: 12),
            const Text(
              'Zero Latency needs camera access to scan your medicine DataMatrix and QR codes.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18, color: AccessibilityTheme.textSecondary),
            ),
            const SizedBox(height: 32),
            AccessiblePrimaryButton(
              label: 'ALLOW CAMERA ACCESS',
              icon: Icons.camera_alt,
              onPressed: () => _controller.initializeScanner(),
            ),
            const SizedBox(height: 16),
            AccessibleSecondaryButton(
              label: 'RETURN TO HOME',
              icon: Icons.home,
              onPressed: () => Navigator.pop(context),
            ),
          ],
        ),
      ),
    );
  }
}
