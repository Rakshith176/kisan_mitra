import 'package:intl/intl.dart';

final _inr = NumberFormat.currency(symbol: '₹', decimalDigits: 0, locale: 'en_IN');
final _km = NumberFormat('0');
final _temp = NumberFormat('0');
final _mm = NumberFormat('0');
final _dateShort = DateFormat('dd MMM');
final _dateTimeShort = DateFormat('dd MMM HH:mm');

String formatInr(num v) => _inr.format(v);
String formatKm(num? v) => v == null ? '-' : '${_km.format(v)} km';
String formatTemp(num v) => '${_temp.format(v)}°';
String formatMm(num? v) => v == null ? '0mm' : '${_mm.format(v)}mm';
String formatDateShort(DateTime d) => _dateShort.format(d);
String formatDateRange(DateTime? a, DateTime? b) {
  if (a == null || b == null) return '-';
  return '${_dateShort.format(a)} → ${_dateShort.format(b)}';
}
String formatDateTimeShort(DateTime? d) => d == null ? '-' : _dateTimeShort.format(d);


