import 'package:flutter/foundation.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../shared/models/verification_model.dart';

class MedicineReaderSectionData {
  final int index;
  final String title;
  final String content;
  final String spokenText;

  const MedicineReaderSectionData({
    required this.index,
    required this.title,
    required this.content,
    required this.spokenText,
  });
}

class MedicineReaderState {
  final int currentIndex;
  final List<MedicineReaderSectionData> sections;
  final VerificationResult verificationResult;
  final bool isSpeaking;

  const MedicineReaderState({
    required this.currentIndex,
    required this.sections,
    required this.verificationResult,
    this.isSpeaking = false,
  });

  MedicineReaderSectionData get currentSection =>
      sections.isNotEmpty ? sections[currentIndex.clamp(0, sections.length - 1)] : const MedicineReaderSectionData(index: 0, title: '', content: '', spokenText: '');

  MedicineReaderState copyWith({
    int? currentIndex,
    List<MedicineReaderSectionData>? sections,
    VerificationResult? verificationResult,
    bool? isSpeaking,
  }) {
    return MedicineReaderState(
      currentIndex: currentIndex ?? this.currentIndex,
      sections: sections ?? this.sections,
      verificationResult: verificationResult ?? this.verificationResult,
      isSpeaking: isSpeaking ?? this.isSpeaking,
    );
  }
}

class MedicineReaderController extends ValueNotifier<MedicineReaderState> {
  final TTSService ttsService;

  MedicineReaderController({
    required VerificationResult result,
    required this.ttsService,
  }) : super(MedicineReaderState(
          currentIndex: 0,
          sections: _buildSections(result),
          verificationResult: result,
        ));

  static List<MedicineReaderSectionData> _buildSections(VerificationResult result) {
    final med = result.medicine;
    final batch = result.batch;
    final List<MedicineReaderSectionData> list = [];
    int idx = 0;

    if (med != null) {
      list.add(MedicineReaderSectionData(
        index: idx++,
        title: 'MEDICINE NAME',
        content: med.name,
        spokenText: 'Medicine name: ${med.name}.',
      ));

      if (med.genericName.isNotEmpty && med.genericName != med.name) {
        list.add(MedicineReaderSectionData(
          index: idx++,
          title: 'GENERIC NAME',
          content: med.genericName,
          spokenText: 'Generic name: ${med.genericName}.',
        ));
      }

      list.add(MedicineReaderSectionData(
        index: idx++,
        title: 'STRENGTH',
        content: med.dosage,
        spokenText: 'Strength: ${med.dosage}.',
      ));

      list.add(MedicineReaderSectionData(
        index: idx++,
        title: 'MANUFACTURER',
        content: med.manufacturer,
        spokenText: 'Manufacturer: ${med.manufacturer}.',
      ));
    }

    if (batch != null) {
      list.add(MedicineReaderSectionData(
        index: idx++,
        title: 'BATCH NUMBER',
        content: batch.batchNumber,
        spokenText: 'Batch number: ${batch.batchNumber}.',
      ));

      list.add(MedicineReaderSectionData(
        index: idx++,
        title: 'MANUFACTURING DATE',
        content: batch.manufactureDate,
        spokenText: 'Manufacturing date: ${batch.manufactureDate}.',
      ));

      list.add(MedicineReaderSectionData(
        index: idx++,
        title: 'EXPIRY DATE',
        content: batch.expiryDate,
        spokenText: 'Expiry date: ${batch.expiryDate}.',
      ));
    }

    if (med != null) {
      if (med.description.isNotEmpty) {
        list.add(MedicineReaderSectionData(
          index: idx++,
          title: 'USES',
          content: med.description,
          spokenText: 'Uses: ${med.description}.',
        ));
      }

      if (med.warnings.isNotEmpty) {
        list.add(MedicineReaderSectionData(
          index: idx++,
          title: 'WARNINGS',
          content: med.warnings,
          spokenText: 'Warnings: ${med.warnings}.',
        ));
      }

      if (med.storageInstructions.isNotEmpty) {
        list.add(MedicineReaderSectionData(
          index: idx++,
          title: 'STORAGE INSTRUCTIONS',
          content: med.storageInstructions,
          spokenText: 'Storage instructions: ${med.storageInstructions}.',
        ));
      }
    }

    if (list.isEmpty) {
      list.add(MedicineReaderSectionData(
        index: 0,
        title: 'VERIFICATION MESSAGE',
        content: result.message,
        spokenText: result.message,
      ));
    }

    return list;
  }

  void speakInitialVerificationHeadline() {
    final headline = state.verificationResult.toSpokenHeadline();
    ttsService.speak(headline);
  }

  void speakCurrentSection() {
    final section = state.currentSection;
    HapticsService.scanningTick();
    ttsService.speak(section.spokenText);
  }

  void nextSection() {
    if (state.sections.isEmpty) return;
    final nextIdx = (state.currentIndex + 1).clamp(0, state.sections.length - 1);
    value = state.copyWith(currentIndex: nextIdx);
    speakCurrentSection();
  }

  void previousSection() {
    if (state.sections.isEmpty) return;
    final prevIdx = (state.currentIndex - 1).clamp(0, state.sections.length - 1);
    value = state.copyWith(currentIndex: prevIdx);
    speakCurrentSection();
  }

  void jumpToSection(int index) {
    if (index >= 0 && index < state.sections.length) {
      value = state.copyWith(currentIndex: index);
      speakCurrentSection();
    }
  }
}
