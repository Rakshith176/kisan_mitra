import 'web_recorder.dart';

class _StubRecorder implements WebRecorder {
  @override
  Future<void> start() async {}

  @override
  Future<String?> stop() async => null;
}

WebRecorder createWebRecorderImpl() => _StubRecorder();
