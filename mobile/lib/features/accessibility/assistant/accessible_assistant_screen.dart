import 'package:flutter/material.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/stt/stt_service.dart';
import '../../../services/api/api_service.dart';
import '../gestures/accessible_gesture_controller.dart';

class AccessibleAssistantScreen extends StatefulWidget {
  final TTSService ttsService;
  final ApiService apiService;

  const AccessibleAssistantScreen({
    super.key,
    required this.ttsService,
    required this.apiService,
  });

  @override
  State<AccessibleAssistantScreen> createState() => _AccessibleAssistantScreenState();
}

class _AccessibleAssistantScreenState extends State<AccessibleAssistantScreen> {
  final STTService _sttService = STTService();
  String _userQuery = "Tap mic button to speak your medicine query.";
  String _assistantResponse = "Assistant standing by. You can ask about medicine storage, expiry dates, or dosage.";
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      widget.ttsService.speak(
        "Voice Assistant screen. Tap microphone button or hold screen to speak your medicine query.",
      );
    });
  }

  Future<void> _startListening() async {
    widget.ttsService.speak("Listening now. Speak your question.");
    await _sttService.listen(
      onResult: (text) async {
        setState(() {
          _userQuery = text;
          _isProcessing = true;
        });
        widget.ttsService.speak("Processing question: $text");
        final resp = await widget.apiService.sendAssistantQuery(text);
        final respText = resp['response_text'] as String? ?? 'No response received.';
        if (mounted) {
          setState(() {
            _assistantResponse = respText;
            _isProcessing = false;
          });
          widget.ttsService.speak(_assistantResponse);
        }
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onSwipeUpHome: () => Navigator.pop(context),
      onSwipeDownRepeat: () => widget.ttsService.speak(_assistantResponse),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Voice Assistant Interface'),
          backgroundColor: Colors.black,
        ),
        body: Container(
          color: Colors.black,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E1E1E),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF00FFFF), width: 2),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('YOU SAID:', style: TextStyle(color: Color(0xFF00FFFF), fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Text(_userQuery, style: const TextStyle(fontSize: 20, color: Colors.white)),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E1E1E),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFFFD700), width: 2),
                  ),
                  child: SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('ASSISTANT RESPONSE:', style: TextStyle(color: Color(0xFFFFD700), fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        if (_isProcessing)
                          const CircularProgressIndicator(color: Color(0xFFFFD700))
                        else
                          Text(_assistantResponse, style: const TextStyle(fontSize: 22, color: Colors.white, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF00FFFF),
                  foregroundColor: Colors.black,
                  minimumSize: const Size(double.infinity, 80),
                ),
                onPressed: _startListening,
                icon: const Icon(Icons.mic, size: 40),
                label: const Text('TAP TO SPEAK QUERY', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
