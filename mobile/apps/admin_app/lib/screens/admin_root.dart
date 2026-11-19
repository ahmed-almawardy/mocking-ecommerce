import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import 'admin_login_screen.dart';
import 'admin_shell.dart';

class AdminRoot extends StatefulWidget { const AdminRoot({super.key}); @override State<AdminRoot> createState() => _AdminRootState(); }
class _AdminRootState extends State<AdminRoot> {
  @override void initState() { super.initState(); WidgetsBinding.instance.addPostFrameCallback((_) async { await context.read<NovaOAuthFlow>().checkInitialLink(); await context.read<AuthController>().restore(); }); }
  @override Widget build(BuildContext context) => Consumer<AuthController>(builder: (context, auth, _) {
    if (!auth.isReady || (auth.isLoading && auth.user == null)) return const Scaffold(body: NovaLoading(label: 'Verifying administrator access…'));
    if (auth.user == null || !auth.isAdmin) return const AdminLoginScreen();
    return const AdminShell();
  });
}
