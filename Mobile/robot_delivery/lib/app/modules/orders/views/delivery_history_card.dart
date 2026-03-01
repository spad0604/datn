part of 'orders_view.dart';

class DeliveryHistoryCard extends StatelessWidget {
  const DeliveryHistoryCard({super.key, required this.item});

  final DeliveryHistoryItem item;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.slate100, width: 1),
        boxShadow: const [
          BoxShadow(
            color: AppColors.black05,
            blurRadius: 14,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: item.leadingBg,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(item.leadingIcon, color: item.leadingFg, size: 22),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.title,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w800,
                          color: AppColors.slate900,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${AppTranslationKeys.sender.tr} ${item.sender}',
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                          color: AppColors.slate600,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        item.dateTimeText,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: AppColors.slate400,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                getItemStatusWidget(item.status),
              ],
            ),
            if (item.showMapPreview) ...[
              const SizedBox(height: 12),
              Container(
                height: 96,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: AppColors.grayF6,
                  borderRadius: BorderRadius.circular(18),
                ),
                child: const Center(
                  child: Icon(
                    Icons.map_outlined,
                    color: AppColors.slate300,
                    size: 30,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
