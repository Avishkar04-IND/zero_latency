import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'history_service.dart';
import '../../shared/models/history_record.dart';
import '../../shared/models/verification_model.dart';

class LocalHistoryService implements HistoryService {
  static const String _storageKey = 'zero_latency_scan_history_v1';
  static const int _duplicateTimeWindowSeconds = 5;

  final List<HistoryRecord> _memoryCache = [];
  bool _isCacheInitialized = false;

  LocalHistoryService();

  Future<void> _ensureCacheLoaded() async {
    if (_isCacheInitialized) return;
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = prefs.getString(_storageKey);
      if (jsonString != null && jsonString.isNotEmpty) {
        final List<dynamic> decodedList = jsonDecode(jsonString);
        _memoryCache.clear();
        for (final item in decodedList) {
          if (item is Map<String, dynamic>) {
            _memoryCache.add(HistoryRecord.fromJson(item));
          }
        }
        _sortRecordsNewestFirst();
      }
    } catch (e) {
      debugPrint("LocalHistoryService warning: storage load failed: $e");
    } finally {
      _isCacheInitialized = true;
    }
  }

  Future<void> _persistCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonList = _memoryCache.map((rec) => rec.toJson()).toList();
      final jsonString = jsonEncode(jsonList);
      await prefs.setString(_storageKey, jsonString);
    } catch (e) {
      debugPrint("LocalHistoryService warning: storage persist failed: $e");
    }
  }

  void _sortRecordsNewestFirst() {
    _memoryCache.sort((a, b) {
      try {
        final dtA = DateTime.parse(a.timestamp);
        final dtB = DateTime.parse(b.timestamp);
        return dtB.compareTo(dtA);
      } catch (_) {
        return b.timestamp.compareTo(a.timestamp);
      }
    });
  }

  bool _isDuplicateScan(HistoryRecord newRecord) {
    if (_memoryCache.isEmpty || newRecord.rawCode.isEmpty) return false;

    // Check recent scans for duplicate rawCode within window
    for (final existing in _memoryCache) {
      if (existing.rawCode == newRecord.rawCode) {
        try {
          final dtExisting = DateTime.parse(existing.timestamp);
          final dtNew = DateTime.parse(newRecord.timestamp);
          final diff = dtNew.difference(dtExisting).inSeconds.abs();
          if (diff < _duplicateTimeWindowSeconds) {
            return true; // Duplicate suppressed
          }
        } catch (_) {}
      }
    }
    return false;
  }

  @override
  Future<List<HistoryRecord>> getHistoryRecords() async {
    await _ensureCacheLoaded();
    _sortRecordsNewestFirst();
    return List.unmodifiable(_memoryCache);
  }

  @override
  Future<void> saveRecord(HistoryRecord record) async {
    await _ensureCacheLoaded();

    // Duplicate check: suppress rapid duplicate scans of exact same raw code within 5s
    if (_isDuplicateScan(record)) {
      debugPrint("LocalHistoryService: Rapid duplicate scan suppressed for ${record.rawCode}");
      return;
    }

    _memoryCache.insert(0, record);
    _sortRecordsNewestFirst();
    await _persistCache();
  }

  @override
  Future<void> saveVerification(VerificationResult result) async {
    try {
      final record = HistoryRecord.fromVerificationResult(result);
      await saveRecord(record);
    } catch (e) {
      debugPrint("LocalHistoryService error saving verification result: $e");
      // Graceful error handling: history failure must never crash verification
    }
  }

  @override
  Future<void> deleteRecord(String id) async {
    await _ensureCacheLoaded();
    _memoryCache.removeWhere((rec) => rec.id == id);
    await _persistCache();
  }

  @override
  Future<void> clearHistory() async {
    await _ensureCacheLoaded();
    _memoryCache.clear();
    await _persistCache();
  }
}
