// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

void downloadOrOpenPlatform(String url, String filename) {
  try {
    final anchor = html.AnchorElement(href: url)
      ..target = '_blank'
      ..download = filename;
    html.document.body?.children.add(anchor);
    anchor.click();
    anchor.remove();
  } catch (_) {
    try {
      html.window.open(url, '_blank');
    } catch (_) {
      // Fallback
    }
  }
}

