import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/crop_cycle_api_service.dart';

class RealTimeWeatherWidget extends ConsumerStatefulWidget {
  final double latitude;
  final double longitude;
  final String clientId;

  const RealTimeWeatherWidget({
    super.key,
    required this.latitude,
    required this.longitude,
    required this.clientId,
  });

  @override
  ConsumerState<RealTimeWeatherWidget> createState() => _RealTimeWeatherWidgetState();
}

class _RealTimeWeatherWidgetState extends ConsumerState<RealTimeWeatherWidget> {
  Map<String, dynamic>? weatherData;
  List<Map<String, dynamic>>? forecastData;
  bool isLoading = false;
  String? error;

  @override
  void initState() {
    super.initState();
    _fetchWeatherData();
  }

  Future<void> _fetchWeatherData() async {
    setState(() {
      isLoading = true;
      error = null;
    });

    try {
      final apiService = CropCycleApiService();
      
      // Fetch current weather
      final currentWeather = await apiService.getRealTimeWeather(
        widget.latitude,
        widget.longitude,
        widget.clientId,
      );
      
      // Fetch weather forecast
      final forecast = await apiService.getWeatherForecast(
        widget.latitude,
        widget.longitude,
        widget.clientId,
      );

      // Debug logging
      print('Weather widget - Current weather data: $currentWeather');
      print('Weather widget - Forecast data: $forecast');
      print('Weather widget - Current weather type: ${currentWeather.runtimeType}');
      print('Weather widget - Forecast type: ${forecast.runtimeType}');
      
      setState(() {
        weatherData = currentWeather;
        forecastData = forecast;
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
                const Icon(Icons.wb_sunny, color: Colors.orange, size: 24),
                const SizedBox(width: 8),
                Text(
                  'Real-Time Weather',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: _fetchWeatherData,
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh',
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            if (isLoading)
              const Center(child: CircularProgressIndicator())
            else if (error != null)
              _buildErrorState()
            else if (weatherData != null)
              _buildWeatherContent()
            else
              _buildNoDataState(),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(Icons.error_outline, color: Colors.red, size: 32),
          const SizedBox(height: 8),
          Text(
            'Weather data unavailable',
            style: TextStyle(color: Colors.red),
          ),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _fetchWeatherData,
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
        color: Colors.grey.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.withOpacity(0.3)),
      ),
      child: const Center(
        child: Text('No weather data available'),
      ),
    );
  }

  Widget _buildWeatherContent() {
    // Add type safety check
    if (weatherData == null || weatherData is! Map<String, dynamic>) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.orange.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.orange.withOpacity(0.3)),
        ),
        child: Column(
          children: [
            Icon(Icons.warning, color: Colors.orange, size: 32),
            const SizedBox(height: 8),
            Text(
              'Invalid weather data format',
              style: TextStyle(color: Colors.orange),
            ),
            const SizedBox(height: 8),
            Text(
              'Received: ${weatherData.runtimeType}',
              style: TextStyle(color: Colors.orange, fontSize: 12),
            ),
          ],
        ),
      );
    }
    
    final current = weatherData as Map<String, dynamic>;
    
    return Column(
      children: [
        // Current Weather
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.blue.withOpacity(0.1), Colors.blue.withOpacity(0.2)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${current['temperature']?.toStringAsFixed(1) ?? 'N/A'}°C',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.blue,
                      ),
                    ),
                    Text(
                      current['weather_description'] ?? 'Unknown',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.blue,
                      ),
                    ),
                  ],
                ),
              ),
              Column(
                children: [
                  _buildWeatherMetric(
                    Icons.water_drop,
                    'Humidity',
                    '${current['humidity']?.toStringAsFixed(0) ?? 'N/A'}%',
                  ),
                  const SizedBox(height: 8),
                  _buildWeatherMetric(
                    Icons.air,
                    'Wind',
                    '${current['wind_speed']?.toStringAsFixed(1) ?? 'N/A'} km/h',
                  ),
                ],
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Weather Forecast
        if (forecastData != null && forecastData!.isNotEmpty) ...[
          Text(
            '7-Day Forecast',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 80,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: forecastData!.length,
              itemBuilder: (context, index) {
                final day = forecastData![index];
                return Container(
                  width: 80,
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.grey.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.grey.withOpacity(0.3)),
                  ),
                  child: Column(
                    children: [
                      Text(
                        _formatDate(day['date']),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${day['max_temp']?.toStringAsFixed(0) ?? 'N/A'}°',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${day['min_temp']?.toStringAsFixed(0) ?? 'N/A'}°',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
        
        const SizedBox(height: 16),
        
        // Crop Impact
        _buildCropImpactSection(current),
      ],
    );
  }

  Widget _buildWeatherMetric(IconData icon, String label, String value) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: Colors.blue),
        const SizedBox(width: 4),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.blue,
              ),
            ),
            Text(
              value,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCropImpactSection(Map<String, dynamic> weather) {
    final temp = weather['temperature'] ?? 0.0;
    final humidity = weather['humidity'] ?? 0.0;
    final rainfall = weather['rainfall'] ?? 0.0;
    
    List<String> impacts = [];
    
    if (temp < 15) {
      impacts.add('🌡️ Low temperature may delay planting');
    } else if (temp > 35) {
      impacts.add('🌡️ High temperature - ensure adequate irrigation');
    }
    
    if (humidity > 80) {
      impacts.add('💧 High humidity - monitor for fungal diseases');
    }
    
    if (rainfall > 20) {
      impacts.add('🌧️ Heavy rainfall - delay field operations');
    }
    
    if (impacts.isEmpty) {
      impacts.add('✅ Weather conditions are favorable for farming');
    }
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.agriculture, color: Colors.green, size: 20),
              const SizedBox(width: 8),
              Text(
                'Crop Impact',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...impacts.map((impact) => Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text(
              impact,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.green,
              ),
            ),
          )),
        ],
      ),
    );
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return 'N/A';
    try {
      final date = DateTime.parse(dateStr);
      return '${date.day}/${date.month}';
    } catch (e) {
      return 'N/A';
    }
  }
}
