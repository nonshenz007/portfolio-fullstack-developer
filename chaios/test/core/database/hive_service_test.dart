import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';

import 'package:chaios/core/database/hive_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('HiveService', () {
    late Directory temp;

    setUp(() async {
      temp = await Directory.systemTemp.createTemp('chaios_hive_test_');
      await HiveService.instance.initialize(customPath: temp.path);
    });

    tearDown(() async {
      await HiveService.instance.close();
      if (await temp.exists()) {
        await temp.delete(recursive: true);
      }
    });

    test('initializes and opens boxes', () async {
      expect(HiveService.instance.isInitialized, isTrue);
      // Verify boxes are open
      expect(Hive.isBoxOpen('sales_box'), isTrue);
      expect(Hive.isBoxOpen('inventory_box'), isTrue);
      expect(Hive.isBoxOpen('settings_box'), isTrue);
    });
  });
}
