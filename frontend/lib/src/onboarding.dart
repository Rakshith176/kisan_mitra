import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:geolocator/geolocator.dart';

import '../l10n/app_localizations.dart';
import 'state/settings_provider.dart';
import 'repositories/profile_repository.dart';
import 'onboarding/signup_page.dart';

class OnboardingScreen extends ConsumerWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = AppLocalizations.of(context)!;
    final settings = ref.watch(appSettingsProvider);
    return Scaffold(
      appBar: AppBar(title: Text(t.welcome)),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(t.languageSelectTitle, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),
            Wrap(spacing: 12, children: [
              _LangButton(code: 'en', label: 'English', onSelect: () => ref.read(appSettingsProvider.notifier).setLanguage(const Locale('en'))),
              _LangButton(code: 'kn', label: 'ಕನ್ನಡ', onSelect: () => ref.read(appSettingsProvider.notifier).setLanguage(const Locale('kn'))),
              _LangButton(code: 'hi', label: 'हिंदी', onSelect: () => ref.read(appSettingsProvider.notifier).setLanguage(const Locale('hi'))),
            ]),
            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () async {
                  // After language selection, proceed to Signup page (localized by current locale)
                  if (context.mounted) {
                    await Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SignupPage()));
                  }
                },
                child: Text(t.ctaContinue),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LangButton extends StatelessWidget {
  final String code;
  final String label;
  final VoidCallback onSelect;
  const _LangButton({required this.code, required this.label, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(onPressed: onSelect, child: Text(label));
  }
}

Future<String?> _showTextDialog(BuildContext context, {required String title, required String hint}) async {
  final controller = TextEditingController();
  return showDialog<String>(
    context: context,
    builder: (context) => AlertDialog(
      title: Text(title),
      content: TextField(controller: controller, keyboardType: TextInputType.number, decoration: InputDecoration(hintText: hint)),
      actions: [
        TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Cancel')),
        ElevatedButton(onPressed: () => Navigator.of(context).pop(controller.text.trim()), child: const Text('OK')),
      ],
    ),
  );
}

Future<String?> _askPincode(BuildContext context) async {
  while (true) {
    final v = await _showTextDialog(context, title: 'Enter pincode', hint: '6-digit pincode');
    if (v == null) return null;
    final valid = RegExp(r'^\d{6}\$').hasMatch(v);
    if (valid) return v;
    if (!context.mounted) return null;
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 6-digit pincode')));
  }
}


