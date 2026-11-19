import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import 'orders_screen.dart';

class CustomerProfileScreen extends StatelessWidget {
  const CustomerProfileScreen({super.key});
  @override Widget build(BuildContext context) {
    final auth = context.watch<AuthController>(); final user = auth.user!; final locale = context.watch<NovaLocaleController>();
    return Scaffold(appBar: AppBar(title: Text(NovaStrings.t(locale.locale, 'account')), actions: [NovaLanguageButton(controller: locale)]), body: ListView(padding: const EdgeInsets.all(17), children: [
      Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(color: NovaColors.charcoal, borderRadius: BorderRadius.circular(18)), child: Row(children: [CircleAvatar(radius: 26, backgroundColor: NovaColors.red, child: Text(user.name.isNotEmpty ? user.name[0].toUpperCase() : 'N', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 20))), const SizedBox(width: 13), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(user.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 17)), const SizedBox(height: 3), Text(user.email ?? user.phone ?? '', style: const TextStyle(color: Colors.white70, fontSize: 12))]))])),
      const SizedBox(height: 20), _item(Icons.receipt_long_outlined, 'My orders', 'Track purchases and payment status', onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CustomerOrdersScreen()))), _item(Icons.location_on_outlined, 'Delivery details', 'Delivery information is collected at checkout'), _item(Icons.support_agent_outlined, 'Customer support', 'Contact NOVA HOME support'), _item(Icons.language_rounded, 'Language', locale.isArabic ? 'العربية' : 'English', onTap: locale.toggle), const SizedBox(height: 10), OutlinedButton.icon(onPressed: () async { await auth.logout(); }, icon: const Icon(Icons.logout_rounded, color: NovaColors.red), label: const Text('Sign out', style: TextStyle(color: NovaColors.red, fontWeight: FontWeight.w900))),
    ]));
  }
  Widget _item(IconData icon, String title, String subtitle, {VoidCallback? onTap}) => ListTile(onTap: onTap, contentPadding: const EdgeInsets.symmetric(horizontal: 4, vertical: 3), leading: Container(width: 42, height: 42, decoration: BoxDecoration(color: NovaColors.red.withOpacity(.08), borderRadius: BorderRadius.circular(12)), child: Icon(icon, color: NovaColors.red)), title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13)), subtitle: Text(subtitle, style: const TextStyle(fontSize: 11)), trailing: const Icon(Icons.chevron_right_rounded));
}
