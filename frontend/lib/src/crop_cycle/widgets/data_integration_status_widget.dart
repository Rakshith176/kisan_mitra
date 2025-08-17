import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/crop_cycle_api_service.dart';

class DataIntegrationStatusWidget extends ConsumerStatefulWidget {
  final String clientId;

  const DataIntegrationStatusWidget({
    super.key,
    required this.clientId,
  });

  @override
  ConsumerState<DataIntegrationStatusWidget> createState() => _DataIntegrationStatusWidgetState();
}

class _DataIntegrationStatusWidgetState extends ConsumerState<DataIntegrationStatusWidget> {
  Map<String, dynamic>? dataStatus;
  bool isLoading = false;
  String? error;

  @override
  void initState() {
    super.initState();
    _fetchDataStatus();
  }

  Future<void> _fetchDataStatus() async {
    setState(() {
      isLoading = true;
      error = null;
    });

    try {
      final apiService = CropCycleApiService();
      final status = await apiService.getRealTimeDataStatus(widget.clientId);
      
      // Debug logging
      print('Status widget - Status data: $status');
      print('Status widget - Status data type: ${status.runtimeType}');
      
      setState(() {
        dataStatus = status;
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
                const Icon(Icons.data_usage, color: Colors.purple, size: 24),
                const SizedBox(width: 8),
                Text(
                  'Data Integration Status',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: _fetchDataStatus,
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
            else if (dataStatus != null)
              _buildStatusContent()
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
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade400, size: 32),
          const SizedBox(height: 8),
          Text(
            'Status data unavailable',
            style: TextStyle(color: Colors.red.shade700),
          ),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _fetchDataStatus,
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
        child: Text('No status data available'),
      ),
    );
  }

  Widget _buildStatusContent() {
    try {
      final status = dataStatus!;
      final overallStatus = status['overall_status'] ?? 'unknown';
      final dataSources = status['data_sources'] ?? {};
      final lastUpdated = status['last_updated'] ?? 'Unknown';
    
    return Column(
      children: [
        // Overall Status
        _buildOverallStatus(overallStatus),
        const SizedBox(height: 16),
        
        // Data Sources Status
        Text(
          'Data Sources',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        
        // Individual Data Source Status
        ...dataSources.entries.map((entry) {
          // Add type checking to prevent TypeError
          if (entry.value is! Map<String, dynamic>) {
            print('Warning: Data source ${entry.key} is not a Map. Type: ${entry.value.runtimeType}, Value: ${entry.value}');
            return _buildDataSourceStatus(entry.key, {
              'status': 'unknown',
              'last_fetch': 'Never',
              'data_age_hours': 0.0,
              'reliability_score': 0.0,
              'error_count': 0
            });
          }
          return _buildDataSourceStatus(entry.key, entry.value);
        }),
        
        const SizedBox(height: 16),
        
        // Last Updated
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Row(
            children: [
              Icon(Icons.access_time, size: 16, color: Colors.grey.shade600),
              const SizedBox(width: 8),
              Text(
                'Last Updated: $lastUpdated',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
    } catch (e) {
      print('Error building status content: $e');
      return _buildErrorState();
    }
  }

  Widget _buildOverallStatus(String status) {
    Color statusColor;
    IconData statusIcon;
    String statusText;
    
    switch (status.toLowerCase()) {
      case 'healthy':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        statusText = 'All Systems Operational';
        break;
      case 'degraded':
        statusColor = Colors.orange;
        statusIcon = Icons.warning;
        statusText = 'Some Issues Detected';
        break;
      case 'critical':
        statusColor = Colors.red;
        statusIcon = Icons.error;
        statusText = 'Critical Issues';
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.help;
        statusText = 'Status Unknown';
    }
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(statusIcon, color: statusColor, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  statusText,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: statusColor,
                  ),
                ),
                Text(
                  'Overall system status: ${status.toUpperCase()}',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: statusColor,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDataSourceStatus(String sourceName, Map<String, dynamic> sourceData) {
    final status = sourceData['status'] ?? 'unknown';
    final lastFetch = sourceData['last_fetch'] ?? 'Never';
    final dataAge = sourceData['data_age_hours'] ?? 0.0;
    final reliability = sourceData['reliability_score'] ?? 0.0;
    final errorCount = sourceData['error_count'] ?? 0;
    
    Color statusColor;
    IconData statusIcon;
    
    switch (status.toLowerCase()) {
      case 'active':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        break;
      case 'inactive':
        statusColor = Colors.grey;
        statusIcon = Icons.circle_outlined;
        break;
      case 'error':
        statusColor = Colors.red;
        statusIcon = Icons.error;
        break;
      case 'degraded':
        statusColor = Colors.orange;
        statusIcon = Icons.warning;
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.help;
    }
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: statusColor.withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade200,
            blurRadius: 2,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(statusIcon, color: statusColor, size: 20),
              const SizedBox(width: 8),
              Text(
                _formatSourceName(sourceName),
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  status.toUpperCase(),
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          
          // Data Details
          Row(
            children: [
              Expanded(
                child: _buildDataMetric(
                  'Last Fetch',
                  lastFetch,
                  Icons.access_time,
                ),
              ),
              Expanded(
                child: _buildDataMetric(
                  'Data Age',
                  '${dataAge.toStringAsFixed(1)}h',
                  Icons.hourglass_empty,
                ),
              ),
              Expanded(
                child: _buildDataMetric(
                  'Reliability',
                  '${(reliability * 100).toStringAsFixed(0)}%',
                  Icons.verified,
                ),
              ),
            ],
          ),
          
          // Error Information
          if (errorCount > 0) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Row(
                children: [
                  Icon(Icons.error_outline, size: 16, color: Colors.red.shade600),
                  const SizedBox(width: 8),
                  Text(
                    '$errorCount errors in last 24 hours',
                    style: TextStyle(
                      color: Colors.red.shade700,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildDataMetric(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 16, color: Colors.grey.shade600),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.grey.shade600,
            fontSize: 10,
          ),
        ),
      ],
    );
  }

  String _formatSourceName(String sourceName) {
    switch (sourceName.toLowerCase()) {
      case 'weather':
        return '🌤️ Weather Data';
      case 'market':
        return '💰 Market Data';
      case 'soil':
        return '🌱 Soil Health';
      case 'crop_calendar':
        return '📅 Crop Calendar';
      case 'government_schemes':
        return '🏛️ Government Schemes';
      default:
        return sourceName.replaceAll('_', ' ').toUpperCase();
    }
  }
}
