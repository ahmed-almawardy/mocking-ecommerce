import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:nova_core/nova_core.dart';
import '../cart_controller.dart';

class CheckoutScreen extends StatefulWidget { const CheckoutScreen({super.key}); @override State<CheckoutScreen> createState() => _CheckoutScreenState(); }
class _CheckoutScreenState extends State<CheckoutScreen> {
  final form = GlobalKey<FormState>();
  final name = TextEditingController(); final phone = TextEditingController(); final address = TextEditingController(); final city = TextEditingController(text: 'Cairo');
  bool busy = false;
  @override void dispose() { name.dispose(); phone.dispose(); address.dispose(); city.dispose(); super.dispose(); }
  Future<void> submit() async {
    if (!form.currentState!.validate()) return;
    final cart = context.read<CartController>();
    if (cart.items.isEmpty) return;
    setState(() => busy = true);
    try {
      final response = await context.read<NovaApiClient>().post('/orders', data: {
        'items': cart.items.map((e) => {'product_id': e.product.id, 'quantity': e.quantity}).toList(),
        'shipping_name': name.text.trim(), 'shipping_phone': phone.text.trim(),
        'shipping_address': address.text.trim(), 'shipping_city': city.text.trim(),
      });
      final result = Map<String, dynamic>.from(response as Map);
      cart.clear();
      if (!mounted) return;
      final paymentUrl = result['payment_url'] as String?;
      if (paymentUrl != null && paymentUrl.isNotEmpty) {
        final opened = await launchUrl(Uri.parse(paymentUrl), mode: LaunchMode.externalApplication);
        if (!opened && mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Order created, but the payment page could not be opened. Find it in Orders to retry.')));
      }
      if (mounted) { await showDialog<void>(context: context, builder: (_) => AlertDialog(title: const Text('Order created'), content: Text('Your order ${result['order_number']} has been saved. Payment is pending until Kashier confirms it.'), actions: [TextButton(onPressed: () { Navigator.pop(context); Navigator.pop(context); }, child: const Text('Done'))])); }
    } catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e'))); }
    finally { if (mounted) setState(() => busy = false); }
  }
  @override Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('Delivery details')), body: Form(key: form, child: ListView(padding: const EdgeInsets.all(18), children: [
      const NovaEyebrow('Where should we deliver?'), const SizedBox(height: 8), Text('Delivery information', style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 18),
      TextFormField(controller: name, decoration: const InputDecoration(labelText: 'Recipient name', prefixIcon: Icon(Icons.person_outline)), validator: (v) => (v == null || v.trim().length < 2) ? 'Enter recipient name' : null), const SizedBox(height: 12),
      TextFormField(controller: phone, keyboardType: TextInputType.phone, decoration: const InputDecoration(labelText: 'Phone number', prefixIcon: Icon(Icons.phone_outlined)), validator: (v) => (v == null || v.replaceAll(RegExp(r'\D'), '').length < 8) ? 'Enter a valid phone' : null), const SizedBox(height: 12),
      TextFormField(controller: address, maxLines: 3, decoration: const InputDecoration(labelText: 'Full address', alignLabelWithHint: true, prefixIcon: Icon(Icons.location_on_outlined)), validator: (v) => (v == null || v.trim().length < 8) ? 'Enter a complete address' : null), const SizedBox(height: 12),
      TextFormField(controller: city, decoration: const InputDecoration(labelText: 'City', prefixIcon: Icon(Icons.location_city_outlined)), validator: (v) => (v == null || v.trim().length < 2) ? 'Enter your city' : null),
      const SizedBox(height: 18), Container(padding: const EdgeInsets.all(14), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14), border: Border.all(color: NovaColors.border)), child: const Row(children: [Icon(Icons.lock_outline, color: NovaColors.red), SizedBox(width: 10), Expanded(child: Text('Your payment will be processed securely by Kashier. NOVA HOME confirms the order only after the provider verifies payment.', style: TextStyle(fontSize: 12, height: 1.4)))])),
      const SizedBox(height: 20), FilledButton(onPressed: busy ? null : submit, child: busy ? const CircularProgressIndicator(color: Colors.white) : const Text('Place order & continue to payment')),
    ])));
  }
}
