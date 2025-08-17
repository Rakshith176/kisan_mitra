import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/crop_cycle_api_service.dart';

class RealTimeMarketWidget extends ConsumerStatefulWidget {
  final String clientId;
  final String? selectedCrop;
  final String? state;
  final String? district;

  const RealTimeMarketWidget({
    super.key,
    required this.clientId,
    this.selectedCrop,
    this.state,
    this.district,
  });

  @override
  ConsumerState<RealTimeMarketWidget> createState() => _RealTimeMarketWidgetState();
}

class _RealTimeMarketWidgetState extends ConsumerState<RealTimeMarketWidget> {
  List<Map<String, dynamic>>? marketData;
  Map<String, dynamic>? priceTrends;
  bool isLoading = false;
  String? error;
  String selectedCrop = 'wheat'; // Default crop

  final List<String> popularCrops = [
    'wheat', 'rice', 'maize', 'cotton', 'sugarcane', 'pulses', 'oilseeds'
  ];

  @override
  void initState() {
    super.initState();
    selectedCrop = widget.selectedCrop ?? 'wheat';
    _fetchMarketData();
  }

  Future<void> _fetchMarketData() async {
    setState(() {
      isLoading = true;
      error = null;
    });

    try {
      final apiService = CropCycleApiService();
      
      // Fetch market data for selected crop
      final market = await apiService.getRealTimeMarketData(
        selectedCrop,
        widget.state,
        widget.district,
        widget.clientId,
      );
      
      // Fetch price trends
      final trends = await apiService.getMarketPriceTrends(
        selectedCrop,
        widget.state,
        widget.clientId,
      );

      // Debug logging
      print('Market widget - Market data: $market');
      print('Market widget - Price trends: $trends');
      print('Market widget - Market data type: ${market.runtimeType}');
      print('Market widget - Price trends type: ${trends.runtimeType}');
      
      setState(() {
        marketData = market;
        priceTrends = trends;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.trending_up, color: Colors.green, size: 24),
                const SizedBox(width: 8),
                Text(
                  'Live Market Prices',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: _fetchMarketData,
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh',
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Crop Selector
            _buildCropSelector(),
            const SizedBox(height: 16),
            
            if (isLoading)
              const Center(child: CircularProgressIndicator())
            else if (error != null)
              _buildErrorState()
            else if (marketData != null && marketData!.isNotEmpty)
              _buildMarketContent()
            else
              _buildNoDataState(),
          ],
        ),
      ),
    );
  }

  Widget _buildCropSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Select Crop',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 40,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: popularCrops.length,
            itemBuilder: (context, index) {
              final crop = popularCrops[index];
              final isSelected = crop == selectedCrop;
              
              return GestureDetector(
                onTap: () {
                  setState(() {
                    selectedCrop = crop;
                  });
                  _fetchMarketData();
                },
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: isSelected ? Colors.green.shade100 : Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isSelected ? Colors.green.shade300 : Colors.grey.shade300,
                    ),
                  ),
                  child: Text(
                    crop.toUpperCase(),
                    style: TextStyle(
                      color: isSelected ? Colors.green.shade700 : Colors.grey.shade700,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildErrorState() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade400, size: 32),
          const SizedBox(height: 8),
          Text(
            'Market data unavailable',
            style: TextStyle(color: Colors.red.shade700),
          ),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _fetchMarketData,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildNoDataState() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: const Center(
        child: Text('No market data available for selected crop'),
      ),
    );
  }

  Widget _buildMarketContent() {
    return Column(
      children: [
        // Price Trends Summary
        if (priceTrends != null) ...[
          _buildPriceTrendsSummary(priceTrends!),
          const SizedBox(height: 16),
        ],
        
        // Market Prices by Location
        Text(
          'Market Prices by Location',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        
        // Market Price Cards
        ...marketData!.take(5).map((market) => _buildMarketPriceCard(market)),
        
        if (marketData!.length > 5) ...[
          const SizedBox(height: 8),
          Center(
            child: Text(
              '+${marketData!.length - 5} more markets',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade600,
              ),
            ),
          ),
        ],
        
        const SizedBox(height: 16),
        
        // Market Recommendations
        _buildMarketRecommendations(),
      ],
    );
  }

  Widget _buildPriceTrendsSummary(Map<String, dynamic> trends) {
    final status = trends['status'] ?? 'unknown';
    final trendDirection = trends['trend_direction'] ?? 'stable';
    final recommendations = trends['recommendations'] ?? [];
    
    Color statusColor;
    IconData statusIcon;
    
    switch (trendDirection) {
      case 'rising':
        statusColor = Colors.green;
        statusIcon = Icons.trending_up;
        break;
      case 'falling':
        statusColor = Colors.red;
        statusIcon = Icons.trending_down;
        break;
      default:
        statusColor = Colors.orange;
        statusIcon = Icons.trending_flat;
    }
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(statusIcon, color: statusColor, size: 24),
              const SizedBox(width: 8),
              Text(
                'Price Trend: ${trendDirection.toUpperCase()}',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: statusColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          if (recommendations.isNotEmpty) ...[
            ...recommendations.take(2).map((rec) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  Icon(Icons.lightbulb_outline, size: 16, color: statusColor),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      rec,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: statusColor,
                      ),
                    ),
                  ),
                ],
              ),
            )),
          ],
        ],
      ),
    );
  }

  Widget _buildMarketPriceCard(Map<String, dynamic> market) {
    final mandiName = market['mandi_name'] ?? 'Unknown';
    final district = market['district'] ?? 'Unknown';
    final minPrice = market['min_price'] ?? 0.0;
    final maxPrice = market['max_price'] ?? 0.0;
    final modalPrice = market['modal_price'] ?? 0.0;
    final source = market['source'] ?? 'Unknown';
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade200,
            blurRadius: 2,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  mandiName,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  district,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey.shade600,
                  ),
                ),
                Text(
                  'Source: $source',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey.shade500,
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '₹${modalPrice.toStringAsFixed(0)}',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.green.shade700,
                ),
              ),
              Text(
                '₹${minPrice.toStringAsFixed(0)} - ₹${maxPrice.toStringAsFixed(0)}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey.shade600,
                ),
              ),
              Text(
                'per quintal',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey.shade500,
                  fontSize: 10,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMarketRecommendations() {
    if (marketData == null || marketData!.isEmpty) return const SizedBox.shrink();
    
    final prices = marketData!.map((m) => m['modal_price'] ?? 0.0).where((p) => p > 0).toList();
    if (prices.isEmpty) return const SizedBox.shrink();
    
    final avgPrice = prices.reduce((a, b) => a + b) / prices.length;
    final maxPrice = prices.reduce((a, b) => a > b ? a : b);
    final minPrice = prices.reduce((a, b) => a < b ? a : b);
    
    List<String> recommendations = [];
    
    if (maxPrice > avgPrice * 1.2) {
      recommendations.add('🚀 High prices at ${_getMandiWithPrice(maxPrice)} - consider selling here');
    }
    
    if (minPrice < avgPrice * 0.8) {
      recommendations.add('📉 Low prices at ${_getMandiWithPrice(minPrice)} - avoid selling here');
    }
    
    if (recommendations.isEmpty) {
      recommendations.add('✅ Prices are consistent across markets');
    }
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.insights, color: Colors.blue.shade600, size: 20),
              const SizedBox(width: 8),
              Text(
                'Market Insights',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue.shade700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...recommendations.map((rec) => Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text(
              rec,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.blue.shade700,
              ),
            ),
          )),
        ],
      ),
    );
  }

  String _getMandiWithPrice(double price) {
    final market = marketData!.firstWhere(
      (m) => (m['modal_price'] ?? 0.0) == price,
      orElse: () => {'mandi_name': 'Unknown'},
    );
    return market['mandi_name'] ?? 'Unknown';
  }
}
