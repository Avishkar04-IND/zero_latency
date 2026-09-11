import 'package:flutter/material.dart';

class TalkBackSemantics extends StatelessWidget {
  final Widget child;
  final String label;
  final String? hint;
  final VoidCallback? onTap;
  final bool isHeader;

  const TalkBackSemantics({
    super.key,
    required this.child,
    required this.label,
    this.hint,
    this.onTap,
    this.isHeader = false,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      hint: hint,
      header: isHeader,
      button: onTap != null,
      onTap: onTap,
      excludeSemantics: true, // Prevents inner elements from duplicating voice readouts
      child: InkWell(
        onTap: onTap,
        child: child,
      ),
    );
  }
}
