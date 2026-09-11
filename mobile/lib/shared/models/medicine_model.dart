class MedicineModel {
  final String id;
  final String name;
  final String genericName;
  final String dosage;
  final String manufacturer;
  final String description;
  final String storageInstructions;
  final String warnings;

  const MedicineModel({
    required this.id,
    required this.name,
    this.genericName = '',
    required this.dosage,
    required this.manufacturer,
    required this.description,
    required this.storageInstructions,
    required this.warnings,
  });

  String get strength => dosage;
  String get uses => description;
  String get storage => storageInstructions;

  factory MedicineModel.fromJson(Map<String, dynamic> json) {
    return MedicineModel(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      genericName: json['generic_name'] as String? ?? json['name'] as String? ?? '',
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
      'generic_name': genericName,
      'dosage': dosage,
      'manufacturer': manufacturer,
      'description': description,
      'storage_instructions': storageInstructions,
      'warnings': warnings,
    };
  }

  String toSpokenSummary() {
    final genericStr = genericName.isNotEmpty && genericName != name ? 'Generic name: $genericName.' : '';
    return 'Medicine name: $name. $genericStr Strength: $dosage. Manufacturer: $manufacturer. Uses: $description. Warnings: $warnings. Storage: $storageInstructions.';
  }
}
