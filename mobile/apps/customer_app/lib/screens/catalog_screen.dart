import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import 'product_detail_screen.dart';
import '../cart_controller.dart';

class CustomerCatalogScreen extends StatefulWidget {
  const CustomerCatalogScreen({super.key, this.initialCategory});
  final String? initialCategory;
  @override
  State<CustomerCatalogScreen> createState() => _CustomerCatalogScreenState();
}
class _CustomerCatalogScreenState extends State<CustomerCatalogScreen> {
  final search = TextEditingController();
  List<NovaProduct> products = [];
  List<String> categories = [];
  String? category;
  bool loading = true;
  String? error;
  @override
  void initState() { super.initState(); category = widget.initialCategory; _load(); }
  @override
  void dispose() { search.dispose(); super.dispose(); }
  Future<void> _load() async {
    setState(() { loading = true; error = null; });
    try {
      final api = context.read<NovaApiClient>();
      final data = await api.get('/products', query: {'q': search.text.trim().isEmpty ? null : search.text.trim(), 'category': category, 'page': 1, 'page_size': 60});
      final cats = await api.get('/products/categories');
      if (!mounted) return;
      setState(() { products = asMapList(asMap(data)['items']).map(NovaProduct.fromJson).toList(); categories = (cats as List).map((e) => '$e').toList(); loading = false; });
    } catch (e) { if (mounted) setState(() { error = e.toString(); loading = false; }); }
  }
  @override
  Widget build(BuildContext context) {
    final api = context.read<NovaApiClient>();
    return Scaffold(appBar: AppBar(title: const NovaBrand(compact: true), actions: [IconButton(onPressed: _load, icon: const Icon(Icons.refresh_rounded))]), body: Column(children: [
      Padding(padding: const EdgeInsets.fromLTRB(16, 5, 16, 12), child: TextField(controller: search, textInputAction: TextInputAction.search, onSubmitted: (_) => _load(), decoration: InputDecoration(hintText: 'Search appliances, brands or model…', prefixIcon: const Icon(Icons.search), suffixIcon: IconButton(onPressed: _load, icon: const Icon(Icons.arrow_forward_rounded))))),
      SizedBox(height: 44, child: ListView(scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 16), children: [Padding(padding: const EdgeInsets.only(right: 7), child: ChoiceChip(label: const Text('All'), selected: category == null, onSelected: (_) { setState(() => category = null); _load(); })), ...categories.map((c) => Padding(padding: const EdgeInsets.only(right: 7), child: ChoiceChip(label: Text(c), selected: category == c, onSelected: (_) { setState(() => category = c); _load(); })))])),
      const SizedBox(height: 9),
      Expanded(child: loading ? const NovaLoading() : error != null ? NovaErrorState(message: error!, onRetry: _load) : products.isEmpty ? const Center(child: Text('No products match your search.')) : GridView.builder(padding: const EdgeInsets.all(15), itemCount: products.length, gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, childAspectRatio: .72, crossAxisSpacing: 11, mainAxisSpacing: 11), itemBuilder: (_, i) => NovaProductCard(api: api, product: products[i], onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ProductDetailScreen(product: products[i]))), onAdd: () { context.read<CartController>().add(products[i]); api.post('/analytics/events', data: {'product_id': products[i].id, 'event_type': 'add_to_cart', 'quantity': 1}).catchError((_) {}); ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Added to your cart'))); }))))
    ]));
  }
}
