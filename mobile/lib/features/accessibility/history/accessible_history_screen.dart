import 'package:flutter/material.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../core/accessibility/talkback_helpers.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../services/api/api_service.dart';
import '../../../services/history/history_service.dart';
import '../../../services/history/local_history_service.dart';
import '../../../shared/models/history_record.dart';
import '../../../shared/models/verification_model.dart';
import '../../../shared/widgets/accessible_buttons.dart';
import '../../../shared/widgets/accessible_states.dart';
import '../gestures/accessible_gesture_controller.dart';
import '../medicine/accessible_medicine_reader_screen.dart';
import '../navigation/accessibility_router.dart';
import 'history_controller.dart';

class AccessibleHistoryScreen extends StatefulWidget {
  final TTSService ttsService;
  final ApiService apiService;
  final HistoryService? historyService;

  const AccessibleHistoryScreen({
    super.key,
    required this.ttsService,
    required this.apiService,
    this.historyService,
  });

  @override
  State<AccessibleHistoryScreen> createState() => _AccessibleHistoryScreenState();
}

class _AccessibleHistoryScreenState extends State<AccessibleHistoryScreen> {
  late HistoryController _controller;
  late HistoryService _historyService;

  @override
  void initState() {
    super.initState();
    _historyService = widget.historyService ?? LocalHistoryService();
    _controller = HistoryController(
      historyService: _historyService,
      ttsService: widget.ttsService,
    );

    _controller.loadHistory();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _openMedicineReader(HistoryRecord record) {
    HapticsService.scanningTick();
    final verificationResult = record.toVerificationResult();
    AccessibilityRouter.navigateToMedicineReader(context, widget.ttsService, verificationResult);
  }

  void _showDeleteConfirmation(BuildContext context, HistoryRecord record) {
    _controller.requestDeleteConfirmation(record.id);

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: const Color(0xFF151B22),
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: AccessibilityTheme.error, width: 3),
          borderRadius: BorderRadius.circular(16),
        ),
        title: TalkBackSemantics(
          label: 'Delete Scan Confirmation',
          isHeader: true,
          child: Row(
            children: const [
              Icon(Icons.warning_amber_rounded, color: AccessibilityTheme.error, size: 32),
              SizedBox(width: 12),
              Text(
                'Delete Scan?',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
              ),
            ],
          ),
        ),
        content: Text(
          'Delete scan record for ${record.medicineName} from history?',
          style: const TextStyle(fontSize: 18, color: AccessibilityTheme.textSecondary),
        ),
        actionsPadding: const EdgeInsets.all(16),
        actions: [
          Row(
            children: [
              Expanded(
                child: AccessibleSecondaryButton(
                  label: 'CANCEL',
                  icon: Icons.close,
                  onPressed: () {
                    _controller.cancelDeleteConfirmation();
                    Navigator.pop(dialogContext);
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: AccessiblePrimaryButton(
                  label: 'DELETE',
                  icon: Icons.delete_forever,
                  backgroundColor: AccessibilityTheme.error,
                  foregroundColor: Colors.white,
                  onPressed: () {
                    Navigator.pop(dialogContext);
                    _controller.confirmAndDelete(record.id);
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showClearAllConfirmation(BuildContext context) {
    _controller.requestClearAllConfirmation();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: const Color(0xFF151B22),
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: AccessibilityTheme.error, width: 3),
          borderRadius: BorderRadius.circular(16),
        ),
        title: TalkBackSemantics(
          label: 'Clear All History Confirmation',
          isHeader: true,
          child: Row(
            children: const [
              Icon(Icons.delete_sweep, color: AccessibilityTheme.error, size: 32),
              SizedBox(width: 12),
              Text(
                'Clear All Scans?',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
              ),
            ],
          ),
        ),
        content: const Text(
          'Are you sure you want to permanently clear all scan history? This action cannot be undone.',
          style: TextStyle(fontSize: 18, color: AccessibilityTheme.textSecondary),
        ),
        actionsPadding: const EdgeInsets.all(16),
        actions: [
          Row(
            children: [
              Expanded(
                child: AccessibleSecondaryButton(
                  label: 'CANCEL',
                  icon: Icons.close,
                  onPressed: () {
                    _controller.cancelClearAllConfirmation();
                    Navigator.pop(dialogContext);
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: AccessiblePrimaryButton(
                  label: 'CLEAR ALL',
                  icon: Icons.delete_sweep,
                  backgroundColor: AccessibilityTheme.error,
                  foregroundColor: Colors.white,
                  onPressed: () {
                    Navigator.pop(dialogContext);
                    _controller.confirmAndClearAll();
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<HistoryState>(
      valueListenable: _controller,
      builder: (context, state, _) {
        return AccessibleGestureController(
          ttsService: widget.ttsService,
          onSwipeUpHome: () => Navigator.pop(context),
          onSwipeDownRepeat: () => _controller.speakCurrentSummary(),
          onLongPressAssistant: () => AccessibilityRouter.navigateToAssistant(context, widget.ttsService, widget.apiService),
          onTwoFingerTapHelp: () => AccessibilityRouter.navigateToHelp(context, widget.ttsService),
          child: Scaffold(
            backgroundColor: AccessibilityTheme.background,
            appBar: AppBar(
              backgroundColor: AccessibilityTheme.background,
              elevation: 0,
              leading: IconButton(
                icon: const Icon(Icons.arrow_back, size: 28, color: AccessibilityTheme.accessibilityHighlight),
                onPressed: () => Navigator.pop(context),
                tooltip: 'Back to Home',
              ),
              title: TalkBackSemantics(
                label: 'Spoken Scan History Screen',
                isHeader: true,
                child: const Text(
                  'SCAN HISTORY',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.extrabold,
                    color: AccessibilityTheme.accessibilityHighlight,
                    letterSpacing: 1.0,
                  ),
                ),
              ),
              actions: [
                if (state.records.isNotEmpty)
                  IconButton(
                    icon: const Icon(Icons.delete_sweep, color: AccessibilityTheme.error, size: 28),
                    onPressed: () => _showClearAllConfirmation(context),
                    tooltip: 'Clear All History',
                  ),
              ],
            ),
            body: SafeArea(
              child: _buildBodyContent(state),
            ),
          ),
        );
      },
    );
  }

  Widget _buildBodyContent(HistoryState state) {
    if (state.isLoading) {
      return const AccessibleLoadingState(message: 'Loading your scan history...');
    }

    if (state.errorMessage != null) {
      return AccessibleErrorState(
        message: state.errorMessage!,
        onRetry: () => _controller.loadHistory(),
      );
    }

    if (state.records.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.history,
                size: 90,
                color: AccessibilityTheme.textSecondary,
              ),
              const SizedBox(height: 20),
              TalkBackSemantics(
                label: 'You have no scan history yet.',
                isHeader: true,
                child: const Text(
                  'No Scan History',
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                    color: AccessibilityTheme.textPrimary,
                  ),
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                'Scanned medicines and verification results will automatically appear here.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 18,
                  color: AccessibilityTheme.textSecondary,
                ),
              ),
              const SizedBox(height: 32),
              AccessiblePrimaryButton(
                label: 'START NEW SCAN',
                icon: Icons.qr_code_scanner,
                onPressed: () => AccessibilityRouter.navigateToScanner(context, widget.ttsService, widget.apiService),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      itemCount: state.records.length,
      itemBuilder: (context, index) {
        final record = state.records[index];
        return _buildHistoryItemCard(record, index);
      },
    );
  }

  Widget _buildHistoryItemCard(HistoryRecord record, int index) {
    final statusColor = _getStatusColor(record.verificationStatus);
    final statusIcon = _getStatusIcon(record.verificationStatus);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF151B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: statusColor, width: 2.5),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () {
            _controller.speakItemDetails(record);
            _openMedicineReader(record);
          },
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Header Row: Status Badge & Delete Icon Button
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Status Badge with Icon + Explicit Text
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: statusColor.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: statusColor, width: 1.5),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(statusIcon, color: statusColor, size: 20),
                          const SizedBox(width: 6),
                          Text(
                            record.formattedStatus.toUpperCase(),
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: statusColor,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Delete Single Record Action Button
                    Semantics(
                      label: 'Delete scan for ${record.medicineName}',
                      hint: 'Double tap to remove this scan from history',
                      child: IconButton(
                        icon: const Icon(Icons.delete_outline, color: AccessibilityTheme.error, size: 28),
                        onPressed: () => _showDeleteConfirmation(context, record),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Medicine Name Headline
                TalkBackSemantics(
                  label: record.toSpokenHeadline(),
                  isHeader: true,
                  child: Text(
                    record.medicineName,
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.extrabold,
                      color: AccessibilityTheme.textPrimary,
                    ),
                  ),
                ),
                const SizedBox(height: 8),

                // Metadata Details: Batch, Expiry, Timestamp
                if (record.batchNumber != 'N/A') ...[
                  Row(
                    children: [
                      const Icon(Icons.inventory_2_outlined, size: 18, color: AccessibilityTheme.textSecondary),
                      const SizedBox(width: 6),
                      Text(
                        'Batch: ${record.batchNumber}',
                        style: const TextStyle(fontSize: 16, color: AccessibilityTheme.textSecondary, fontWeight: FontWeight.w500),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                ],

                if (record.expiryDate != 'N/A') ...[
                  Row(
                    children: [
                      const Icon(Icons.calendar_today_outlined, size: 18, color: AccessibilityTheme.textSecondary),
                      const SizedBox(width: 6),
                      Text(
                        'Expires: ${record.expiryDate}',
                        style: const TextStyle(fontSize: 16, color: AccessibilityTheme.textSecondary, fontWeight: FontWeight.w500),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                ],

                // Timestamp & Tap Action Hint
                Row(
                  children: [
                    const Icon(Icons.access_time, size: 18, color: AccessibilityTheme.primary),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        'Scanned ${HistoryRecord._formatReadableTimestamp(record.timestamp)}',
                        style: const TextStyle(fontSize: 16, color: AccessibilityTheme.primary, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getStatusColor(VerificationStatus status) {
    switch (status) {
      case VerificationStatus.authentic:
        return AccessibilityTheme.success; // #00E676 Green
      case VerificationStatus.expired:
        return AccessibilityTheme.warning; // #FFD600 Yellow
      case VerificationStatus.suspectedCounterfeit:
      case VerificationStatus.recalled:
      case VerificationStatus.revoked:
        return AccessibilityTheme.error; // #FF5252 Red
      case VerificationStatus.offlineError:
        return const Color(0xFF00E5FF); // Cyan
      case VerificationStatus.invalid:
      default:
        return AccessibilityTheme.textSecondary;
    }
  }

  IconData _getStatusIcon(VerificationStatus status) {
    switch (status) {
      case VerificationStatus.authentic:
        return Icons.verified_user;
      case VerificationStatus.expired:
        return Icons.event_busy;
      case VerificationStatus.suspectedCounterfeit:
        return Icons.gpp_maybe;
      case VerificationStatus.recalled:
        return Icons.warning_amber;
      case VerificationStatus.revoked:
        return Icons.cancel_outlined;
      case VerificationStatus.offlineError:
        return Icons.wifi_off;
      case VerificationStatus.invalid:
      default:
        return Icons.help_outline;
    }
  }
}
