import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import 'screens/customer_root.dart';
import 'cart_controller.dart';

const apiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000');

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final api = NovaApiClient(baseUrl: apiBaseUrl, storageNamespace: 'nova_customer');
  final auth = AuthController(api);
  final locale = NovaLocaleController();
  final oauth = NovaOAuthFlow(api: api, auth: auth, appType: 'customer', scheme: 'novahome');
  final cart = CartController();
  await cart.restore();
  runApp(MultiProvider(
    providers: [
      Provider<NovaApiClient>.value(value: api),
      ChangeNotifierProvider<AuthController>.value(value: auth),
      ChangeNotifierProvider<NovaLocaleController>.value(value: locale),
      ChangeNotifierProvider<NovaOAuthFlow>.value(value: oauth),
      ChangeNotifierProvider<CartController>.value(value: cart),
    ],
    child: const NovaCustomerApp(),
  ));
}

class NovaCustomerApp extends StatelessWidget {
  const NovaCustomerApp({super.key});
  @override
  Widget build(BuildContext context) => Consumer<NovaLocaleController>(builder: (context, locale, _) => MaterialApp(
    title: 'NOVA HOME', debugShowCheckedModeBanner: false,
    theme: NovaTheme.light, locale: locale.locale,
    supportedLocales: const [Locale('en'), Locale('ar')],
    localizationsDelegates: GlobalMaterialLocalizations.delegates,
    builder: (context, child) => Directionality(textDirection: locale.direction, child: child ?? const SizedBox.shrink()),
    home: const CustomerRoot(),
  ));
}

