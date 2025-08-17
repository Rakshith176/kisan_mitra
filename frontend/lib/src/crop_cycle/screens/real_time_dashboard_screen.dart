import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/real_time_weather_widget.dart';
import '../widgets/real_time_market_widget.dart';
import '../widgets/data_integration_status_widget.dart';
import '../services/crop_cycle_api_service.dart';

class RealTimeDashboardScreen extends ConsumerStatefulWidget {
  final String clientId;
  final double? latitude;
  final double? longitude;
  final String? state;
  final String? district;

  const RealTimeDashboardScreen({
    super.key,
    required this.clientId,
    this.latitude,
    this.longitude,
    this.state,
    this.district,
  });

  @override
  ConsumerState<RealTimeDashboardScreen> createState() => _RealTimeDashboardScreenState();
}

class _RealTimeDashboardScreenState extends ConsumerState<RealTimeDashboardScreen> {
  Map<String, dynamic>? soilData;
  bool isLoadingSoil = false;
  String? soilError;

  @override
  void initState() {
    super.initState();
    _fetchSoilData();
  }

  Future<void> _fetchSoilData() async {
    if (widget.latitude == null || widget.longitude == null) return;
    
    setState(() {
      isLoadingSoil = true;
      soilError = null;
    });

    try {
      final apiService = CropCycleApiService();
      // Use a default pincode for now - should come from farmer profile
      final soil = await apiService.getRealTimeSoilData('560001', widget.clientId);
      
      setState(() {
        soilData = soil;
        isLoadingSoil = false;
      });
    } catch (e) {
      setState(() {
        soilError = e.toString();
        isLoadingSoil = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📊 Real-Time Data Dashboard'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            onPressed: () {
              // Refresh all data
              setState(() {});
            },
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh All Data',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          setState(() {});
        },
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header with summary
              _buildDashboardHeader(),
              const SizedBox(height: 24),
              
              // Data Integration Status
              DataIntegrationStatusWidget(clientId: widget.clientId),
              const SizedBox(height: 24),
              
              // Weather and Market Data Row
              Row(
                children: [
                  Expanded(
                    child: RealTimeWeatherWidget(
                      latitude: widget.latitude ?? 12.9716,
                      longitude: widget.longitude ?? 77.5946,
                      clientId: widget.clientId,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: RealTimeMarketWidget(
                      clientId: widget.clientId,
                      state: widget.state ?? 'Karnataka',
                      district: widget.district,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              
              // Soil Health Data
              _buildSoilHealthSection(),
              const SizedBox(height: 24),
              
              // Data Insights and Recommendations
              _buildDataInsightsSection(),
              const SizedBox(height: 24),
              
              // Data Source Information
              _buildDataSourceInfoSection(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDashboardHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade600, Colors.blue.shade800],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.shade200,
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.dashboard,
                color: Colors.white,
                size: 32,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Real-Time Agricultural Data',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Live weather, market prices, and soil health data for informed farming decisions',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.white.withOpacity(0.9),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Quick Stats
          Row(
            children: [
              _buildQuickStat('🌤️ Weather', 'Live', Colors.green.shade300),
              const SizedBox(width: 16),
              _buildQuickStat('💰 Markets', 'Active', Colors.yellow.shade300),
              const SizedBox(width: 16),
              _buildQuickStat('🌱 Soil', 'Updated', Colors.orange.shade300),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStat(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.white,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 10,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSoilHealthSection() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.eco, color: Colors.green, size: 24),
                const SizedBox(width: 8),
                Text(
                  '🌱 Soil Health Data',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: _fetchSoilData,
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh',
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            if (isLoadingSoil)
              const Center(child: CircularProgressIndicator())
            else if (soilError != null)
              _buildSoilErrorState()
            else if (soilData != null && soilData!.isNotEmpty)
              _buildSoilContent()
            else
              _buildSoilNoDataState(),
          ],
        ),
      ),
    );
  }

  Widget _buildSoilErrorState() {
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
            'Soil data unavailable',
            style: TextStyle(color: Colors.red.shade700),
          ),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _fetchSoilData,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildSoilNoDataState() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: const Center(
        child: Text('No soil data available for this location'),
      ),
    );
  }

  Widget _buildSoilContent() {
    final soil = soilData!;
    
    return Column(
      children: [
        // Soil Type and Basic Info
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.green.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.green.shade200),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      soil['soil_type'] ?? 'Unknown',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.green.shade700,
                      ),
                    ),
                    Text(
                      '${soil['district'] ?? 'Unknown'}, ${soil['state'] ?? 'Unknown'}',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.green.shade600,
                      ),
                    ),
                  ],
                ),
              ),
              Column(
                children: [
                  _buildSoilMetric(
                    'pH Level',
                    '${soil['ph_level']?.toStringAsFixed(1) ?? 'N/A'}',
                    Icons.science,
                  ),
                  const SizedBox(height: 8),
                  _buildSoilMetric(
                    'Organic Carbon',
                    '${soil['organic_carbon']?.toStringAsFixed(1) ?? 'N/A'}%',
                    Icons.eco,
                  ),
                ],
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Nutrient Levels
        Text(
          'Nutrient Levels',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        
        Row(
          children: [
            Expanded(
              child: _buildNutrientCard(
                'Nitrogen (N)',
                soil['nitrogen_n'] ?? 0.0,
                'kg/ha',
                Colors.blue,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildNutrientCard(
                'Phosphorus (P)',
                soil['phosphorus_p'] ?? 0.0,
                'kg/ha',
                Colors.orange,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildNutrientCard(
                'Potassium (K)',
                soil['potassium_k'] ?? 0.0,
                'kg/ha',
                Colors.purple,
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Soil Recommendations
        _buildSoilRecommendations(soil),
      ],
    );
  }

  Widget _buildSoilMetric(String label, String value, IconData icon) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: Colors.green.shade600),
        const SizedBox(width: 4),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              value,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.green.shade700,
              ),
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.green.shade600,
                fontSize: 10,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildNutrientCard(String nutrient, double value, String unit, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            nutrient,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 4),
          Text(
            '${value.toStringAsFixed(1)} $unit',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSoilRecommendations(Map<String, dynamic> soil) {
    final ph = soil['ph_level'] ?? 7.0;
    final organicCarbon = soil['organic_carbon'] ?? 0.0;
    final nitrogen = soil['nitrogen_n'] ?? 0.0;
    
    List<String> recommendations = [];
    
    if (ph < 6.0) {
      recommendations.add('🔴 pH is too low - consider adding lime to raise pH');
    } else if (ph > 8.0) {
      recommendations.add('🔴 pH is too high - consider adding sulfur to lower pH');
    } else {
      recommendations.add('✅ pH level is optimal for most crops');
    }
    
    if (organicCarbon < 0.5) {
      recommendations.add('🟡 Low organic carbon - add organic matter like compost');
    } else {
      recommendations.add('✅ Organic carbon level is good');
    }
    
    if (nitrogen < 140) {
      recommendations.add('🟡 Nitrogen levels are low - consider nitrogen fertilizers');
    } else {
      recommendations.add('✅ Nitrogen levels are adequate');
    }
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb_outline, color: Colors.blue, size: 20),
              const SizedBox(width: 8),
              Text(
                'Soil Recommendations',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
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
                color: Colors.blue,
              ),
            ),
          )),
        ],
      ),
    );
  }

  Widget _buildDataInsightsSection() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.insights, color: Colors.purple, size: 24),
                const SizedBox(width: 8),
                Text(
                  '💡 Data Insights & Recommendations',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.purple.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.purple.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Farming Recommendations Based on Real-Time Data',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.purple.shade700,
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  _buildInsightItem(
                    '🌤️ Weather-Based Planning',
                    'Monitor weather forecasts for optimal planting and harvesting times',
                    Colors.blue,
                  ),
                  const SizedBox(height: 8),
                  
                  _buildInsightItem(
                    '💰 Market Intelligence',
                    'Track price trends to maximize profits and plan crop selection',
                    Colors.green,
                  ),
                  const SizedBox(height: 8),
                  
                  _buildInsightItem(
                    '🌱 Soil Health Management',
                    'Use soil data to optimize fertilizer application and crop selection',
                    Colors.orange,
                  ),
                  const SizedBox(height: 8),
                  
                  _buildInsightItem(
                    '📊 Data-Driven Decisions',
                    'Combine all data sources for informed agricultural planning',
                    Colors.purple,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInsightItem(String title, String description, Color color) {
    return Row(
      children: [
        Icon(Icons.check_circle, color: color, size: 20),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              Text(
                description,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: color,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDataSourceInfoSection() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.info_outline, color: Colors.grey, size: 24),
                const SizedBox(width: 8),
                Text(
                  'ℹ️ Data Source Information',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            _buildDataSourceItem(
              '🌤️ Weather Data',
              'OpenMeteo API',
              'Real-time weather conditions and forecasts',
              Colors.blue,
            ),
            const SizedBox(height: 8),
            
            _buildDataSourceItem(
              '💰 Market Data',
              'Agmarknet & Karnataka Govt Portal',
              'Live market prices and trends',
              Colors.green,
            ),
            const SizedBox(height: 8),
            
            _buildDataSourceItem(
              '🌱 Soil Health',
              'Government Soil Portals',
              'Soil nutrient analysis and recommendations',
              Colors.orange,
            ),
            const SizedBox(height: 8),
            
            _buildDataSourceItem(
              '📅 Crop Calendars',
              'ICAR & Agricultural Portals',
              'Seasonal planting and harvesting guides',
              Colors.purple,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDataSourceItem(String title, String source, String description, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(Icons.verified, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                Text(
                  source,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: color,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  description,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: color,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
