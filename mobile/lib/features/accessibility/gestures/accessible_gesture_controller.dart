import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';

class AccessibleGestureController extends StatelessWidget {
  final Widget child;
  final VoidCallback? onDoubleTapScan;
  final VoidCallback? onSwipeRightNext;
  final VoidCallback? onSwipeLeftPrevious;
  final VoidCallback? onSwipeDownRepeat;
  final VoidCallback? onSwipeUpHome;
  final VoidCallback? onLongPressAssistant;
  final VoidCallback? onTwoFingerTapHelp;
  final TTSService? ttsService;

  const AccessibleGestureController({
    super.key,
    required this.child,
    this.onDoubleTapScan,
    this.onSwipeRightNext,
    this.onSwipeLeftPrevious,
    this.onSwipeDownRepeat,
    this.onSwipeUpHome,
    this.onLongPressAssistant,
    this.onTwoFingerTapHelp,
    this.ttsService,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onDoubleTap: () {
        HapticsService.capture();
        ttsService?.speak("Scanning started.");
        onDoubleTapScan?.call();
      },
      onLongPress: () {
        HapticsService.codeDetected();
        ttsService?.speak("Voice Assistant opened. Listening for command.");
        onLongPressAssistant?.call();
      },
      onHorizontalDragEnd: (details) {
        if ((details.primaryVelocity ?? 0) < 0) {
          // Swipe Left -> Previous
          HapticsService.scanningTick();
          ttsService?.speak("Previous item.");
          onSwipeLeftPrevious?.call();
        } else if ((details.primaryVelocity ?? 0) > 0) {
          // Swipe Right -> Next
          HapticsService.scanningTick();
          ttsService?.speak("Next item.");
          onSwipeRightNext?.call();
        }
      },
      onVerticalDragEnd: (details) {
        if ((details.primaryVelocity ?? 0) < 0) {
          // Swipe Up -> Home
          HapticsService.scanningTick();
          ttsService?.speak("Returning to Home screen.");
          onSwipeUpHome?.call();
        } else if ((details.primaryVelocity ?? 0) > 0) {
          // Swipe Down -> Repeat
          HapticsService.scanningTick();
          onSwipeDownRepeat?.call();
        }
      },
      child: RawGestureDetector(
        gestures: {
          _TwoFingerTapGestureRecognizer: GestureRecognizerFactoryWithHandlers<_TwoFingerTapGestureRecognizer>(
            () => _TwoFingerTapGestureRecognizer(),
            (_TwoFingerTapGestureRecognizer instance) {
              instance.onTwoFingerTap = () {
                HapticsService.codeDetected();
                ttsService?.speak("Help menu. Double tap to scan medicine. Swipe right for next option. Swipe down to repeat audio.");
                onTwoFingerTapHelp?.call();
              };
            },
          ),
        },
        child: child,
      ),
    );
  }
}

class _TwoFingerTapGestureRecognizer extends OneSequenceGestureRecognizer {
  VoidCallback? onTwoFingerTap;
  int _pointerCount = 0;

  @override
  void addAllowedPointer(PointerDownEvent event) {
    _pointerCount++;
    if (_pointerCount == 2) {
      onTwoFingerTap?.call();
    }
    startTrackingPointer(event.pointer);
  }

  @override
  void handleEvent(PointerEvent event) {
    if (event is PointerUpEvent || event is PointerCancelEvent) {
      _pointerCount = 0;
    }
  }

  @override
  String get debugDescription => 'twoFingerTap';

  @override
  void didStopTrackingLastPointer(int pointer) {}
}
