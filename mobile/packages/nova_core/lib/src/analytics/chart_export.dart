import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/rendering.dart';
import 'package:cross_file/cross_file.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class NovaChartExport {
  static Future<void> sharePng(GlobalKey key, String filename) async {
    final context = key.currentContext;
    if (context == null) return;
    final render = context.findRenderObject();
    if (render is! RenderRepaintBoundary) return;
    final image = await render.toImage(pixelRatio: 3);
    final data = await image.toByteData(format: ui.ImageByteFormat.png);
    if (data == null) return;
    final directory = await getTemporaryDirectory();
    final file = File('${directory.path}/$filename.png');
    await file.writeAsBytes(data.buffer.asUint8List(), flush: true);
    await Share.shareXFiles([XFile(file.path)], subject: filename);
  }

  static Future<void> shareCsv(String filename, List<List<Object?>> rows) async {
    final escaped = rows.map((row) => row.map((value) {
      final text = '${value ?? ''}';
      final safe = RegExp(r'^[\s]*[=+@-]').hasMatch(text) ? "'$text" : text;
      return '"${safe.replaceAll('"', '""')}"';
    }).join(',')).join('\r\n');
    final directory = await getTemporaryDirectory();
    final file = File('${directory.path}/$filename.csv');
    await file.writeAsString('\uFEFF$escaped', flush: true);
    await Share.shareXFiles([XFile(file.path)], subject: filename);
  }
}
