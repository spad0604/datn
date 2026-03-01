part of '../home_view.dart';

class QuickActions extends StatelessWidget {
  QuickActions({super.key});

  final mainController = Get.find<MainController>();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          AppTranslationKeys.quickActions.tr,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            CustomIconButton(
              icon: Icons.add,
              iconColor: AppColors.primary,
              backGroundColor: AppColors.white,
              onPressed: (){
                Get.toNamed(Routes.CREATE_ORDER);
              },
              tooltip: 'New Order',
            ),
            CustomIconButton(
              icon: Icons.add_location,
              iconColor: AppColors.primary,
              backGroundColor: AppColors.white,
              onPressed: (){},
              tooltip: 'Address',
            ),
            CustomIconButton(
              icon: Icons.history,
              iconColor: AppColors.primary,
              backGroundColor: AppColors.white,
              onPressed: (){},
              tooltip: 'History',
            ),
            CustomIconButton(
              icon: Icons.contact_support,
              iconColor: AppColors.primary,
              backGroundColor: AppColors.white,
              onPressed: (){},
              tooltip: 'Support',
            ),
          ],
        ),
      ],
    );
  }
}
