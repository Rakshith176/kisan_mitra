import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/ai_recommendation_models.dart';
import '../providers/ai_recommendation_providers.dart';
import '../widgets/ai_recommendation_card.dart';
import '../widgets/ai_recommendation_summary_card.dart';

class AIRecommendationsDashboard extends ConsumerStatefulWidget {
  final String clientId;

  const AIRecommendationsDashboard({
    super.key,
    required this.clientId,
  });

  @override
  ConsumerState<AIRecommendationsDashboard> createState() => _AIRecommendationsDashboardState();
}

class _AIRecommendationsDashboardState extends ConsumerState<AIRecommendationsDashboard>
    with TickerProviderStateMixin {
  late TabController _tabController;
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    
    // Fetch initial recommendations
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetchRecommendations();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchRecommendations() async {
    await ref.read(clientAIRecommendationProvider(widget.clientId).notifier)
        .fetchCachedRecommendations(widget.clientId, maxRecommendations: 20);
  }

  Future<void> _refreshRecommendations() async {
    setState(() => _isRefreshing = true);
    
    await ref.read(clientAIRecommendationProvider(widget.clientId).notifier)
        .refreshRecommendations(widget.clientId);
    
    setState(() => _isRefreshing = false);
  }

  Future<void> _generateNewRecommendations() async {
    await ref.read(clientAIRecommendationProvider(widget.clientId).notifier)
        .generateRecommendations(widget.clientId);
  }

  @override
  Widget build(BuildContext context) {
    final recommendationsState = ref.watch(clientAIRecommendationProvider(widget.clientId));
    final urgentRecommendations = ref.watch(urgentRecommendationsProvider(widget.clientId));
    final criticalRecommendations = ref.watch(criticalRecommendationsProvider(widget.clientId));
    final weatherRecommendations = ref.watch(weatherRecommendationsProvider(widget.clientId));
    final marketRecommendations = ref.watch(marketRecommendationsProvider(widget.clientId));
    final soilRecommendations = ref.watch(soilRecommendationsProvider(widget.clientId));
    final cropProtectionRecommendations = ref.watch(cropProtectionRecommendationsProvider(widget.clientId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('🤖 AI Farming Assistant'),
        backgroundColor: Colors.green[700],
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isRefreshing ? null : _refreshRecommendations,
            tooltip: 'Refresh Recommendations',
          ),
          IconButton(
            icon: const Icon(Icons.smart_toy),
            onPressed: _generateNewRecommendations,
            tooltip: 'Generate New Recommendations',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(icon: Icon(Icons.dashboard), text: 'Overview'),
            Tab(icon: Icon(Icons.warning), text: 'Urgent'),
            Tab(icon: Icon(Icons.category), text: 'By Type'),
            Tab(icon: Icon(Icons.analytics), text: 'Analytics'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildOverviewTab(
            recommendationsState,
            urgentRecommendations,
            criticalRecommendations,
          ),
          _buildUrgentTab(urgentRecommendations, recommendationsState),
          _buildByTypeTab(
            weatherRecommendations,
            marketRecommendations,
            soilRecommendations,
            cropProtectionRecommendations,
          ),
          _buildAnalyticsTab(recommendationsState),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _generateNewRecommendations,
        icon: const Icon(Icons.auto_awesome),
        label: const Text('AI Analysis'),
        backgroundColor: Colors.green[600],
        foregroundColor: Colors.white,
      ),
    );
  }

  Widget _buildOverviewTab(
    AIRecommendationState state,
    List<AIRecommendation> urgent,
    List<AIRecommendation> critical,
  ) {
    return RefreshIndicator(
      onRefresh: _fetchRecommendations,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Summary Cards
            Row(
              children: [
                Expanded(
                  child: AIRecommendationSummaryCard(
                    title: 'Total',
                    count: state.recommendations.length,
                    icon: Icons.list,
                    color: Colors.blue,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: AIRecommendationSummaryCard(
                    title: 'Urgent',
                    count: urgent.length,
                    icon: Icons.warning,
                    color: Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: AIRecommendationSummaryCard(
                    title: 'Critical',
                    count: critical.length,
                    icon: Icons.error,
                    color: Colors.red,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: AIRecommendationSummaryCard(
                    title: 'Active',
                    count: state.recommendations.where((r) => !r.isExpired).length,
                    icon: Icons.check_circle,
                    color: Colors.green,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // Last Updated
            if (state.lastUpdated != DateTime.now())
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.info, color: Colors.blue[600]),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Last updated: ${state.lastUpdated != null ? _formatDateTime(state.lastUpdated!) : 'Never'}',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            
            const SizedBox(height: 24),
            
            // Critical Recommendations
            if (critical.isNotEmpty) ...[
              _buildSectionHeader('🚨 Critical Actions Required', Colors.red),
              const SizedBox(height: 16),
              ...critical.map((rec) => AIRecommendationCard(
                recommendation: rec,
                onActionTaken: () => _markActionTaken(rec),
              )),
              const SizedBox(height: 24),
            ],
            
            // Urgent Recommendations
            if (urgent.isNotEmpty) ...[
              _buildSectionHeader('⚠️ Urgent Actions (24h)', Colors.orange),
              const SizedBox(height: 16),
              ...urgent.take(3).map((rec) => AIRecommendationCard(
                recommendation: rec,
                onActionTaken: () => _markActionTaken(rec),
              )),
              if (urgent.length > 3)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Center(
                    child: TextButton(
                      onPressed: () => _tabController.animateTo(1),
                      child: Text('View all ${urgent.length} urgent recommendations'),
                    ),
                  ),
                ),
              const SizedBox(height: 24),
            ],
            
            // Recent Recommendations
            if (state.recommendations.isNotEmpty) ...[
              _buildSectionHeader('📋 Recent Recommendations', Colors.green),
              const SizedBox(height: 16),
              ...state.recommendations
                  .where((rec) => !rec.isCritical && !rec.isUrgent)
                  .take(5)
                  .map((rec) => AIRecommendationCard(
                    recommendation: rec,
                    onActionTaken: () => _markActionTaken(rec),
                  )),
            ],
            
            // Empty State
            if (state.recommendations.isEmpty && !state.isLoading) ...[
              const SizedBox(height: 48),
              Center(
                child: Column(
                  children: [
                    Icon(Icons.psychology, size: 64, color: Colors.grey[400]),
                    const SizedBox(height: 16),
                    Text(
                      'No AI recommendations yet',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Tap the AI Analysis button to generate personalized farming recommendations',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey[500]),
                    ),
                  ],
                ),
              ),
            ],
            
            // Loading State
            if (state.isLoading) ...[
              const SizedBox(height: 48),
              const Center(child: CircularProgressIndicator()),
            ],
            
            // Error State
            if (state.error != null) ...[
              const SizedBox(height: 16),
              Card(
                color: Colors.red[50],
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.error, color: Colors.red[600]),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Error: ${state.error}',
                          style: TextStyle(color: Colors.red[700]),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => ref.read(clientAIRecommendationProvider(widget.clientId).notifier).clearError(),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            
            const SizedBox(height: 100), // Bottom padding for FAB
          ],
        ),
      ),
    );
  }

  Widget _buildUrgentTab(
    List<AIRecommendation> urgent,
    AIRecommendationState state,
  ) {
    return RefreshIndicator(
      onRefresh: _fetchRecommendations,
      child: urgent.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.check_circle, size: 64, color: Colors.green[400]),
                  const SizedBox(height: 16),
                  Text(
                    'No urgent actions required!',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      color: Colors.green[600],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'All recommendations are under control',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: urgent.length,
              itemBuilder: (context, index) {
                final rec = urgent[index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: AIRecommendationCard(
                    recommendation: rec,
                    onActionTaken: () => _markActionTaken(rec),
                  ),
                );
              },
            ),
    );
  }

  Widget _buildByTypeTab(
    List<AIRecommendation> weather,
    List<AIRecommendation> market,
    List<AIRecommendation> soil,
    List<AIRecommendation> cropProtection,
  ) {
    return RefreshIndicator(
      onRefresh: _fetchRecommendations,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildTypeSection('🌤️ Weather Adaptation', weather, Colors.blue),
            const SizedBox(height: 24),
            _buildTypeSection('💰 Market Actions', market, Colors.green),
            const SizedBox(height: 24),
            _buildTypeSection('🌍 Soil Improvement', soil, Colors.brown),
            const SizedBox(height: 24),
            _buildTypeSection('🛡️ Crop Protection', cropProtection, Colors.orange),
            const SizedBox(height: 100), // Bottom padding for FAB
          ],
        ),
      ),
    );
  }

  Widget _buildTypeSection(
    String title,
    List<AIRecommendation> recommendations,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(title, color),
        const SizedBox(height: 16),
        if (recommendations.isEmpty)
          Padding(
            padding: const EdgeInsets.all(16),
            child: Center(
              child: Text(
                'No recommendations in this category',
                style: TextStyle(color: Colors.grey[500]),
              ),
            ),
          )
        else
          ...recommendations.map((rec) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: AIRecommendationCard(
              recommendation: rec,
              onActionTaken: () => _markActionTaken(rec),
            ),
          )),
      ],
    );
  }

  Widget _buildAnalyticsTab(AIRecommendationState state) {
    final summary = ref.read(clientAIRecommendationProvider(widget.clientId).notifier)
        .getRecommendationsSummary();
    
    return RefreshIndicator(
      onRefresh: _fetchRecommendations,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Performance Metrics
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '📊 Performance Overview',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    _buildMetricRow('Total Recommendations', summary['total']?.toString() ?? '0'),
                    _buildMetricRow('Active Recommendations', summary['active']?.toString() ?? '0'),
                    _buildMetricRow('Urgent Actions', summary['urgent']?.toString() ?? '0'),
                    _buildMetricRow('Critical Issues', summary['critical']?.toString() ?? '0'),
                    _buildMetricRow('Expired', summary['expired']?.toString() ?? '0'),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Priority Distribution
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '🎯 Priority Distribution',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    _buildPriorityChart(),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Type Distribution
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '📋 Recommendation Types',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    _buildTypeChart(),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 100), // Bottom padding for FAB
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, Color color) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: Text(
            title,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMetricRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 16)),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.green[700],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPriorityChart() {
    final counts = ref.watch(recommendationsCountByPriorityProvider(widget.clientId));
    
    return Column(
      children: [
        _buildChartBar('Critical', counts['critical'] ?? 0, Colors.red, 100),
        _buildChartBar('High', counts['high'] ?? 0, Colors.orange, 100),
        _buildChartBar('Medium', counts['medium'] ?? 0, Colors.yellow, 100),
        _buildChartBar('Low', counts['low'] ?? 0, Colors.green, 100),
      ],
    );
  }

  Widget _buildTypeChart() {
    final counts = ref.watch(recommendationsCountByTypeProvider(widget.clientId));
    
    return Column(
      children: [
        _buildChartBar('Weather', counts['weather_adaptation'] ?? 0, Colors.blue, 100),
        _buildChartBar('Market', counts['market_action'] ?? 0, Colors.green, 100),
        _buildChartBar('Soil', counts['soil_improvement'] ?? 0, Colors.brown, 100),
        _buildChartBar('Crop Protection', counts['crop_protection'] ?? 0, Colors.orange, 100),
        _buildChartBar('Irrigation', counts['irrigation'] ?? 0, Colors.cyan, 100),
        _buildChartBar('Fertilization', counts['fertilization'] ?? 0, Colors.purple, 100),
      ],
    );
  }

  Widget _buildChartBar(String label, int count, Color color, double maxWidth) {
    final width = count > 0 ? (count / 10) * maxWidth : 0.0;
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(label, style: const TextStyle(fontSize: 14)),
          ),
          Expanded(
            child: Container(
              height: 20,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(10),
              ),
              child: FractionallySizedBox(
                alignment: Alignment.centerLeft,
                widthFactor: width / maxWidth,
                child: Container(
                  decoration: BoxDecoration(
                    color: color,
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          SizedBox(
            width: 30,
            child: Text(
              count.toString(),
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inDays}d ago';
    }
  }

  void _markActionTaken(AIRecommendation recommendation) {
    // TODO: Implement action tracking
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Action marked as taken: ${recommendation.title}'),
        backgroundColor: Colors.green[600],
      ),
    );
  }
}
