import 'package:flutter/material.dart';

class CustomButton extends StatelessWidget {
  final String text;
  final IconData? prefixIcon;
  final IconData? suffixIcon;
  final Color textColor;
  final Color backgroundColor;
  final Color? borderColor;
  final VoidCallback onPressed;

  const CustomButton({
    super.key,
    required this.text,
    this.prefixIcon,
    this.suffixIcon,
    required this.textColor,
    required this.backgroundColor,
    this.borderColor,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.all(Radius.circular(24)),
          color: backgroundColor,
          border: borderColor != null ? Border.all(color: borderColor!, width: 1) : null,
        ),
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Center(
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (prefixIcon != null)
                Icon(
                  prefixIcon,
                  color: textColor,
                  size: 18,
                ),
              if (prefixIcon != null) const SizedBox(width: 8),
              Text(
                text,
                style: TextStyle(
                  color: textColor,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
              if (suffixIcon != null) const SizedBox(width: 8),
              if (suffixIcon != null)
                Icon(
                  suffixIcon,
                  color: textColor,
                  size: 18,
                ),
            ],
          ),
        ),
      ),
    );
  }
}