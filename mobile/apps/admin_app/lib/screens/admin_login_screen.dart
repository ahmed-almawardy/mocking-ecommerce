import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';

class AdminLoginScreen extends StatefulWidget { const AdminLoginScreen({super.key}); @override State<AdminLoginScreen> createState() => _AdminLoginScreenState(); }
class _AdminLoginScreenState extends State<AdminLoginScreen> {
  final form = GlobalKey<FormState>(); final email = TextEditingController(); final password = TextEditingController(); bool showPassword = false;
  Map<String, dynamic> providers = {}; bool providersLoading = true;
  @override void initState() { super.initState(); _loadProviders(); }
  Future<void> _loadProviders() async { try { final result = await context.read<NovaApiClient>().get('/auth/providers'); if (mounted) setState(() => providers = Map<String, dynamic>.from((result as Map)['providers'] as Map)); } catch (_) {} finally { if (mounted) setState(() => providersLoading = false); } }
  @override void dispose() { email.dispose(); password.dispose(); super.dispose(); }
  Future<void> _submit() async { if (!form.currentState!.validate()) return; await context.read<AuthController>().login(email.text, password.text, adminOnly: true); }
  Future<void> _social(String provider) async { try { await context.read<NovaOAuthFlow>().start(provider); } catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e'))); } }
  @override Widget build(BuildContext context) {
    final auth = context.watch<AuthController>(); final locale = context.watch<NovaLocaleController>();
    return Scaffold(body: SafeArea(child: Center(child: SingleChildScrollView(padding: const EdgeInsets.all(23), child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 430), child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      const NovaBrand(), const SizedBox(height: 39), Container(padding: const EdgeInsets.all(19), decoration: BoxDecoration(color: NovaColors.charcoal, borderRadius: BorderRadius.circular(20)), child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [NovaEyebrow('PRIVATE WORKSPACE'), SizedBox(height: 8), Text('Store control.\nAt your fingertips.', style: TextStyle(color: Colors.white, fontSize: 27, fontWeight: FontWeight.w900, height: 1.1)), SizedBox(height: 10), Text('Manage your NOVA HOME business securely from anywhere.', style: TextStyle(color: Colors.white70, fontSize: 12))])),
      const SizedBox(height: 25), Text('Administrator sign in', style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 7), const Text('Use your existing administrator account. Customer accounts cannot enter this workspace.', style: TextStyle(color: NovaColors.muted, fontSize: 12, height: 1.4)), const SizedBox(height: 19),
      Form(key: form, child: Column(children: [TextFormField(controller: email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Admin email', prefixIcon: Icon(Icons.mail_outline)), validator: (v) => (v == null || !v.contains('@')) ? 'Enter a valid email' : null), const SizedBox(height: 12), TextFormField(controller: password, obscureText: !showPassword, decoration: InputDecoration(labelText: 'Password', prefixIcon: const Icon(Icons.lock_outline), suffixIcon: IconButton(onPressed: () => setState(() => showPassword = !showPassword), icon: Icon(showPassword ? Icons.visibility_off : Icons.visibility))), validator: (v) => (v == null || v.isEmpty) ? 'Enter your password' : null)])),
      const SizedBox(height: 17),
      FilledButton(onPressed: auth.isLoading ? null : _submit, child: auth.isLoading ? const CircularProgressIndicator(color: Colors.white) : const Text('Secure sign in')),
      const SizedBox(height: 16),
      Row(children: [const Expanded(child: Divider()), Padding(padding: const EdgeInsets.symmetric(horizontal: 9), child: Text('OR CONTINUE WITH', style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 9, letterSpacing: 1, fontWeight: FontWeight.w800))), const Expanded(child: Divider())]),
      const SizedBox(height: 10),
      Row(children: [for (final provider in ['google', 'facebook', 'apple']) Expanded(child: Padding(padding: const EdgeInsets.symmetric(horizontal: 4), child: OutlinedButton(onPressed: providersLoading || providers[provider] == null || (providers[provider] as Map)['available'] != true ? null : () => _social(provider), child: Text(provider[0].toUpperCase() + provider.substring(1), style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)))))]),
      Consumer<NovaOAuthFlow>(builder: (context, flow, _) => flow.error == null ? const SizedBox.shrink() : Padding(padding: const EdgeInsets.only(top: 8), child: Text(flow.error!, textAlign: TextAlign.center, style: const TextStyle(color: NovaColors.red, fontSize: 11)))),
      if (auth.error != null) Padding(padding: const EdgeInsets.only(top: 8), child: Text(auth.error!, textAlign: TextAlign.center, style: const TextStyle(color: NovaColors.red, fontSize: 11))),
      const SizedBox(height: 10), NovaLanguageButton(controller: locale), const SizedBox(height: 21), const Center(child: Text('ROLE-BASED ACCESS  •  AUDITABLE OPERATIONS', style: TextStyle(color: NovaColors.muted, fontSize: 9, letterSpacing: 1, fontWeight: FontWeight.w900))),
    ])))));
  }
}
