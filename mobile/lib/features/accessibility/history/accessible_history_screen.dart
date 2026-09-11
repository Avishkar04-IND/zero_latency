import 'package:flutter/material.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/api/api_service.dart';
import '../../../shared/models/verification_model.dart';
import '../gestures/accessible_gesture_controller.dart';
import '../medicine/accessible_medicine_reader_screen.dart';

class AccessibleHistoryScreen extends StatefulWidget {
  final TTSService ttsService;
  final ApiService apiService;

  const AccessibleHistoryScreen({
    super.key,
    required this.ttsService,
    required this.apiService,
  });

  @override
  State<AccessibleHistoryScreen> createState() => _AccessibleHistoryScreenState();
}

class _AccessibleHistoryScreenState extends State<AccessibleHistoryScreen> {
  List<VerificationResult> _history = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    final list = await widget.apiService.getScanHistory();
    if (mounted) {
      setState(() {
        _history = list;
        _isLoading = false;
      });
      widget.ttsService.speak(
        "Scan History. ${_history.length} verification records found. Tap item to hear medicine info.",
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onSwipeUpHome: () => Navigator.pop(context),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Spoken Scan History'),
          backgroundColor: Colors.black,
        ),
        body: _isLoading
            ? const Center(child: CircularProgressIndicator(color: Color(0xFFFFD700)))
            : _history.isEmpty
                ? const Center(
                    child: Text(
                      'No scan history recorded yet.',
                      style: TextStyle(fontSize: 22, color: Colors.white),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _history.length,
                    itemBuilder: (context, index) {
                      final item = _history[index];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1A1A1A),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFFFFD700), width: 2),
                        ),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(16),
                          leading: const Icon(Icons.verified, size: 40, color: Color(0xFFFFD700)),
                          title: Text(
                            item.medicine?.name ?? 'Scanned Code',
                            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                          subtitle: Text(
                            'Status: ${item.status.name.toUpperCase()} • ${item.scannedAt.substring(0, 10)}',
                            style: const TextStyle(fontSize: 16, color: Color(0xFF00FFFF)),
                          ),
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => AccessibleMedicineReaderScreen(
                                  verificationResult: item,
                                  ttsService: widget.ttsService,
                                ),
                              ),
                            );
                          },
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}
