import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import 'admin_resource_screen.dart';
import 'admin_offers_screen.dart';

class AdminMoreScreen extends StatelessWidget {
  const AdminMoreScreen({super.key});
  @override Widget build(BuildContext context) {
    final user = context.watch<AuthController>().user;
    return ListView(padding: const EdgeInsets.all(16), children: [const NovaEyebrow('STORE OPERATIONS'), Text('Manage your store', style: Theme.of(context).textTheme.headlineSmall), Text('Administration tools for your NOVA HOME business.', style: Theme.of(context).textTheme.bodySmall), const SizedBox(height: 16),
      _tile(context, Icons.local_offer_outlined, 'Offers & campaigns', 'Publish homepage banners and scheduled promotions', () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminOffersScreen()))),
      _tile(context, Icons.people_alt_outlined, 'Customers', 'Search customer accounts and contact details', () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminResourceScreen(resource: AdminResource.customers)))),
      _tile(context, Icons.payments_outlined, 'Payments', 'Payment provider, amount, status and reference', () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminResourceScreen(resource: AdminResource.payments)))),
      const SizedBox(height: 12), Container(padding: const EdgeInsets.all(15), decoration: BoxDecoration(color: NovaColors.charcoal, borderRadius: BorderRadius.circular(16)), child: Row(children: [const CircleAvatar(backgroundColor: NovaColors.red, child: Icon(Icons.admin_panel_settings_outlined, color: Colors.white)), const SizedBox(width: 11), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(user?.name ?? 'Administrator', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900)), Text(user?.email ?? '', style: const TextStyle(color: Colors.white70, fontSize: 11))]))]))
    ]);
  }
  Widget _tile(BuildContext context, IconData icon, String title, String subtitle, VoidCallback onTap) => Card(child: ListTile(onTap: onTap, contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7), leading: Container(width: 43, height: 43, decoration: BoxDecoration(color: NovaColors.red.withOpacity(.09), borderRadius: BorderRadius.circular(12)), child: Icon(icon, color: NovaColors.red)), title: Text(title, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 13)), subtitle: Text(subtitle, style: const TextStyle(fontSize: 10)), trailing: const Icon(Icons.chevron_right_rounded)));
}
