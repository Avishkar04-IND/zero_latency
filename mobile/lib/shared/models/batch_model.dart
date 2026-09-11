class BatchModel {
  final String id;
  final String batchNumber;
  final String manufactureDate;
  final String expiryDate;
  final int quantity;

  const BatchModel({
    required this.id,
    required this.batchNumber,
    required this.manufactureDate,
    required this.expiryDate,
    required this.quantity,
  });

  factory BatchModel.fromJson(Map<String, dynamic> json) {
    return BatchModel(
      id: json['id'] as String? ?? '',
      batchNumber: json['batch_number'] as String? ?? '',
      manufactureDate: json['manufacture_date'] as String? ?? '',
      expiryDate: json['expiry_date'] as String? ?? '',
      quantity: json['quantity'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'batch_number': batchNumber,
      'manufacture_date': manufactureDate,
      'expiry_date': expiryDate,
      'quantity': quantity,
    };
  }

  bool isExpired() {
    try {
      final expiry = DateTime.parse(expiryDate);
      return DateTime.now().isAfter(expiry);
    } catch (_) {
      return false;
    }
  }
}
