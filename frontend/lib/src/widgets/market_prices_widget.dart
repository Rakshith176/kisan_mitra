import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../state/market_prices_provider.dart';
import '../services/market_prices_service.dart';

class MarketPricesWidget extends ConsumerStatefulWidget {
  final String? clientId;
  final String? location;
  
  const MarketPricesWidget({
    super.key,
    this.clientId,
    this.location,
  });

  @override
  ConsumerState<MarketPricesWidget> createState() => _MarketPricesWidgetState();
}

class _MarketPricesWidgetState extends ConsumerState<MarketPricesWidget> {
  final List<String> availableCrops = [
    'WHEAT',
    'RICE', 
    'MAIZE',
    'COTTON',
    'SUGARCANE',
  ];

  @override
  void initState() {
    super.initState();
    // Load initial data for wheat
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(marketPricesProvider.notifier).fetchMarketPrices(
        crop: 'wheat',
        location: widget.location,
        clientId: widget.clientId,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(marketPricesProvider);
    
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with title and refresh button
            Row(
              children: [
                const Icon(
                  Icons.trending_up,
                  color: Colors.green,
                  size: 20,
                ),
                const SizedBox(width: 8),
                const Text(
                  'Live Market Prices',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: () => ref.read(marketPricesProvider.notifier).refresh(),
                  icon: const Icon(Icons.refresh),
                  iconSize: 20,
                ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // Crop selection label
            const Text(
              'Select Crop',
              style: TextStyle(
                fontSize: 14,
                color: Colors.black54,
              ),
            ),
            
            const SizedBox(height: 8),
            
            // Crop selection buttons
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: availableCrops.map((crop) {
                  final isSelected = state.selectedCrop.toLowerCase() == crop.toLowerCase();
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: FilterChip(
                      label: Text(
                        crop,
                        style: TextStyle(
                          color: isSelected ? Colors.white : Colors.black87,
                          fontSize: 12,
                        ),
                      ),
                      selected: isSelected,
                      onSelected: (selected) {
                        if (selected) {
                          ref.read(marketPricesProvider.notifier).selectCrop(crop.toLowerCase());
                        }
                      },
                      backgroundColor: Colors.grey[200],
                      selectedColor: Colors.green,
                      checkmarkColor: Colors.white,
                    ),
                  );
                }).toList(),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Market data display
            _buildMarketDataDisplay(state),
          ],
        ),
      ),
    );
  }

  Widget _buildMarketDataDisplay(MarketPricesState state) {
    return state.data.when(
      data: (marketData) {
        if (marketData == null || marketData.prices.isEmpty) {
          return Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Text(
                marketData?.message ?? 'No market data available for selected crop',
                style: const TextStyle(
                  color: Colors.grey,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          );
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Summary info
            Row(
              children: [
                Text(
                  '${marketData.totalMarkets} markets',
                  style: const TextStyle(
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
                const Spacer(),
                if (marketData.lastUpdated != null)
                  Text(
                    'Updated: ${_formatDate(marketData.lastUpdated!)}',
                    style: const TextStyle(
                      fontSize: 12,
                      color: Colors.grey,
                    ),
                  ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // Market prices list
            ...marketData.prices.take(5).map((price) => _buildPriceItem(price)),
            
            if (marketData.prices.length > 5)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  '... and ${marketData.prices.length - 5} more markets',
                  style: const TextStyle(
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
              ),
          ],
        );
      },
      loading: () => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        child: const Center(
          child: CircularProgressIndicator(),
        ),
      ),
      error: (error, stack) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.red[50],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Center(
          child: Column(
            children: [
              const Icon(
                Icons.error_outline,
                color: Colors.red,
                size: 24,
              ),
              const SizedBox(height: 8),
              Text(
                'Failed to load market data',
                style: const TextStyle(
                  color: Colors.red,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => ref.read(marketPricesProvider.notifier).refresh(),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPriceItem(MarketPrice price) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              price.marketName,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            flex: 1,
            child: Text(
              price.modalPrice != null 
                  ? '₹${price.modalPrice!.toStringAsFixed(0)}'
                  : 'N/A',
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Colors.green,
              ),
              textAlign: TextAlign.end,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            price.unit ?? '₹/quintal',
            style: const TextStyle(
              fontSize: 12,
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
}
