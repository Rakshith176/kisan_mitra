import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../state/feed_provider.dart';
import '../api/dto/feed.dart';
import 'widgets/chips.dart';
import 'widgets/mini_forecast.dart';
import 'widgets/formatters.dart';

class FeedScreen extends ConsumerWidget {
  final String clientId;
  final String language;
  const FeedScreen({super.key, required this.clientId, required this.language});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifierProvider = feedNotifierProvider(clientId);
    // Hydrate cache once when building the screen
    ref.read(notifierProvider.notifier).hydrateFromCache();
    // Also trigger a one-time refresh on first open
    ref.read(notifierProvider.notifier).triggerInitialRefresh();
    final state = ref.watch(notifierProvider);
    return RefreshIndicator(
      onRefresh: () => ref.read(notifierProvider.notifier).refresh(),
      child: Builder(builder: (context) {
        return state.feed.when(
          data: (feed) {
            final cards = feed?.cards ?? [];
            return ListView(
              children: [
                if (state.isStale)
                  Container(
                    margin: const EdgeInsets.all(12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: Colors.amber.shade50, borderRadius: BorderRadius.circular(8)),
                    child: Row(children: const [Icon(Icons.info, color: Colors.amber), SizedBox(width: 8), Expanded(child: Text('Showing cached feed (stale). Pull to refresh.'))]),
                  ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Row(children: [
                    Text('Feed', style: Theme.of(context).textTheme.titleMedium),
                    const Spacer(),
                    IconButton(onPressed: () => ref.read(notifierProvider.notifier).refresh(), icon: const Icon(Icons.refresh)),
                  ]),
                ),
                if (cards.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(24.0),
                    child: Center(child: Text('No cards yet. Update your profile or pull to refresh.')),
                  ),
                for (final c in cards) _FeedCardWidget(card: c, language: language),
              ],
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => ListView(children: [
            const SizedBox(height: 100),
            Center(child: Text('Failed to load feed')), 
            TextButton(onPressed: () => ref.read(notifierProvider.notifier).refresh(), child: const Text('Retry')),
          ]),
        );
      }),
    );
  }
}

class _FeedCardWidget extends StatelessWidget {
  final FeedCard card;
  final String language;
  const _FeedCardWidget({required this.card, required this.language});

  @override
  Widget build(BuildContext context) {
    final type = card.data['card_type'] as String?;
    if (type == 'weather') {
      final data = WeatherCardData.fromJson(card.data);
      return _WeatherCardView(data: data, language: language);
    }
    if (type == 'market_prices') {
      final data = MarketPricesCardData.fromJson(card.data);
      return _MarketCardView(data: data, language: language);
    }
    if (type == 'crop_tip') {
      final data = CropTipsCardData.fromJson(card.data);
      return _CropTipCardView(data: data, language: language);
    }
    return _GenericCardView(raw: card.data, language: language);
  }
}

class _WeatherCardView extends StatelessWidget {
  final WeatherCardData data;
  final String language;
  const _WeatherCardView({required this.data, required this.language});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            const Icon(Icons.cloud, color: Colors.blueGrey),
            const SizedBox(width: 8),
            Expanded(child: Text(localized(data.title, language), style: Theme.of(context).textTheme.titleMedium)),
            if (data.risk_tags.isNotEmpty) SeverityChip(severity: (data.risk_tags.first['severity'] ?? 'low') as String),
          ]),
          const SizedBox(height: 8),
          Row(children: [
            DateRangeChip(start: data.action_window_start, end: data.action_window_end),
          ]),
          const SizedBox(height: 12),
          if (data.recommendations.isNotEmpty)
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              for (final r in data.recommendations.take(3))
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.check_circle, color: Colors.green),
                  title: Text(localized(r, language)),
                  dense: true,
                  visualDensity: VisualDensity.compact,
                ),
            ]),
          const SizedBox(height: 8),
          MiniForecastRow(items: data.forecast_days),
          const SizedBox(height: 8),
          ExpansionTile(
            tilePadding: EdgeInsets.zero,
            title: const Text('Details'),
            children: [
              if (data.analysis != null) Text(localized(data.analysis!, language)),
              const SizedBox(height: 8),
              const Text('Advisories are informational; verify locally.', style: TextStyle(fontSize: 12)),
            ],
          ),
        ]),
      ),
    );
  }
}

class _MarketCardView extends StatelessWidget {
  final MarketPricesCardData data;
  final String language;
  const _MarketCardView({required this.data, required this.language});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            const Icon(Icons.store, color: Colors.brown),
            const SizedBox(width: 8),
            Expanded(child: Text(localized(data.title, language), style: Theme.of(context).textTheme.titleMedium)),
            FreshnessChip(date: data.freshness_date),
          ]),
          const SizedBox(height: 12),
          if (data.items.isNotEmpty) _TopMandiHighlight(item: data.items.first),
          const SizedBox(height: 8),
          _MandiTable(items: data.items.take(5).toList()),
          const SizedBox(height: 8),
          if (data.recommendations.isNotEmpty)
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              for (final r in data.recommendations.take(3))
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.tips_and_updates, color: Colors.indigo),
                  title: Text(localized(r, language)),
                  dense: true,
                  visualDensity: VisualDensity.compact,
                ),
            ]),
          const SizedBox(height: 8),
          const Text('Prices vary; check local mandi before transporting.', style: TextStyle(fontSize: 12)),
        ]),
      ),
    );
  }
}

class _CropTipCardView extends StatelessWidget {
  final CropTipsCardData data;
  final String language;
  const _CropTipCardView({required this.data, required this.language});
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            const Icon(Icons.agriculture, color: Colors.green),
            const SizedBox(width: 8),
            Expanded(child: Text(localized(data.title, language), style: Theme.of(context).textTheme.titleMedium)),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(12)),
              child: Text(localized(data.crop_name, language), style: const TextStyle(color: Colors.green)),
            ),
          ]),
          const SizedBox(height: 8),
          for (final v in data.body_variants.take(3))
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.check, color: Colors.green),
              title: Text(localized(v, language)),
              dense: true,
              visualDensity: VisualDensity.compact,
            ),
        ]),
      ),
    );
  }
}

class _GenericCardView extends StatelessWidget {
  final Map<String, dynamic> raw;
  final String language;
  const _GenericCardView({required this.raw, required this.language});

  String _localize(dynamic v) {
    if (v is Map<String, dynamic>) {
      final lt = LocalizedText.fromJson(v);
      return localized(lt, language);
    }
    return v?.toString() ?? '';
  }

  @override
  Widget build(BuildContext context) {
    final cardType = (raw['card_type'] as String?) ?? 'card';
    final title = _localize(raw['title']);
    final variants = (raw['body_variants'] as List?)?.cast<dynamic>() ?? const [];
    final severity = raw['severity'] as String?;

    return Card(
      margin: const EdgeInsets.all(12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            const Icon(Icons.info_outline), const SizedBox(width: 8),
            Expanded(child: Text(title.isEmpty ? cardType : title, style: Theme.of(context).textTheme.titleMedium)),
            if (severity != null) SeverityChip(severity: severity),
          ]),
          const SizedBox(height: 8),
          for (final v in variants.take(3))
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 2),
              child: Text(_localize(v)),
            ),
          if (variants.isEmpty) Text(cardType, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 8),
          ExpansionTile(
            tilePadding: EdgeInsets.zero,
            title: const Text('Details'),
            children: [
              Text(raw.toString(), style: const TextStyle(fontSize: 12)),
            ],
          ),
        ]),
      ),
    );
  }
}

class _TopMandiHighlight extends StatelessWidget {
  final MarketPriceItem item;
  const _TopMandiHighlight({required this.item});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(12)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            Expanded(child: Text(item.market_name, style: const TextStyle(fontWeight: FontWeight.w600))),
            Text('${formatInr(item.price_modal ?? item.price_max)}/q', style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
            const SizedBox(width: 8),
            Text(formatKm(item.distance_km)),
          ]),
          const SizedBox(height: 4),
          Text(item.commodity, style: const TextStyle(fontSize: 12, color: Colors.grey)),
        ],
      ),
    );
  }
}

class _MandiTable extends StatelessWidget {
  final List<MarketPriceItem> items;
  const _MandiTable({required this.items});
  @override
  Widget build(BuildContext context) {
    return DataTable(columns: const [
      DataColumn(label: Text('Market')),
      DataColumn(label: Text('Commodity')),  // Added missing Commodity column
      DataColumn(label: Text('Modal')),
      DataColumn(label: Text('Km')),
      DataColumn(label: Text('Date')),
    ], rows: [
      for (final i in items)
        DataRow(cells: [
          DataCell(Text(i.market_name)),
          DataCell(Text(i.commodity)),  // Display the commodity (crop name)
          DataCell(Text('${formatInr(i.price_modal ?? i.price_max)}/q')),
          DataCell(Text(formatKm(i.distance_km))),
          DataCell(Text(i.date == null ? '-' : formatDateShort(i.date!))),
        ])
    ]);
  }
}


