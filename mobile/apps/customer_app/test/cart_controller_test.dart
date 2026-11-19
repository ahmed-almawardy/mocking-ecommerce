import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:nova_core/nova_core.dart';
import '../lib/cart_controller.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() => SharedPreferences.setMockInitialValues({}));
  NovaProduct product(String id, double price) => NovaProduct(id: id, sku: id, slug: id, name: id, category: 'Appliances', price: price);
  group('CartController', () {
    test('adds items, calculates Egyptian delivery and total', () {
      final cart = CartController();
      cart.add(product('A', 1000));
      cart.add(product('B', 1200));
      expect(cart.count, 2);
      expect(cart.subtotal, 2200);
      expect(cart.shipping, 0);
      expect(cart.total, 2200);
    });
    test('charges delivery below the free delivery threshold', () {
      final cart = CartController()..add(product('A', 500));
      expect(cart.shipping, 75);
      expect(cart.total, 575);
    });
    test('merges same product and removes zero quantity', () {
      final cart = CartController()..add(product('A', 100))..add(product('A', 100), 2);
      expect(cart.count, 3);
      cart.setQuantity('A', 0);
      expect(cart.items, isEmpty);
    });
  });
}
