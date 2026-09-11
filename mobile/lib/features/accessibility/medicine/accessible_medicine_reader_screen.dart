import 'package:flutter/material.dart';
import '../../../services/tts/tts_service.dart';
import '../../../shared/models/verification_model.dart';
import '../gestures/accessible_gesture_controller.dart';

class AccessibleMedicineReaderScreen extends StatefulWidget {
  final VerificationResult verificationResult;
  final TTSService ttsService;

  const AccessibleMedicineReaderScreen({
    super.key,
    required this.verificationResult,
    required this.ttsService,
  });

  @override
  State<AccessibleMedicineReaderScreen> createState() => _AccessibleMedicineReaderScreenState();
}

class _AccessibleMedicineReaderScreenState extends State<AccessibleMedicineReaderScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _speakResult();
    });
  }

  void _speakResult() {
    widget.ttsService.speak(widget.verificationResult.toSpokenResult());
  }

  Color _getStatusColor() {
    switch (widget.verificationResult.status) {
      case VerificationStatus.authentic:
        return const Color(0xFF33FF99);
      case VerificationStatus.expired:
        return const Color(0xFFFF9900);
      case VerificationStatus.suspectedCounterfeit:
      case VerificationStatus.recalled:
        return const Color(0xFFFF3333);
      case VerificationStatus.invalid:
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final result = widget.verificationResult;
    final medicine = result.medicine;
    final batch = result.batch;
    final statusColor = _getStatusColor();

    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onSwipeUpHome: () => Navigator.popUntil(context, (route) => route.isFirst),
      onSwipeDownRepeat: _speakResult,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Medicine Verification Info'),
          backgroundColor: Colors.black,
        ),
        body: Container(
          color: Colors.black,
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: statusColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    Text(
                      result.status.name.toUpperCase(),
                      style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.black),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      result.message,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 18, color: Colors.black, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              Expanded(
                child: ListView(
                  children: [
                    if (medicine != null) ...[
                      _buildInfoTile('MEDICINE NAME', medicine.name, Icons.medication),
                      _buildInfoTile('DOSAGE', medicine.dosage, Icons.line_weight),
                      _buildInfoTile('MANUFACTURER', medicine.manufacturer, Icons.factory),
                      _buildInfoTile('STORAGE', medicine.storageInstructions, Icons.ac_unit),
                      _buildInfoTile('WARNINGS', medicine.warnings, Icons.warning_amber),
                    ],
                    if (batch != null) ...[
                      _buildInfoTile('BATCH NUMBER', batch.batchNumber, Icons.inventory_2),
                      _buildInfoTile('EXPIRY DATE', batch.expiryDate, Icons.calendar_today),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFFFD700),
                  foregroundColor: Colors.black,
                  minimumSize: const Size(double.infinity, 64),
                ),
                onPressed: _speakResult,
                icon: const Icon(Icons.volume_up, size: 32),
                label: const Text('RE-READ DETAILS'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoTile(String title, String value, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white24),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 32, color: const Color(0xFFFFD700)),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, color: Colors.grey, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(value, style: const TextStyle(fontSize: 20, color: Colors.white, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
