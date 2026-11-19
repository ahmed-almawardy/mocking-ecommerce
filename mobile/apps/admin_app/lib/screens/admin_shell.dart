import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import 'admin_dashboard_screen.dart';
import 'admin_products_screen.dart';
import 'admin_orders_screen.dart';
import 'admin_more_screen.dart';

class AdminShell extends StatefulWidget { const AdminShell({super.key}); @override State<AdminShell> createState() => _AdminShellState(); }
class _AdminShellState extends State<AdminShell> {
  int index = 0;
  late final pages = const [AdminDashboardScreen(), AdminProductsScreen(), AdminOrdersScreen(), AdminMoreScreen()];
  @override Widget build(BuildContext context) {
    final auth = context.watch<AuthController>();
    return Scaffold(
      appBar: AppBar(title: const NovaBrand(compact: true), actions: [NovaLanguageButton(controller: context.watch<NovaLocaleController>()), PopupMenuButton<String>(icon: const Icon(Icons.account_circle_outlined), onSelected: (v) async { if (v == 'logout') await auth.logout(); }, itemBuilder: (_) => [PopupMenuItem(value: 'logout', child: Row(children: [const Icon(Icons.logout, size: 18), const SizedBox(width: 9), Text('Sign out (${auth.user?.name ?? 'Admin'})')]))])]),
      body: IndexedStack(index: index, children: pages),
      bottomNavigationBar: NavigationBar(selectedIndex: index, onDestinationSelected: (v) => setState(() => index = v), destinations: const [
        NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard, color: NovaColors.red), label: 'Overview'),
        NavigationDestination(icon: Icon(Icons.inventory_2_outlined), selectedIcon: Icon(Icons.inventory_2, color: NovaColors.red), label: 'Products'),
        NavigationDestination(icon: Icon(Icons.receipt_long_outlined), selectedIcon: Icon(Icons.receipt_long, color: NovaColors.red), label: 'Orders'),
        NavigationDestination(icon: Icon(Icons.grid_view_rounded), selectedIcon: Icon(Icons.grid_view, color: NovaColors.red), label: 'Manage'),
      ]),
    );
  }
}
