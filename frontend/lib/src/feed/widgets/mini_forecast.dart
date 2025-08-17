import 'package:flutter/material.dart';
import '../../api/dto/feed.dart';
import 'formatters.dart';

class MiniForecastRow extends StatelessWidget {
  final List<WeatherDailyItem> items;
  const MiniForecastRow({super.key, required this.items});
  @override
  Widget build(BuildContext context) {
    final days = items.take(3).toList();
    return Row(children: [
      for (int i = 0; i < days.length; i++) ...[
        _MiniDay(item: days[i]),
        if (i != days.length - 1) const VerticalDivider(width: 24),
      ]
    ]);
  }
}

class _MiniDay extends StatelessWidget {
  final WeatherDailyItem item;
  const _MiniDay({required this.item});
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(formatDateShort(item.date), style: Theme.of(context).textTheme.labelMedium),
        const SizedBox(height: 4),
        Text('${formatTemp(item.temp_max_c)} / ${formatMm(item.precipitation_mm)}'),
        const SizedBox(height: 2),
        Text('Wind ${item.wind_kph?.toStringAsFixed(0) ?? '-'} kph', style: Theme.of(context).textTheme.bodySmall),
      ]),
    );
  }
}


