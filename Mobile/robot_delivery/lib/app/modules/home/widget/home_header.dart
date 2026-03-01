part of '../home_view.dart';

class HomeHeaderWidget extends StatelessWidget {
  const HomeHeaderWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(24),
          bottomRight: Radius.circular(24),
        ),
        boxShadow: const [
          BoxShadow(color: Colors.black12, spreadRadius: 0, blurRadius: 10),
        ],
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              CustomIconButton(
                icon: Icons.car_crash,
                backGroundColor: AppColors.primary.withValues(alpha: 0.1),
                iconColor: AppColors.primary, 
                iconSize: 18,
                borderRadius: BorderRadius.circular(9999),
                padding: const EdgeInsets.all(9),
                onPressed: () {},
              ),
              const SizedBox(width: 12),
              Text(
                'Robot Delivery',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                  color: Colors.black
                )
              )
            ]
          ),
          CustomIconButton(
            icon: Icons.notifications_none,
            backGroundColor: AppColors.primary.withValues(alpha: 0.1),
            iconColor: AppColors.primary, 
            iconSize: 18,
            borderRadius: BorderRadius.circular(9999),
            padding: const EdgeInsets.all(9),
            onPressed: () {},
          )
        ],
      )
    );
  }
}