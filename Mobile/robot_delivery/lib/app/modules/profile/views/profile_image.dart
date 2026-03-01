import 'package:flutter/material.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

class ProfileImage extends StatelessWidget {
  const ProfileImage({super.key, this.imageUrl});

  final String? imageUrl;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        CircleAvatar(
          radius: 36,
          backgroundImage: imageUrl != null ? NetworkImage(imageUrl!) : null,
          child: imageUrl == null ? const Icon(Icons.person, size: 50) : null,
        ),
        Positioned(
          bottom: -4,
          right: -4,
          child: Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              color: AppColors.white,
              shape: BoxShape.circle,
            ),
            child: Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: AppColors.primary,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.camera_alt_outlined, size: 16, color: AppColors.white,),
            ),
          ),
        ),
      ],
    );
  }
}