import 'package:flutter/foundation.dart' show kIsWeb;

import 'web_recorder_stub.dart' if (dart.library.html) 'web_recorder_web.dart';

abstract class WebRecorder {
  Future<void> start();
  Future<String?> stop();
}

WebRecorder createWebRecorder() => createWebRecorderImpl();
