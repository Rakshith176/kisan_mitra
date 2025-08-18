import 'package:flutter/material.dart';
import '../widgets/market_prices_widget.dart';

class MarketPricesTestScreen extends StatelessWidget {
  const MarketPricesTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Market Prices Test'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: const SingleChildScrollView(
        child: Column(
          children: [
            SizedBox(height: 16),
            MarketPricesWidget(
              clientId: 'test_user',
              location: 'Karnataka',
            ),
            SizedBox(height: 16),
            Padding(
              padding: EdgeInsets.all(16),
              child: Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Market Prices API Test',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'This widget demonstrates the market prices functionality:',
                        style: TextStyle(fontSize: 14),
                      ),
                      SizedBox(height: 8),
                      Text('• Select different crops using the chips'),
                      Text('• View market prices for each crop'),
                      Text('• Refresh data using the refresh button'),
                      Text('• Data is cached for 6 hours'),
                      Text('• Fallback to sample data when real data unavailable'),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
