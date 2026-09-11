import 'dart:async';
import 'package:mobile_scanner/mobile_scanner.dart';

abstract class ScannerService {
  Future<void> initialize();
  Future<void> startScan({required Function(String rawCode, BarcodeFormat format) onCodeScanned});
  Future<void> stopScan();
  Future<void> toggleTorch();
  Future<void> dispose();
}

class MobileScannerService implements ScannerService {
  MobileScannerController? _controller;
  bool _isTorchOn = false;

  MobileScannerController? get controller => _controller;

  @override
  Future<void> initialize() async {
    _controller = MobileScannerController(
      formats: const [
        BarcodeFormat.qrCode,
        BarcodeFormat.dataMatrix,
      ],
      detectionSpeed: DetectionSpeed.normal,
      facing: CameraFacing.back,
      torchEnabled: false,
    );
  }

  @override
  Future<void> startScan({required Function(String rawCode, BarcodeFormat format) onCodeScanned}) async {
    if (_controller == null) {
      await initialize();
    }
    await _controller?.start();
  }

  @override
  Future<void> stopScan() async {
    await _controller?.stop();
  }

  @override
  Future<void> toggleTorch() async {
    if (_controller != null) {
      _isTorchOn = !_isTorchOn;
      await _controller?.toggleTorch();
    }
  }

  @override
  Future<void> dispose() async {
    await _controller?.dispose();
    _controller = null;
  }
}
