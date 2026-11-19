import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import '../cart_controller.dart';
import 'checkout_screen.dart';

class CustomerCartScreen extends StatelessWidget {
  const CustomerCartScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final cart = context.watch<CartController>(); final api = context.read<NovaApiClient>();
    return Scaffold(appBar: AppBar(title: const Text('Shopping cart'), actions: [if (cart.items.isNotEmpty) TextButton(onPressed: cart.clear, child: const Text('Clear'))]), body: cart.items.isEmpty ? Center(child: Column(mainAxisSize: MainAxisSize.min, children: [const Icon(Icons.shopping_bag_outlined, size: 54, color: NovaColors.muted), const SizedBox(height: 12), Text(NovaStrings.t(context.watch<NovaLocaleController>().locale, 'empty_cart'), style: Theme.of(context).textTheme.titleMedium), const SizedBox(height: 8), const Text('Find something useful for your home.', style: TextStyle(color: NovaColors.muted))])) : ListView(padding: const EdgeInsets.all(16), children: [
      ...cart.items.map((line) => Container(margin: const EdgeInsets.only(bottom: 11), padding: const EdgeInsets.all(11), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(15), border: Border.all(color: NovaColors.border)), child: Row(children: [SizedBox(width: 84, height: 90, child: NovaProductImage(api: api, imageUrl: line.product.imageUrl, category: line.product.category)), const SizedBox(width: 12), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(line.product.name, maxLines: 2, style: const TextStyle(fontWeight: FontWeight.w800)), const SizedBox(height: 5), Text('EGP ${line.product.price.toStringAsFixed(2)}', style: const TextStyle(color: NovaColors.red, fontWeight: FontWeight.w900)), const SizedBox(height: 8), Row(children: [IconButton(visualDensity: VisualDensity.compact, onPressed: () => cart.setQuantity(line.product.id, line.quantity - 1), icon: const Icon(Icons.remove_circle_outline)), Text('${line.quantity}', style: const TextStyle(fontWeight: FontWeight.w900)), IconButton(visualDensity: VisualDensity.compact, onPressed: () => cart.setQuantity(line.product.id, line.quantity + 1), icon: const Icon(Icons.add_circle_outline)), const Spacer(), IconButton(onPressed: () => cart.remove(line.product.id), icon: const Icon(Icons.delete_outline, color: NovaColors.red))])]))])),
      const SizedBox(height: 7), _priceRow('Subtotal', cart.subtotal), _priceRow('Delivery', cart.shipping), const Divider(height: 24), _priceRow('Total', cart.total, strong: true), const SizedBox(height: 18), FilledButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CheckoutScreen())), child: const Text('Continue to checkout')),
    ]));
  }
  Widget _priceRow(String label, double value, {bool strong = false}) => Padding(padding: const EdgeInsets.symmetric(vertical: 5), child: Row(children: [Text(label, style: TextStyle(fontWeight: strong ? FontWeight.w900 : FontWeight.w500, color: strong ? NovaColors.charcoal : NovaColors.muted)), const Spacer(), Text('EGP ${value.toStringAsFixed(2)}', style: TextStyle(fontWeight: FontWeight.w900, fontSize: strong ? 18 : 13, color: strong ? NovaColors.red : NovaColors.ink))]));
}
