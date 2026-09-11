class MedicineModel {
  final String id;
  final String name;
  final String dosage;
  final String manufacturer;
  final String description;
  final String storageInstructions;
  final String warnings;

  const MedicineModel({
    required this.id,
    required this.name,
    required this.dosage,
    required this.manufacturer,
    required this.description,
    required this.storageInstructions,
    required this.warnings,
  });

  factory MedicineModel.fromJson(Map<String, dynamic> json) {
    return MedicineModel(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      dosage: json['dosage'] as String? ?? '',
      manufacturer: json['manufacturer'] as String? ?? '',
      description: json['description'] as String? ?? '',
      storageInstructions: json['storage_instructions'] as String? ?? '',
      warnings: json['warnings'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'dosage': dosage,
      'manufacturer': manufacturer,
      'description': description,
      'storage_instructions': storageInstructions,
      'warnings': warnings,
    };
  }

  String toSpokenSummary() {
    return 'Medicine: $name. Dosage: $dosage. Manufacturer: $manufacturer. Warnings: $warnings.';
  }
}
