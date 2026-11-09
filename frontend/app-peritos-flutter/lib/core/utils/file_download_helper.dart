import 'file_download_helper_stub.dart'
    if (dart.library.html) 'file_download_helper_web.dart';

class FileDownloadHelper {
  /// Descarga o abre el archivo de manera transparente sin bloquear la UI ni exigir copiar enlaces.
  static void downloadOrOpen(String url, String filename) {
    if (url.isEmpty) return;
    downloadOrOpenPlatform(url, filename);
  }
}

