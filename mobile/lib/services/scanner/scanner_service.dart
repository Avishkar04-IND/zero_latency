abstract class ScannerService {
  Future<void> startScan({required Function(String rawCode) onCodeScanned});
  Future<void> stopScan();
  Future<void> toggleTorch();
}
