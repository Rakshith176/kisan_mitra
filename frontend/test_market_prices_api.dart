import 'dart:convert';
import 'dart:io';

void main() async {
  print('Testing Market Prices API...\n');
  
  final crops = ['wheat', 'rice', 'maize', 'cotton', 'sugarcane'];
  
  for (final crop in crops) {
    print('Testing crop: $crop');
    
    try {
      final response = await HttpClient().getUrl(
        Uri.parse('http://localhost:8080/market/prices?crop=$crop&location=Karnataka')
      );
      
      final httpResponse = await response.close();
      final responseBody = await httpResponse.transform(utf8.decoder).join();
      final data = jsonDecode(responseBody);
      
      print('✅ Status: ${httpResponse.statusCode}');
      print('📊 Total markets: ${data['total_markets']}');
      print('📍 Location: ${data['location']}');
      print('📅 Last updated: ${data['last_updated']}');
      print('🏷️ Source: ${data['source']}');
      
      if (data['prices'] is List && (data['prices'] as List).isNotEmpty) {
        print('💰 Sample prices:');
        for (final price in (data['prices'] as List).take(2)) {
          print('  - ${price['market_name']}: ₹${price['modal_price']}/${price['unit']}');
        }
      } else {
        print('❌ No prices available');
      }
      
    } catch (e) {
      print('❌ Error: $e');
    }
    
    print('');
  }
  
  print('✅ Market Prices API test completed!');
}
