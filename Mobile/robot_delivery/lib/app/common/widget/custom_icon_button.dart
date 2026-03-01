import 'package:flutter/material.dart';

class CustomIconButton extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final Color backGroundColor;
  final double iconSize;
  final VoidCallback onPressed;
  final BorderRadius? borderRadius;
  final String? tooltip;
  final EdgeInsets? padding;

  const CustomIconButton({
    super.key,
    required this.icon,
    required this.iconColor,
    required this.backGroundColor,
    this.iconSize = 24,
    this.borderRadius,
    this.tooltip,
    this.padding,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        GestureDetector(
          onTap: onPressed,
          child: Container(
            decoration: BoxDecoration(
              color: backGroundColor,
              borderRadius: borderRadius ?? BorderRadius.circular(16),
            ),
            child: Padding(
              padding: padding ?? const EdgeInsets.all(18),
              child: Icon(icon, color: iconColor, size: iconSize),
            ),
          ),
        ),
        tooltip != null ? const SizedBox(height: 4) : const SizedBox.shrink(),
        tooltip != null
            ? Text(
                tooltip!,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
                maxLines: 1,
              )
            : const SizedBox.shrink(),
      ],
    );
  }
}
