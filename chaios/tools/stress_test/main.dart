import 'dart:io';
import 'dart:math';

import 'package:flutter/widgets.dart';
import 'package:intl/intl.dart';

import 'package:chaios/core/database/hive_service.dart';
import 'package:chaios/features/inventory/data/inventory_repository.dart';
import 'package:chaios/features/inventory/models/inventory_item.dart';
import 'package:chaios/features/sales/data/sales_repository.dart';
import 'package:chaios/features/sales/models/sale.dart';
import 'package:chaios/features/sales/models/sale_item.dart';
import 'package:chaios/features/credit/data/credit_repository.dart';
import 'package:chaios/features/reports/services/report_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final Stopwatch sw = Stopwatch()..start();
  stdout.writeln('Stress test starting...');

  // Initialize database
  await HiveService.instance.initialize();

  final InventoryRepository invRepo = InventoryRepository();
  final SalesRepository salesRepo = SalesRepository();
  final CreditRepository creditRepo = CreditRepository();
  await invRepo.init();
  await salesRepo.init();
  await creditRepo.init();

  final Random rng = Random(42);
  int nextInt(int min, int max) => min + rng.nextInt((max - min) + 1);
  double nextPrice(double min, double max) =>
      min + rng.nextDouble() * (max - min);

  // Create inventory
  const int numItems = 500;
  stdout.writeln('Creating $numItems inventory items...');
  for (int i = 0; i < numItems; i++) {
    final InventoryItem item = InventoryItem.create(
      name: 'Item ${i + 1}',
      sellingPrice: double.parse(nextPrice(5, 500).toStringAsFixed(2)),
      costPrice: double.parse(nextPrice(2, 480).toStringAsFixed(2)),
      currentStock: nextInt(0, 500),
      minimumStock: nextInt(3, 15),
      category: (i % 5 == 0)
          ? 'Food'
          : (i % 5 == 1)
          ? 'Drink'
          : null,
    );
    await invRepo.saveItem(item);
  }

  final List<InventoryItem> items = await invRepo.getAllItems();
  stdout.writeln('Inventory ready: ${items.length}');

  // Create sales
  const int numSales = 2000;
  stdout.writeln('Creating $numSales sales...');
  final DateTime now = DateTime.now();
  for (int s = 0; s < numSales; s++) {
    final int lineCount = nextInt(1, 10);
    final List<SaleItem> lines = <SaleItem>[];
    for (int l = 0; l < lineCount; l++) {
      final InventoryItem inv = items[nextInt(0, items.length - 1)];
      final int qty = nextInt(1, 5);
      lines.add(
        SaleItem(
          name: inv.name,
          quantity: qty,
          unitPrice: inv.sellingPrice,
          costPrice: inv.costPrice,
          inventoryItemId: inv.id,
        ),
      );
    }
    final double total = lines.fold(0.0, (p, e) => p + e.lineTotal);
    final PaymentMethod pm;
    final int pmRoll = nextInt(1, 100);
    if (pmRoll <= 50) {
      pm = PaymentMethod.cash;
    } else if (pmRoll <= 85) {
      pm = PaymentMethod.upi;
    } else {
      pm = PaymentMethod.credit;
    }

    final DateTime createdAt = now.subtract(
      Duration(
        days: nextInt(0, 30),
        hours: nextInt(0, 23),
        minutes: nextInt(0, 59),
      ),
    );
    final Sale sale = Sale(
      billNumber: 'BILL-${now.millisecondsSinceEpoch}-$s',
      items: lines,
      totalAmount: total,
      paymentMethod: pm,
      createdAt: createdAt,
      customerName: pm == PaymentMethod.credit
          ? 'Customer ${nextInt(1, 300)}'
          : null,
      customerPhone: pm == PaymentMethod.credit
          ? '98${nextInt(10000000, 99999999)}'
          : null,
    );
    await salesRepo.addSale(sale);
    // Reduce inventory stock (mirror app behavior)
    for (final SaleItem li in lines) {
      if (li.inventoryItemId != null && li.inventoryItemId!.isNotEmpty) {
        final InventoryItem? inv = await invRepo.getById(li.inventoryItemId!);
        if (inv != null) {
          await invRepo.saveItem(inv.reduceStock(li.quantity));
        }
      }
    }

    // Credit details
    if (pm == PaymentMethod.credit) {
      if (rng.nextBool()) {
        final DateTime due = createdAt.add(Duration(days: nextInt(15, 45)));
        await creditRepo.setDueDate(billNumber: sale.billNumber, dueDate: due);
      }
      // Add 0-3 partial payments
      final int pays = nextInt(0, 3);
      for (int p = 0; p < pays; p++) {
        final double amt = double.parse(
          (total * rng.nextDouble() * 0.6).toStringAsFixed(2),
        );
        await creditRepo.addPayment(
          billNumber: sale.billNumber,
          amount: amt,
          method: rng.nextBool() ? 'cash' : 'upi',
          date: createdAt.add(Duration(days: nextInt(0, 20))),
        );
      }
    }
  }

  stdout.writeln('Sales created. Computing reports...');
  final ReportService reports = ReportService();
  // ignore: unused_local_variable
  final DateFormat df = DateFormat('yyyy-MM-dd');
  (DateTime, DateTime) rangeDays(int days) {
    final DateTime end = DateTime.now();
    final DateTime start = end.subtract(Duration(days: days));
    return (start, end);
  }

  final allSales = salesRepo.getAllSales();
  final (tStart, tEnd) = rangeDays(0);
  final (wStart, wEnd) = rangeDays(7);
  final (mStart, mEnd) = rangeDays(30);
  final t = reports.compute(
    allSales,
    DateTime(tStart.year, tStart.month, tStart.day),
    DateTime(tEnd.year, tEnd.month, tEnd.day, 23, 59, 59),
  );
  final w = reports.compute(
    allSales,
    DateTime(wStart.year, wStart.month, wStart.day),
    DateTime(wEnd.year, wEnd.month, wEnd.day, 23, 59, 59),
  );
  final m = reports.compute(
    allSales,
    DateTime(mStart.year, mStart.month, mStart.day),
    DateTime(mEnd.year, mEnd.month, mEnd.day, 23, 59, 59),
  );

  stdout.writeln(
    'Today: total=${t.totalSales.toStringAsFixed(2)} cash=${t.cashTotal.toStringAsFixed(2)} upi=${t.upiTotal.toStringAsFixed(2)} creditOut=${t.creditOutstanding.toStringAsFixed(2)} bills=${t.billCount}',
  );
  stdout.writeln(
    'Week:  total=${w.totalSales.toStringAsFixed(2)} cash=${w.cashTotal.toStringAsFixed(2)} upi=${w.upiTotal.toStringAsFixed(2)} creditOut=${w.creditOutstanding.toStringAsFixed(2)} bills=${w.billCount}',
  );
  stdout.writeln(
    'Month: total=${m.totalSales.toStringAsFixed(2)} cash=${m.cashTotal.toStringAsFixed(2)} upi=${m.upiTotal.toStringAsFixed(2)} creditOut=${m.creditOutstanding.toStringAsFixed(2)} bills=${m.billCount}',
  );

  final stats = HiveService.instance.getDatabaseStats();
  stdout.writeln('DB stats: $stats');

  sw.stop();
  stdout.writeln('Stress test finished in ${sw.elapsedMilliseconds} ms');

  // Exit process
  exit(0);
}
