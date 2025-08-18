import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppSettingsState {
  final Locale locale;
  final bool onboardingDone;
  const AppSettingsState({required this.locale, required this.onboardingDone});

  AppSettingsState copyWith({Locale? locale, bool? onboardingDone}) => AppSettingsState(
        locale: locale ?? this.locale,
        onboardingDone: onboardingDone ?? this.onboardingDone,
      );
}

class AppSettingsNotifier extends StateNotifier<AppSettingsState> {
  AppSettingsNotifier(AppSettingsState initialState) : super(initialState);

  Future<void> setLanguage(Locale locale) async {
    state = state.copyWith(locale: locale);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('languageCode', locale.languageCode);
  }

  Future<void> setOnboardingDone(bool done) async {
    state = state.copyWith(onboardingDone: done);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('onboardingDone', done);
  }
}

final appSettingsProvider = StateNotifierProvider<AppSettingsNotifier, AppSettingsState>((ref) {
  throw UnimplementedError('appSettingsProvider must be overridden with initial state');
});


