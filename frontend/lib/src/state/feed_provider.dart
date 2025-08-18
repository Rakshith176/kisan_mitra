import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../repositories/feed_repository.dart';
import '../api/dto/feed.dart';

final feedRepositoryProvider = Provider<FeedRepository>((ref) => FeedRepository());

class FeedState {
  final AsyncValue<FeedResponse?> feed;
  final bool isStale;
  const FeedState({required this.feed, required this.isStale});
}

class FeedNotifier extends StateNotifier<FeedState> {
  final FeedRepository _repo;
  final String _clientId;
  FeedNotifier(this._repo, this._clientId) : super(const FeedState(feed: AsyncData(null), isStale: false));
  bool _didInitialFetch = false;

  // Load from local cache only; no network call
  Future<void> hydrateFromCache() async {
    final (cached, ts) = await _repo.readCachedFeed(_clientId);
    if (cached != null) {
      final stale = ts == null ? true : DateTime.now().difference(ts) > const Duration(hours: 24);
      state = FeedState(feed: AsyncData(cached), isStale: stale);
    } else {
      state = const FeedState(feed: AsyncData(null), isStale: true);
    }
  }

  // Explicit user-initiated refresh → single backend call
  Future<void> refresh() async {
    state = FeedState(feed: const AsyncLoading(), isStale: state.isStale);
    try {
      final fresh = await _repo.fetchFeed(_clientId);
      state = FeedState(feed: AsyncData(fresh), isStale: false);
    } catch (e, st) {
      state = FeedState(feed: AsyncError(e, st), isStale: state.isStale);
    }
  }

  // Call once per app session (e.g., after login/first open)
  Future<void> triggerInitialRefresh() async {
    if (_didInitialFetch) return;
    _didInitialFetch = true;
    await refresh();
  }
}

// Global provider (family) to avoid recreating providers during rebuilds
final feedNotifierProvider = StateNotifierProvider.family<FeedNotifier, FeedState, String>(
  (ref, clientId) => FeedNotifier(ref.read(feedRepositoryProvider), clientId),
);


