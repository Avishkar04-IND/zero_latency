import 'package:flutter/foundation.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/stt/stt_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../services/assistant/assistant_intent_service.dart';
import '../../../shared/models/verification_model.dart';

class AssistantState {
  final String userQuery;
  final String assistantResponse;
  final bool isListening;
  final bool isProcessing;
  final VerificationResult? verificationResult;
  final String? errorMessage;

  const AssistantState({
    required this.userQuery,
    required this.assistantResponse,
    this.isListening = false,
    this.isProcessing = false,
    this.verificationResult,
    this.errorMessage,
  });

  AssistantState copyWith({
    String? userQuery,
    String? assistantResponse,
    bool? isListening,
    bool? isProcessing,
    VerificationResult? verificationResult,
    String? errorMessage,
  }) {
    return AssistantState(
      userQuery: userQuery ?? this.userQuery,
      assistantResponse: assistantResponse ?? this.assistantResponse,
      isListening: isListening ?? this.isListening,
      isProcessing: isProcessing ?? this.isProcessing,
      verificationResult: verificationResult ?? this.verificationResult,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class AssistantController extends ValueNotifier<AssistantState> {
  final TTSService ttsService;
  final STTService sttService;
  bool _isDisposed = false;

  AssistantController({
    required this.ttsService,
    required this.sttService,
    VerificationResult? result,
  }) : super(AssistantState(
          userQuery: 'Tap mic button or hold screen to ask a question.',
          assistantResponse: result != null
              ? 'Assistant ready for ${result.medicine?.name ?? "verified medicine"}. Ask about dosage strength, expiry date, uses, warnings, or storage.'
              : 'I do not have a verified medicine record. Please scan a medicine package code first.',
          verificationResult: result,
        ));

  void speakInitialGreeting() {
    final res = state.verificationResult;
    if (res != null && res.medicine != null) {
      ttsService.speak('Voice Assistant ready for ${res.medicine!.name}. Ask a question about this medicine.');
    } else {
      ttsService.speak('Voice Assistant ready. Ask a question about medicine dosage, expiry date, or storage.');
    }
  }

  Future<void> startListening() async {
    if (state.isListening) {
      await stopListening();
      return;
    }

    _updateState(state.copyWith(
      isListening: true,
      errorMessage: null,
    ));

    await HapticsService.codeDetected();
    ttsService.speak('Listening now. Speak your question.');

    await sttService.listen(
      onResult: (queryText) {
        if (_isDisposed) return;
        if (queryText.trim().isNotEmpty) {
          processQuery(queryText);
        }
      },
    );
  }

  Future<void> stopListening() async {
    await sttService.stop();
    _updateState(state.copyWith(isListening: false));
  }

  void processQuery(String query) async {
    await stopListening();

    _updateState(state.copyWith(
      userQuery: query,
      isProcessing: true,
    ));

    await HapticsService.capture();
    ttsService.speak('Processing question.');

    await Future.delayed(const Duration(milliseconds: 500));

    final response = AssistantIntentService.generateResponse(
      query: query,
      result: state.verificationResult,
    );

    if (_isDisposed) return;

    _updateState(state.copyWith(
      assistantResponse: response,
      isProcessing: false,
    ));

    await HapticsService.verifiedAuthentic();
    ttsService.speak(response);
  }

  void repeatResponse() {
    HapticsService.scanningTick();
    ttsService.speak(state.assistantResponse);
  }

  void _updateState(AssistantState newState) {
    if (!_isDisposed) {
      value = newState;
    }
  }

  AssistantState get state => value;

  @override
  void dispose() {
    _isDisposed = true;
    sttService.stop();
    super.dispose();
  }
}
