import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';

class CustomerLoginScreen extends StatefulWidget {
  const CustomerLoginScreen({super.key});
  @override
  State<CustomerLoginScreen> createState() => _CustomerLoginScreenState();
}

class _CustomerLoginScreenState extends State<CustomerLoginScreen> {
  final _form = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  final _password = TextEditingController();
  bool _register = false;
  bool _whatsapp = false;
  bool _showPassword = false;
  Map<String, dynamic> _providers = {};
  bool _providerLoading = true;

  @override
  void initState() { super.initState(); _loadProviders(); }
  @override
  void dispose() { _name.dispose(); _email.dispose(); _phone.dispose(); _password.dispose(); super.dispose(); }

  Future<void> _loadProviders() async {
    try {
      final result = await context.read<NovaApiClient>().get('/auth/providers');
      if (mounted) setState(() => _providers = Map<String, dynamic>.from((result as Map)['providers'] as Map));
    } catch (_) {} finally { if (mounted) setState(() => _providerLoading = false); }
  }

  Future<void> _submit() async {
    if (!_form.currentState!.validate()) return;
    final auth = context.read<AuthController>();
    final ok = _register
      ? await auth.register(name: _name.text, email: _email.text, phone: _phone.text, password: _password.text, whatsappOptIn: _whatsapp)
      : await auth.login(_email.text, _password.text, adminOnly: false);
    if (ok && mounted) { ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(_register ? 'Your account is ready.' : 'Welcome back.'))); }
  }

  Future<void> _social(String provider) async {
    try { await context.read<NovaOAuthFlow>().start(provider); }
    catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e'))); }
  }

  @override
  Widget build(BuildContext context) {
    final locale = context.watch<NovaLocaleController>();
    final auth = context.watch<AuthController>();
    return Scaffold(body: SafeArea(child: Center(child: SingleChildScrollView(padding: const EdgeInsets.all(22), child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 460), child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const NovaBrand(), NovaLanguageButton(controller: locale)]),
      const SizedBox(height: 34),
      Container(height: 8, decoration: BoxDecoration(color: NovaColors.charcoal, borderRadius: BorderRadius.circular(8)), child: Align(alignment: Alignment.centerLeft, child: Container(width: 92, decoration: BoxDecoration(color: NovaColors.red, borderRadius: BorderRadius.circular(8))))),
      const SizedBox(height: 25),
      NovaEyebrow(_register ? 'Join the NOVA HOME family' : 'Welcome to NOVA HOME'),
      const SizedBox(height: 8),
      Text(_register ? 'Create your account.' : 'Good to see you again.', style: Theme.of(context).textTheme.headlineSmall),
      const SizedBox(height: 8), Text('Discover useful appliances, thoughtful design and everyday value.', style: Theme.of(context).textTheme.bodyMedium),
      const SizedBox(height: 25),
      Form(key: _form, child: Column(children: [
        if (_register) ...[
          TextFormField(controller: _name, textInputAction: TextInputAction.next, decoration: const InputDecoration(labelText: 'Full name', prefixIcon: Icon(Icons.person_outline)), validator: (v) => (v == null || v.trim().length < 2) ? 'Enter your name' : null),
          const SizedBox(height: 12),
          TextFormField(controller: _phone, keyboardType: TextInputType.phone, textInputAction: TextInputAction.next, decoration: const InputDecoration(labelText: 'Phone number (+20…)', prefixIcon: Icon(Icons.phone_outlined)), validator: (v) => (v == null || v.replaceAll(RegExp(r'\D'), '').length < 8) ? 'Enter a valid phone number' : null),
          const SizedBox(height: 12),
        ],
        TextFormField(controller: _email, keyboardType: TextInputType.emailAddress, textInputAction: TextInputAction.next, decoration: const InputDecoration(labelText: 'Email address', prefixIcon: Icon(Icons.mail_outline)), validator: (v) => (v == null || !v.contains('@') || !v.contains('.')) ? 'Enter a valid email address' : null),
        const SizedBox(height: 12),
        TextFormField(controller: _password, obscureText: !_showPassword, onFieldSubmitted: (_) => _submit(), decoration: InputDecoration(labelText: 'Password', prefixIcon: const Icon(Icons.lock_outline), suffixIcon: IconButton(onPressed: () => setState(() => _showPassword = !_showPassword), icon: Icon(_showPassword ? Icons.visibility_off : Icons.visibility))), validator: (v) => (v == null || v.length < (_register ? 10 : 1)) ? (_register ? 'Use at least 10 characters' : 'Enter your password') : null),
        if (_register) CheckboxListTile(value: _whatsapp, onChanged: (v) => setState(() => _whatsapp = v ?? false), contentPadding: EdgeInsets.zero, controlAffinity: ListTileControlAffinity.leading, title: const Text('Send me order updates on WhatsApp', style: TextStyle(fontSize: 12))),
      ])),
      if (auth.error != null) ...[const SizedBox(height: 12), Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: const Color(0xFFFFEEEE), borderRadius: BorderRadius.circular(10)), child: Text(auth.error!, style: const TextStyle(color: NovaColors.red, fontSize: 12)))],
      const SizedBox(height: 16),
      FilledButton(onPressed: auth.isLoading ? null : _submit, child: auth.isLoading ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : Text(_register ? 'Create account' : 'Sign in')),
      const SizedBox(height: 13),
      TextButton(onPressed: () => setState(() { _register = !_register; context.read<AuthController>().clearError(); }), child: Text(_register ? 'Already have an account? Sign in' : 'New to NOVA HOME? Create an account', style: const TextStyle(color: NovaColors.charcoal, fontWeight: FontWeight.w800))),
      const SizedBox(height: 22),
      Row(children: [const Expanded(child: Divider()), Padding(padding: const EdgeInsets.symmetric(horizontal: 10), child: Text('OR CONTINUE WITH', style: Theme.of(context).textTheme.bodySmall?.copyWith(letterSpacing: 1, fontWeight: FontWeight.w800))), const Expanded(child: Divider())]),
      const SizedBox(height: 13),
      Row(children: [for (final provider in ['google', 'facebook', 'apple']) Expanded(child: Padding(padding: const EdgeInsets.symmetric(horizontal: 4), child: OutlinedButton(onPressed: _providerLoading || _providers[provider] == null || (_providers[provider] as Map)['available'] != true ? null : () => _social(provider), child: Text(provider[0].toUpperCase() + provider.substring(1), style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)))))]),
      if (!_providerLoading && _providers.values.every((v) => v is Map && v['available'] != true)) Padding(padding: const EdgeInsets.only(top: 8), child: Text('Social sign-in becomes available when the provider credentials are configured on your NOVA HOME server.', textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodySmall)),
      Consumer<NovaOAuthFlow>(builder: (context, flow, _) => flow.error == null ? const SizedBox.shrink() : Padding(padding: const EdgeInsets.only(top: 8), child: Text(flow.error!, textAlign: TextAlign.center, style: const TextStyle(color: NovaColors.red, fontSize: 11)))),
      const SizedBox(height: 28),
      const Center(child: Text('SECURE CHECKOUT  •  LOCAL SUPPORT  •  EGYPT', style: TextStyle(fontSize: 9, color: NovaColors.muted, fontWeight: FontWeight.w900, letterSpacing: 1))),
    ]))))));
  }
}
