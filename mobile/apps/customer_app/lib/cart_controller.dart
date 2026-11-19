import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';
import 'package:nova_core/nova_core.dart';

class CartLine {
  CartLine(this.product, this.quantity);
  final NovaProduct product;
  int quantity;
}

class CartController extends ChangeNotifier {
  final Map<String, CartLine> _items = {};
  List<CartLine> get items => _items.values.toList(growable: false);
  static const _storageKey = 'nova_home_customer_cart_v1';

  Future<void> restore() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final stored = prefs.getString(_storageKey);
      if (stored == null || stored.isEmpty) return;
      final decoded = jsonDecode(stored);
      if (decoded is! List) return;
      _items.clear();
      for (final entry in decoded.whereType<Map>()) {
        final productJson = Map<String, dynamic>.from(entry['product'] as Map);
        final product = NovaProduct.fromJson(productJson);
        final quantity = int.tryParse('${entry['quantity']}') ?? 1;
        if (quantity > 0 && quantity <= 20) _items[product.id] = CartLine(product, quantity);
      }
      notifyListeners();
    } catch (_) {
      _items.clear();
    }
  }

  void _persist() {
    final value = _items.values.map((line) => {'product': line.product.toJson(), 'quantity': line.quantity}).toList();
    SharedPreferences.getInstance()
        .then((prefs) => prefs.setString(_storageKey, jsonEncode(value)))
        .catchError((_) => false);
  }
  int get count => _items.values.fold(0, (sum, line) => sum + line.quantity);
  double get subtotal => _items.values.fold(0, (sum, line) => sum + line.product.price * line.quantity);
  double get shipping => subtotal >= 2000 || subtotal == 0 ? 0 : 75;
  double get total => subtotal + shipping;
  void add(NovaProduct product, [int quantity = 1]) {
    final item = _items[product.id];
    if (item == null) { _items[product.id] = CartLine(product, quantity.clamp(1, 20).toInt()); }
    else { item.quantity = (item.quantity + quantity).clamp(1, 20).toInt(); }
    notifyListeners();
    _persist();
  }
  void setQuantity(String id, int quantity) {
    if (quantity <= 0) { _items.remove(id); }
    else if (_items.containsKey(id)) { _items[id]!.quantity = quantity.clamp(1, 20).toInt(); }
    notifyListeners();
    _persist();
  }
  void remove(String id) { _items.remove(id); notifyListeners(); _persist(); }
  void clear() { _items.clear(); notifyListeners(); _persist(); }
}
