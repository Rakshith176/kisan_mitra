import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import 'package:http/http.dart' as http;

import 'l10n/app_localizations.dart';
import 'src/app_shell.dart';
import 'src/onboarding.dart';
import 'src/state/settings_provider.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  // Ensure clientId exists
  var clientId = prefs.getString('clientId');
  clientId ??= const Uuid().v4();
  await prefs.setString('clientId', clientId);
  
  // Create user in backend if it doesn't exist
  try {
    final response = await http.post(
      Uri.parse('http://localhost:8080/users?client_id=$clientId&language=en'),
    );
    if (response.statusCode == 200) {
      print('User created/verified in backend: $clientId');
    }
  } catch (e) {
    print('Warning: Could not create user in backend: $e');
  }
  
  final langCode = prefs.getString('languageCode') ?? 'en';
  final onboardingDone = prefs.getBool('onboardingDone') ?? false;

  runApp(ProviderScope(
    overrides: [
      appSettingsProvider.overrideWith((ref) => AppSettingsNotifier(
            AppSettingsState(locale: Locale(langCode), onboardingDone: onboardingDone),
          )),
    ],
    child: const FarmerApp(),
  ));
}

class FarmerApp extends ConsumerWidget {
  const FarmerApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(appSettingsProvider);
    return MaterialApp(
      title: 'Farmer Assistant',
      debugShowCheckedModeBanner: false,
      locale: settings.locale,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('kn'),
        Locale('hi'),
      ],
      home: Builder(builder: (context) {
        // Show onboarding once to pick language
        return Consumer(builder: (context, ref, _) {
          final settings = ref.watch(appSettingsProvider);
          return settings.onboardingDone ? const AppShell() : const OnboardingScreen();
        });
      }),
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
        useMaterial3: true,
        textTheme: const TextTheme(
          bodyLarge: TextStyle(fontSize: 18),
          bodyMedium: TextStyle(fontSize: 16),
          labelLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}


