import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import 'customer_shell.dart';
import 'login_screen.dart';

class CustomerRoot extends StatefulWidget {
  const CustomerRoot({super.key});
  @override
  State<CustomerRoot> createState() => _CustomerRootState();
}

class _CustomerRootState extends State<CustomerRoot> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await context.read<NovaOAuthFlow>().checkInitialLink();
      await context.read<AuthController>().restore();
    });
  }
  @override
  Widget build(BuildContext context) => Consumer<AuthController>(builder: (context, auth, _) {
    if (!auth.isReady || auth.isLoading && auth.user == null) return const Scaffold(body: NovaLoading(label: 'Preparing your store…'));
    return auth.user == null ? const CustomerLoginScreen() : const CustomerShell();
  });
}
