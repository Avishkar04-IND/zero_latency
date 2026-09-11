import '../../shared/models/verification_model.dart';

enum AssistantIntent {
  medicineName,
  genericName,
  strength,
  manufacturer,
  batchNumber,
  manufacturingDate,
  expiryDate,
  uses,
  warnings,
  storage,
  verificationStatus,
  medicalAdviceRefusal,
  unknown,
}

class AssistantIntentService {
  static AssistantIntent parseQueryIntent(String query) {
    final q = query.toLowerCase().trim();

    // 1. Medical Safety Refusal Check (Dosage, Diagnosis, Medical Treatment)
    if (q.contains('how many') ||
        q.contains('dosage advice') ||
        q.contains('how much should i take') ||
        q.contains('how often') ||
        q.contains('can i take') ||
        q.contains('will this cure') ||
        q.contains('prescribe') ||
        q.contains('doctor advice') ||
        q.contains('treat my')) {
      return AssistantIntent.medicalAdviceRefusal;
    }

    // 2. Medicine Name
    if (q.contains('medicine name') ||
        q.contains('what is this medicine') ||
        q.contains('what pill') ||
        q.contains('name of medicine') ||
        q.contains('product name')) {
      return AssistantIntent.medicineName;
    }

    // 3. Generic Name
    if (q.contains('generic name') ||
        q.contains('generic') ||
        q.contains('active ingredient') ||
        q.contains('chemical name')) {
      return AssistantIntent.genericName;
    }

    // 4. Strength / Dosage
    if (q.contains('strength') ||
        q.contains('dosage') ||
        q.contains('milligrams') ||
        q.contains('mg') ||
        q.contains('how strong')) {
      return AssistantIntent.strength;
    }

    // 5. Manufacturer
    if (q.contains('manufacturer') ||
        q.contains('who makes') ||
        q.contains('who manufactured') ||
        q.contains('who made') ||
        q.contains('company') ||
        q.contains('brand')) {
      return AssistantIntent.manufacturer;
    }

    // 6. Batch Number
    if (q.contains('batch number') ||
        q.contains('batch') ||
        q.contains('lot number') ||
        q.contains('serial number')) {
      return AssistantIntent.batchNumber;
    }

    // 7. Manufacturing Date
    if (q.contains('manufactured') ||
        q.contains('manufacture date') ||
        q.contains('date made') ||
        q.contains('production date')) {
      return AssistantIntent.manufacturingDate;
    }

    // 8. Expiry Date
    if (q.contains('expire') ||
        q.contains('expiry') ||
        q.contains('expiration') ||
        q.contains('when does it expire') ||
        q.contains('use by date')) {
      return AssistantIntent.expiryDate;
    }

    // 9. Uses / Purpose
    if (q.contains('used for') ||
        q.contains('indication') ||
        q.contains('why take') ||
        q.contains('purpose') ||
        q.contains('what does it treat')) {
      return AssistantIntent.uses;
    }

    // 10. Warnings / Precautions
    if (q.contains('warning') ||
        q.contains('side effect') ||
        q.contains('precaution') ||
        q.contains('danger') ||
        q.contains('risk')) {
      return AssistantIntent.warnings;
    }

    // 11. Storage Instructions
    if (q.contains('store') ||
        q.contains('storage') ||
        q.contains('temperature') ||
        q.contains('refrigerate') ||
        q.contains('keep cool')) {
      return AssistantIntent.storage;
    }

    // 12. Verification Status
    if (q.contains('verified') ||
        q.contains('authentic') ||
        q.contains('fake') ||
        q.contains('real') ||
        q.contains('legit') ||
        q.contains('status')) {
      return AssistantIntent.verificationStatus;
    }

    return AssistantIntent.unknown;
  }

  static String generateResponse({
    required String query,
    required VerificationResult? result,
  }) {
    if (result == null) {
      return "I don't have a verified medicine to answer questions about. Please scan a medicine package code first.";
    }

    final intent = parseQueryIntent(query);
    final med = result.medicine;
    final batch = result.batch;

    switch (intent) {
      case AssistantIntent.medicalAdviceRefusal:
        return "I cannot provide personalized medical diagnosis or dosage advice. Please follow the instructions on the medicine packaging or consult a healthcare professional.";

      case AssistantIntent.medicineName:
        if (med != null && med.name.isNotEmpty) {
          return "The verified medicine name is ${med.name}.";
        }
        return "I don't have verified medicine name information for this scan.";

      case AssistantIntent.genericName:
        if (med != null && med.genericName.isNotEmpty) {
          return "The generic active name is ${med.genericName}.";
        }
        return "Generic name information is not listed in the verified record.";

      case AssistantIntent.strength:
        if (med != null && med.dosage.isNotEmpty) {
          return "The dosage strength is ${med.dosage}.";
        }
        return "Strength information is not listed for this medicine.";

      case AssistantIntent.manufacturer:
        if (med != null && med.manufacturer.isNotEmpty) {
          return "This medicine is manufactured by ${med.manufacturer}.";
        }
        return "Manufacturer details are not listed in the verified record.";

      case AssistantIntent.batchNumber:
        if (batch != null && batch.batchNumber.isNotEmpty) {
          return "The batch number is ${batch.batchNumber}.";
        }
        return "Batch number is not available for this medicine scan.";

      case AssistantIntent.manufacturingDate:
        if (batch != null && batch.manufactureDate.isNotEmpty) {
          return "This batch was manufactured on ${batch.manufactureDate}.";
        }
        return "Manufacturing date is not available.";

      case AssistantIntent.expiryDate:
        if (batch != null && batch.expiryDate.isNotEmpty) {
          return "The expiry date is ${batch.expiryDate}. ${batch.isExpired() ? 'Warning: This medicine is EXPIRED.' : ''}";
        }
        return "Expiry date is not listed for this batch.";

      case AssistantIntent.uses:
        if (med != null && med.description.isNotEmpty) {
          return "This medicine is used for ${med.description}.";
        }
        return "Uses information is not listed in the verified record.";

      case AssistantIntent.warnings:
        if (med != null && med.warnings.isNotEmpty) {
          return "Safety Warnings: ${med.warnings}.";
        }
        return "No specific warnings are listed in the verified record. Always follow package instructions.";

      case AssistantIntent.storage:
        if (med != null && med.storageInstructions.isNotEmpty) {
          return "Storage Instructions: ${med.storageInstructions}.";
        }
        return "Storage instructions are not specified in the verified record.";

      case AssistantIntent.verificationStatus:
        return result.toSpokenHeadline();

      case AssistantIntent.unknown:
      default:
        return "I can answer questions about medicine name, generic name, strength, manufacturer, batch number, expiry date, uses, warnings, and storage instructions. Please ask about one of these topics.";
    }
  }
}
