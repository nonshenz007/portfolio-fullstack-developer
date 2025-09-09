import 'package:flutter_test/flutter_test.dart';
import 'package:chaios/features/sales/models/sale.dart';
import 'package:chaios/features/sales/models/sale_item.dart';
import 'package:chaios/features/sales/services/bill_service.dart';

void main() {
  test('BillService builds non-empty pdf', () async {
    final sale = Sale(
      billNumber: 'TEST-1',
      items: [SaleItem(name: 'Chai', quantity: 2, unitPrice: 30)],
      totalAmount: 60,
      paymentMethod: PaymentMethod.cash,
      createdAt: DateTime.now(),
    );

    final bytes = await BillService().buildBillPdf(sale);
    expect(bytes.isNotEmpty, isTrue);
  });
}
