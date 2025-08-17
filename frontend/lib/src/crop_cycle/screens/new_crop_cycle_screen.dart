import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/crop_cycle_models.dart';

import '../providers/crop_cycle_providers.dart';

class NewCropCycleScreen extends ConsumerStatefulWidget {
  final String clientId;

  const NewCropCycleScreen({
    super.key,
    required this.clientId,
  });

  @override
  ConsumerState<NewCropCycleScreen> createState() => _NewCropCycleScreenState();
}

class _NewCropCycleScreenState extends ConsumerState<NewCropCycleScreen> {
  final _formKey = GlobalKey<FormState>();
  final _scrollController = ScrollController();
  
  // Form fields
  String? _selectedCropId;
  String _variety = '';
  DateTime _startDate = DateTime.now();
  String _selectedSeason = 'kharif';
  String _pincode = '';
  double _lat = 0.0;
  double _lon = 0.0;
  String _selectedIrrigationType = 'rainfed';
  double _areaAcres = 1.0;
  String _selectedLanguage = 'en';
  
  // State
  bool _isLoading = false;
  List<Crop> _availableCrops = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAvailableCrops();
    _getCurrentLocation();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadAvailableCrops() async {
    try {
      setState(() => _isLoading = true);
      final apiService = ref.read(cropCycleApiServiceProvider);
      final crops = await apiService.getAvailableCrops();
      setState(() {
        _availableCrops = crops;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _getCurrentLocation() async {
    // TODO: Implement actual location detection
    // For now, use default values
    setState(() {
      _lat = 12.9716; // Default to Bangalore
      _lon = 77.5946;
      _pincode = '560001';
    });
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null && picked != _startDate) {
      setState(() {
        _startDate = picked;
      });
    }
  }

  Future<void> _createCropCycle() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedCropId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a crop')),
      );
      return;
    }

    try {
      setState(() => _isLoading = true);
      
      final apiService = ref.read(cropCycleApiServiceProvider);
      final cycleData = {
        'clientId': widget.clientId,
        'cropId': _selectedCropId,
        'variety': _variety,
        'startDate': _startDate.toIso8601String(),
        'season': _selectedSeason,
        'pincode': _pincode,
        'lat': _lat,
        'lon': _lon,
        'irrigationType': _selectedIrrigationType,
        'areaAcres': _areaAcres,
        'language': _selectedLanguage,
        'status': 'planned',
        'plannedHarvestDate': _startDate.add(const Duration(days: 120)).toIso8601String(),
      };

      final newCycle = await apiService.createCropCycle(cycleData);
      
      // Refresh the crop cycles list
      ref.read(cropCyclesProvider(widget.clientId).notifier).refreshCropCycles(widget.clientId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Crop cycle created successfully!')),
        );
        Navigator.of(context).pop(newCycle);
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to create crop cycle: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('New Crop Cycle'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: Form(
        key: _formKey,
        child: Column(
          children: [
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _error != null
                      ? _buildErrorState()
                      : _buildForm(),
            ),
            _buildBottomActions(),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.red.shade300),
          const SizedBox(height: 16),
          Text(
            'Failed to load crops',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            _error!,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey.shade600,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadAvailableCrops,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildForm() {
    return ListView(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      children: [
        // Crop Selection
        _buildSectionHeader('🌱 Crop Selection'),
        _buildCropDropdown(),
        
        const SizedBox(height: 24),
        
        // Basic Details
        _buildSectionHeader('📋 Basic Details'),
        _buildVarietyField(),
        _buildDateField(),
        _buildSeasonField(),
        
        const SizedBox(height: 24),
        
        // Location & Area
        _buildSectionHeader('📍 Location & Area'),
        _buildPincodeField(),
        _buildAreaField(),
        _buildIrrigationField(),
        
        const SizedBox(height: 24),
        
        // Language Preference
        _buildSectionHeader('🌐 Language Preference'),
        _buildLanguageField(),
        
        const SizedBox(height: 100), // Bottom padding
      ],
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleLarge?.copyWith(
          fontWeight: FontWeight.bold,
          color: Colors.green.shade700,
        ),
      ),
    );
  }

  Widget _buildCropDropdown() {
    return DropdownButtonFormField<String>(
      value: _selectedCropId,
      decoration: const InputDecoration(
        labelText: 'Select Crop *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.grass),
      ),
      items: _availableCrops.map((crop) {
        return DropdownMenuItem(
          value: crop.id,
          child: Text('${crop.nameEn} (${crop.category})'),
        );
      }).toList(),
      onChanged: (value) {
        setState(() {
          _selectedCropId = value;
        });
      },
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please select a crop';
        }
        return null;
      },
    );
  }

  Widget _buildVarietyField() {
    return TextFormField(
      initialValue: _variety,
      decoration: const InputDecoration(
        labelText: 'Variety',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.category),
        hintText: 'e.g., Basmati, Hybrid, Local',
      ),
      onChanged: (value) => _variety = value,
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter crop variety';
        }
        return null;
      },
    );
  }

  Widget _buildDateField() {
    return InkWell(
      onTap: () => _selectDate(context),
      child: InputDecorator(
        decoration: const InputDecoration(
          labelText: 'Start Date *',
          border: OutlineInputBorder(),
          prefixIcon: Icon(Icons.calendar_today),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${_startDate.day}/${_startDate.month}/${_startDate.year}',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const Icon(Icons.arrow_drop_down),
          ],
        ),
      ),
    );
  }

  Widget _buildSeasonField() {
    return DropdownButtonFormField<String>(
      value: _selectedSeason,
      decoration: const InputDecoration(
        labelText: 'Season *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.wb_sunny),
      ),
      items: const [
        DropdownMenuItem(value: 'kharif', child: Text('Kharif (Monsoon)')),
        DropdownMenuItem(value: 'rabi', child: Text('Rabi (Winter)')),
        DropdownMenuItem(value: 'zaid', child: Text('Zaid (Summer)')),
        DropdownMenuItem(value: 'yearRound', child: Text('Year Round')),
      ],
      onChanged: (value) {
        setState(() {
          _selectedSeason = value!;
        });
      },
    );
  }

  Widget _buildPincodeField() {
    return TextFormField(
      initialValue: _pincode,
      decoration: const InputDecoration(
        labelText: 'Pincode *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.location_on),
        hintText: 'e.g., 560001',
      ),
      keyboardType: TextInputType.number,
      onChanged: (value) => _pincode = value,
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter pincode';
        }
        if (value.length != 6) {
          return 'Pincode must be 6 digits';
        }
        return null;
      },
    );
  }

  Widget _buildAreaField() {
    return TextFormField(
      initialValue: _areaAcres.toString(),
      decoration: const InputDecoration(
        labelText: 'Area (Acres) *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.area_chart),
        hintText: 'e.g., 2.5',
      ),
      keyboardType: TextInputType.number,
      onChanged: (value) {
        final area = double.tryParse(value);
        if (area != null && area > 0) {
          _areaAcres = area;
        }
      },
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter area';
        }
        final area = double.tryParse(value);
        if (area == null || area <= 0) {
          return 'Please enter a valid area';
        }
        return null;
      },
    );
  }

  Widget _buildIrrigationField() {
    return DropdownButtonFormField<String>(
      value: _selectedIrrigationType,
      decoration: const InputDecoration(
        labelText: 'Irrigation Type *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.water_drop),
      ),
      items: const [
        DropdownMenuItem(value: 'rainfed', child: Text('Rainfed')),
        DropdownMenuItem(value: 'irrigated', child: Text('Irrigated')),
        DropdownMenuItem(value: 'drip', child: Text('Drip Irrigation')),
        DropdownMenuItem(value: 'sprinkler', child: Text('Sprinkler')),
      ],
      onChanged: (value) {
        setState(() {
          _selectedIrrigationType = value!;
        });
      },
    );
  }

  Widget _buildLanguageField() {
    return DropdownButtonFormField<String>(
      value: _selectedLanguage,
      decoration: const InputDecoration(
        labelText: 'Preferred Language *',
        border: OutlineInputBorder(),
        prefixIcon: Icon(Icons.language),
      ),
      items: const [
        DropdownMenuItem(value: 'en', child: Text('English')),
        DropdownMenuItem(value: 'hi', child: Text('Hindi')),
        DropdownMenuItem(value: 'kn', child: Text('Kannada')),
      ],
      onChanged: (value) {
        setState(() {
          _selectedLanguage = value!;
        });
      },
    );
  }

  Widget _buildBottomActions() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade300,
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: () => Navigator.of(context).pop(),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('Cancel'),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: ElevatedButton(
              onPressed: _isLoading ? null : _createCropCycle,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Text('Create Crop Cycle'),
            ),
          ),
        ],
      ),
    );
  }
}
