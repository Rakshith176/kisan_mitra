import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:geolocator/geolocator.dart';

import '../../l10n/app_localizations.dart';
import '../repositories/profile_repository.dart';
import '../repositories/catalog_repository.dart';
import '../api/dto/catalog.dart';
import '../state/settings_provider.dart';

class SignupPage extends ConsumerStatefulWidget {
  const SignupPage({super.key});
  @override
  ConsumerState<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends ConsumerState<SignupPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _pincodeCtrl = TextEditingController();
  final _farmSizeCtrl = TextEditingController();
  bool _locChecked = false;
  bool _fetchingLoc = false;
  double? _lat;
  double? _lon;
  List<String> _cropIds = [];
  List<CropItemDto> _cropOptions = [];
  bool _loadingCrops = true;

  @override
  void initState() {
    super.initState();
    _loadCrops();
    // Try to get GPS automatically; user can still enter pincode if denied/unavailable
    _getLocation();
  }

  Future<void> _loadCrops() async {
    try {
      final crops = await CatalogRepository().fetchCrops();
      setState(() {
        _cropOptions = crops;
      });
    } catch (_) {} finally {
      setState(() => _loadingCrops = false);
    }
  }

  Future<void> _getLocation() async {
    setState(() => _fetchingLoc = true);
    try {
      var perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) perm = await Geolocator.requestPermission();
      if (perm == LocationPermission.always || perm == LocationPermission.whileInUse) {
        final pos = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.low);
        setState(() {
          _lat = pos.latitude; _lon = pos.longitude; _locChecked = true;
        });
      } else {
        setState(() => _locChecked = true);
      }
    } catch (_) {
      setState(() => _locChecked = true);
    } finally {
      setState(() => _fetchingLoc = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(title: Text(t.welcome)),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(t.languageSelectTitle, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(t.ctaContinue, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 16),
            TextFormField(
              controller: _nameCtrl,
              decoration: const InputDecoration(labelText: 'Your name (optional)'),
            ),
            const SizedBox(height: 16),
            Row(children: [
              Expanded(child: Text(_lat != null ? 'Location: $_lat, $_lon' : 'No GPS location yet')),
              if (_fetchingLoc) const SizedBox(width: 16),
              if (_fetchingLoc) const CircularProgressIndicator(strokeWidth: 2),
              if (!_fetchingLoc)
                ElevatedButton.icon(onPressed: _getLocation, icon: const Icon(Icons.my_location), label: const Text('Use GPS')),
            ]),
            const SizedBox(height: 12),
            if (_lat == null || _lon == null)
              TextFormField(
                controller: _pincodeCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Pincode (if GPS not available)'),
                validator: (v) {
                  if (_lat == null || _lon == null) {
                    final re = RegExp(r'^\d{6}$');
                    if (v == null || !re.hasMatch(v)) {
                      return 'Enter a valid 6-digit pincode';
                    }
                  }
                  return null;
                },
              ),
            const SizedBox(height: 16),
            Text('Select your crops'),
            const SizedBox(height: 8),
            if (_loadingCrops) const LinearProgressIndicator(),
            if (!_loadingCrops)
              Wrap(spacing: 8, runSpacing: 8, children: [
                for (final c in _cropOptions)
                  FilterChip(
                    label: Text(_cropLabel(c, Localizations.localeOf(context).languageCode)),
                    selected: _cropIds.contains(c.id),
                    onSelected: (sel) {
                      setState(() {
                        if (sel) {
                          _cropIds.add(c.id);
                        } else {
                          _cropIds.remove(c.id);
                        }
                      });
                    },
                  ),
              ]),
            if (_cropIds.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text('${_cropIds.length} selected', style: Theme.of(context).textTheme.bodySmall),
              ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _farmSizeCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Farm size (acres, optional)'),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () async {
                if (!_formKey.currentState!.validate()) return;
                if (_cropIds.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please select at least one crop')));
                  return;
                }
                final prefs = await SharedPreferences.getInstance();
                final clientId = prefs.getString('clientId')!;
                final lang = Localizations.localeOf(context).languageCode;
                final repo = ProfileRepository();
                await repo.upsertProfile(
                  clientId: clientId,
                  language: lang,
                  lat: _lat,
                  lon: _lon,
                  pincode: (_lat == null || _lon == null) ? _pincodeCtrl.text.trim() : null,
                  cropIds: _cropIds.isEmpty ? null : _cropIds,
                  farmSizeAcres: double.tryParse(_farmSizeCtrl.text.trim()),
                );
                // Mark onboarding complete so app switches to AppShell
                await ref.read(appSettingsProvider.notifier).setOnboardingDone(true);
                if (context.mounted) Navigator.of(context).pop();
              },
              child: const Text('Create profile'),
            ),
            const SizedBox(height: 12),
            const Text('We respect your privacy. Location helps tailor weather and mandi prices.'),
          ],
        ),
      ),
    );
  }
}

String _cropLabel(CropItemDto c, String lang) {
  switch (lang) {
    case 'hi':
      return c.name_hi ?? c.name_en;
    case 'kn':
      return c.name_kn ?? c.name_en;
    default:
      return c.name_en;
  }
}

// duplicate helper removed


