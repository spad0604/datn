import 'package:flutter/material.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

class CustomTextfield extends StatelessWidget {
  final String hintText;
  final IconData? prefixIcon;
  final IconData? suffixIcon;
  final TextEditingController? controller;
  final bool isPassword;
  final String title;
  final bool isRequired;
  final String? Function(String?)? validator;
  final Function()? onSuffixIconPressed;
  final ValueChanged<String>? onChanged;
  final bool readOnly;
  final VoidCallback? onTap;

  const CustomTextfield({
    super.key,
    required this.hintText,
    this.prefixIcon,
    this.suffixIcon,
    this.controller,
    this.isPassword = false,
    required this.title,
    this.isRequired = false,
    this.validator,
    this.onSuffixIconPressed,
    this.onChanged,
    this.readOnly = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final border = OutlineInputBorder(
      borderRadius: BorderRadius.circular(24),
      borderSide: const BorderSide(color: AppColors.slate300, width: 1),
    );

    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: AppColors.slate900,
              ),
            ),
            const SizedBox(width: 8),
            if (isRequired)
              const Text(
                ' *',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: Colors.red,
                ),
              ),
          ],
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          obscureText: isPassword,
          onChanged: onChanged,
          readOnly: readOnly,
          onTap: onTap,
          validator: validator,
          decoration: InputDecoration(
            filled: true,
            fillColor: AppColors.white,
            hintText: hintText,
            hintStyle: const TextStyle(
              color: AppColors.slate400,
              fontWeight: FontWeight.w400,
            ),
            prefixIcon: prefixIcon != null
                ? Icon(prefixIcon, color: AppColors.slate400)
                : null,
            suffixIcon: suffixIcon != null
                ? IconButton(
                    icon: Icon(suffixIcon, color: AppColors.slate400),
                    onPressed: onSuffixIconPressed,
                  )
                : null,
            enabledBorder: border,
            focusedBorder: border,
            errorBorder: border.copyWith(
              borderSide: const BorderSide(color: AppColors.errorAlt, width: 1),
            ),
            focusedErrorBorder: border.copyWith(
              borderSide: const BorderSide(color: AppColors.errorAlt, width: 1),
            ),
            border: border,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 18,
            ),
          ),
        ),
      ],
    );
  }
}
