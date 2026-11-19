import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import '../cart_controller.dart';

class ProductDetailScreen extends StatefulWidget {
  const ProductDetailScreen({super.key, required this.product});
  final NovaProduct product;
  @override State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}
class _ProductDetailScreenState extends State<ProductDetailScreen> {
  @override void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      try { await context.read<NovaApiClient>().post('/analytics/events', data: {'product_id': widget.product.id, 'event_type': 'view', 'quantity': 1}); } catch (_) {}
    });
  }
  @override Widget build(BuildContext context) {
    final p = widget.product; final api = context.read<NovaApiClient>();
    return Scaffold(appBar: AppBar(title: const NovaBrand(compact: true), actions: [IconButton(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.close))]), body: ListView(padding: const EdgeInsets.all(18), children: [
      AspectRatio(aspectRatio: 1.08, child: NovaProductImage(api: api, imageUrl: p.imageUrl, category: p.category)), const SizedBox(height: 19),
      NovaEyebrow(p.category), const SizedBox(height: 7), Text(p.name, style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 8),
      Text('EGP ${p.price.toStringAsFixed(2)}', style: const TextStyle(color: NovaColors.red, fontWeight: FontWeight.w900, fontSize: 22)), const SizedBox(height: 14),
      NovaStatusPill(p.stockQty > 0 ? '${p.stockQty} in stock' : 'Out of stock'), const SizedBox(height: 18),
      const Text('Product details', style: TextStyle(fontWeight: FontWeight.w900)), const SizedBox(height: 7),
      Text(p.description.isEmpty ? 'A practical addition to your home, selected for dependable everyday use.' : p.description, style: Theme.of(context).textTheme.bodyMedium), const SizedBox(height: 24),
      FilledButton.icon(onPressed: p.stockQty <= 0 ? null : () { context.read<CartController>().add(p); api.post('/analytics/events', data: {'product_id': p.id, 'event_type': 'add_to_cart', 'quantity': 1}).catchError((_) {}); ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Added to your cart'))); }, icon: const Icon(Icons.shopping_bag_outlined), label: const Text('Add to cart'))
    ]));
  }
}
