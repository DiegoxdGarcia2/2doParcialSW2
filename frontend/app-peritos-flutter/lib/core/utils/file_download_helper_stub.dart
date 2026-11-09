import 'dart:io' show Platform, Process;

void downloadOrOpenPlatform(String url, String filename) {
  try {
    if (Platform.isWindows) {
      Process.run('cmd', ['/c', 'start', '', url]);
    }
  } catch (_) {
    // Modo no interactivo o headless
  }
}

