import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/market_prices_service.dart';

final marketPricesServiceProvider = Provider<MarketPricesService>((ref) => MarketPricesService());

class MarketPricesState {
  final AsyncValue<MarketPricesResponse?> data;
  final String selectedCrop;
  final bool isStale;
  
  const MarketPricesState({
    required this.data,
    required this.selectedCrop,
    required this.isStale,
  });
  
  MarketPricesState copyWith({
    AsyncValue<MarketPricesResponse?>? data,
    String? selectedCrop,
    bool? isStale,
  }) {
    return MarketPricesState(
      data: data ?? this.data,
      selectedCrop: selectedCrop ?? this.selectedCrop,
      isStale: isStale ?? this.isStale,
    );
  }
}

class MarketPricesNotifier extends StateNotifier<MarketPricesState> {
  final MarketPricesService _service;
  
  MarketPricesNotifier(this._service) 
      : super(const MarketPricesState(
          data: AsyncData(null),
          selectedCrop: 'wheat',
          isStale: false,
        ));

  /// Load cached data for the selected crop
  Future<void> loadCachedData(String crop) async {
    final cached = await _service.getCachedMarketPrices(crop);
    if (cached != null) {
      state = state.copyWith(
        data: AsyncData(cached),
        selectedCrop: crop,
        isStale: false,
      );
    } else {
      state = state.copyWith(
        data: const AsyncData(null),
        selectedCrop: crop,
        isStale: true,
      );
    }
  }

  /// Fetch fresh market data for a crop
  Future<void> fetchMarketPrices({
    required String crop,
    String? location,
    String? clientId,
  }) async {
    state = state.copyWith(
      data: const AsyncLoading(),
      selectedCrop: crop,
    );
    
    try {
      final response = await _service.getMarketPricesWithCache(
        crop: crop,
        location: location,
        clientId: clientId,
      );
      
      state = state.copyWith(
        data: AsyncData(response),
        isStale: false,
      );
    } catch (e, stackTrace) {
      state = state.copyWith(
        data: AsyncError(e, stackTrace),
      );
    }
  }

  /// Refresh market data for the currently selected crop
  Future<void> refresh() async {
    if (state.selectedCrop.isNotEmpty) {
      await fetchMarketPrices(crop: state.selectedCrop);
    }
  }

  /// Change the selected crop and fetch its data
  Future<void> selectCrop(String crop) async {
    if (crop != state.selectedCrop) {
      await fetchMarketPrices(crop: crop);
    }
  }
}

// Global provider for market prices state
final marketPricesProvider = StateNotifierProvider<MarketPricesNotifier, MarketPricesState>(
  (ref) => MarketPricesNotifier(ref.read(marketPricesServiceProvider)),
);
