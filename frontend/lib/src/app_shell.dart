import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import 'feed/feed_screen.dart';
import 'state/client_provider.dart';
import '../screens/chat_screen.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'state/settings_provider.dart';
import 'repositories/profile_repository.dart';
import 'package:shared_preferences/shared_preferences.dart';
import './crop_cycle/screens/planner_main_screen.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final t = AppLocalizations.of(context)!;
    final tabs = [
      _FeedTab(title: t.tabFeed),
      _ChatTab(title: t.tabChat),
      _PlannerTab(title: t.tabPlanner),
      _SettingsTab(title: t.tabSettings),
    ];

    return Scaffold(
      appBar: AppBar(title: Text(t.appTitle)),
      body: tabs[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        destinations: [
          NavigationDestination(icon: const Icon(Icons.view_agenda), label: t.tabFeed),
          NavigationDestination(icon: const Icon(Icons.chat_bubble), label: t.tabChat),
          NavigationDestination(icon: const Icon(Icons.event), label: t.tabPlanner),
          NavigationDestination(icon: const Icon(Icons.settings), label: t.tabSettings),
        ],
        onDestinationSelected: (i) => setState(() => _index = i),
      ),
    );
  }
}

class _FeedTab extends StatelessWidget {
  final String title;
  const _FeedTab({required this.title});

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {
      final clientIdAsync = ref.watch(clientIdProvider);
      return clientIdAsync.when(
        data: (id) => FeedScreen(clientId: id, language: Localizations.localeOf(context).languageCode),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Client not initialized')),
      );
    });
  }
}

class _ChatTab extends StatelessWidget {
  final String title;
  const _ChatTab({required this.title});

  @override
  Widget build(BuildContext context) {
    final lang = Localizations.localeOf(context).languageCode;
    return Column(
      children: [
        // Live Chat Button
        Container(
          width: double.infinity,
          margin: EdgeInsets.all(16),
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ChatScreen(),
                ),
              );
            },
            icon: Icon(Icons.record_voice_over, color: Colors.white),
            label: Text(
              '🎙️ Live Voice Chat',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              padding: EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
        
        // Existing Chat Screen
        Expanded(
          child: const ChatScreen(),
        ),
      ],
    );
  }
}

class _PlannerTab extends StatelessWidget {
  final String title;
  const _PlannerTab({required this.title});

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {
      final clientIdAsync = ref.watch(clientIdProvider);
      return clientIdAsync.when(
        data: (id) => PlannerMainScreen(clientId: id),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Client not initialized')),
      );
    });
  }
}

class _SettingsTab extends StatelessWidget {
  final String title;
  const _SettingsTab({required this.title});

  @override
  Widget build(BuildContext context) {
    final t = AppLocalizations.of(context)!;
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(t.languageSelectTitle, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          Wrap(spacing: 12, children: const [
            _LangChip(code: 'en', label: 'English'),
            _LangChip(code: 'kn', label: 'ಕನ್ನಡ'),
            _LangChip(code: 'hi', label: 'हिंदी'),
          ]),
        ],
      ),
    );
  }
}

class _LangChip extends StatelessWidget {
  final String code;
  final String label;
  const _LangChip({required this.code, required this.label});

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {
      return ActionChip(
        label: Text(label),
        onPressed: () async {
          // Update app locale and sync to backend profile
          await ref.read(appSettingsProvider.notifier).setLanguage(Locale(code));
          final prefs = await SharedPreferences.getInstance();
          final clientId = prefs.getString('clientId');
          if (clientId != null) {
            try {
              await ProfileRepository().upsertProfile(clientId: clientId, language: code);
              // Optionally refresh feed here if user is on the feed tab
            } catch (_) {}
          }
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Language set to $label')),
          );
        },
      );
    });
  }
}


