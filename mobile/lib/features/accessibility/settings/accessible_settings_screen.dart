import 'package:flutter/material.dart';
import '../../../services/tts/tts_service.dart';
import '../gestures/accessible_gesture_controller.dart';

class AccessibleSettingsScreen extends StatefulWidget {
  final TTSService ttsService;

  const AccessibleSettingsScreen({
    super.key,
    required this.ttsService,
  });

  @override
  State<AccessibleSettingsScreen> createState() => _AccessibleSettingsScreenState();
}

class _AccessibleSettingsScreenState extends State<AccessibleSettingsScreen> {
  double _speechRate = 0.5;
  bool _hapticsEnabled = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      widget.ttsService.speak("Accessibility Settings menu active.");
    });
  }

  @override
  Widget build(BuildContext context) {
    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onSwipeUpHome: () => Navigator.pop(context),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Accessibility Settings'),
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
                  border: Border.all(color: const Color(0xFFFFD700), width: 2),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('VOICE READOUT SPEED', style: TextStyle(fontSize: 18, color: Color(0xFFFFD700), fontWeight: FontWeight.bold)),
                    Slider(
                      value: _speechRate,
                      min: 0.2,
                      max: 1.0,
                      divisions: 8,
                      activeColor: const Color(0xFFFFD700),
                      label: '${(_speechRate * 100).toInt()}%',
                      onChanged: (val) {
                        setState(() {
                          _speechRate = val;
                        });
                        widget.ttsService.setSpeechRate(val);
                        widget.ttsService.speak("Voice readout speed set to ${(_speechRate * 100).toInt()} percent.");
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E1E1E),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF00FFFF), width: 2),
                ),
                child: SwitchListTile(
                  title: const Text('TACTILE HAPTIC VIBRATIONS', style: TextStyle(fontSize: 20, color: Colors.white, fontWeight: FontWeight.bold)),
                  value: _hapticsEnabled,
                  activeColor: const Color(0xFF00FFFF),
                  onChanged: (val) {
                    setState(() {
                      _hapticsEnabled = val;
                    });
                    widget.ttsService.speak(val ? "Haptic vibrations enabled." : "Haptic vibrations disabled.");
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
