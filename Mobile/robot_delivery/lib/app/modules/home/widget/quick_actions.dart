part of '../home_view.dart';

class QuickActions extends StatelessWidget {
  const QuickActions({super.key});

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
              hasShadow: true,
              icon: Icons.add,
              iconColor: AppColors.primary,
              backGroundColor: AppColors.white,
              onPressed: () {
                Get.toNamed(Routes.CREATE_ORDER);
              },
              tooltip: AppTranslationKeys.newOrder.tr,
            ),
            CustomIconButton(
              hasShadow: true,
              icon: Icons.add_location,
              iconColor: AppColors.primary,
              backGroundColor: AppColors.white,
              onPressed: () {},
              tooltip: AppTranslationKeys.address.tr,
            ),
            CustomIconButton(
              hasShadow: true,
              icon: Icons.history,
              iconColor: AppColors.primary,
              backGroundColor: AppColors.white,
              onPressed: () {
                Get.find<MainController>().setTabIndex(AppNavTab.orders.index);
              },
              tooltip: AppTranslationKeys.history.tr,
            ),
            CustomIconButton(
              hasShadow: true,
              icon: Icons.contact_support,
              iconColor: AppColors.primary,
              backGroundColor: AppColors.white,
              onPressed: () {},
              tooltip: AppTranslationKeys.support.tr,
            ),
          ],
        ),
      ],
    );
  }
}
