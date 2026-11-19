import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';
import '../cart_controller.dart';
import 'product_detail_screen.dart';
import 'catalog_screen.dart';
import 'cart_screen.dart';
import 'orders_screen.dart';
import 'profile_screen.dart';

class CustomerShell extends StatefulWidget {
  const CustomerShell({super.key});
  @override
  State<CustomerShell> createState() => _CustomerShellState();
}

class _CustomerShellState extends State<CustomerShell> {
  int index = 0;
  late final pages = [
    CustomerHomeScreen(onOpenShop: () => setState(() => index = 1)),
    const CustomerCatalogScreen(), const CustomerCartScreen(), const CustomerOrdersScreen(), const CustomerProfileScreen(),
  ];
  @override
  Widget build(BuildContext context) {
    final cartCount = context.watch<CartController>().count;
    final locale = context.watch<NovaLocaleController>().locale;
    final labels = ['Home', 'Shop', 'Cart', 'Orders', 'Account'];
    final icons = [Icons.home_outlined, Icons.grid_view_rounded, Icons.shopping_bag_outlined, Icons.receipt_long_outlined, Icons.person_outline];
    return Scaffold(
      body: IndexedStack(index: index, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index, onDestinationSelected: (value) => setState(() => index = value),
        backgroundColor: Colors.white, indicatorColor: NovaColors.red.withOpacity(.10),
        destinations: [for (var i = 0; i < labels.length; i++) NavigationDestination(
          icon: Badge(isLabelVisible: i == 2 && cartCount > 0, label: Text('$cartCount'), child: Icon(icons[i])),
          selectedIcon: Icon(icons[i], color: NovaColors.red), label: NovaStrings.t(locale, ['home','shop','cart','orders','account'][i]),
        )],
      ),
    );
  }
}

class CustomerHomeScreen extends StatefulWidget {
  const CustomerHomeScreen({super.key, this.onOpenShop});
  final VoidCallback? onOpenShop;
  @override
  State<CustomerHomeScreen> createState() => _CustomerHomeScreenState();
}

class _CustomerHomeScreenState extends State<CustomerHomeScreen> {
  List<NovaProduct> products = [];
  List<NovaOffer> offers = [];
  List<String> categories = [];
  bool loading = true;
  String? error;
  int slide = 0;
  late final PageController _pageController = PageController();
  Timer? _timer;

  @override
  void initState() { super.initState(); _load(); _timer = Timer.periodic(const Duration(seconds: 5), (_) { if (offers.isNotEmpty && mounted) { slide = (slide + 1) % offers.length; _pageController.animateToPage(slide, duration: const Duration(milliseconds: 500), curve: Curves.easeInOut); } }); }
  @override
  void dispose() { _timer?.cancel(); _pageController.dispose(); super.dispose(); }

  Future<void> _load() async {
    setState(() { loading = true; error = null; });
    try {
      final api = context.read<NovaApiClient>();
      final results = await Future.wait([api.get('/products', query: {'featured': true, 'page_size': 12}), api.get('/offers/active'), api.get('/products/categories')]);
      final productJson = Map<String, dynamic>.from(results[0] as Map);
      if (!mounted) return;
      setState(() {
        products = asMapList(productJson['items']).map(NovaProduct.fromJson).toList();
        offers = asMapList(asMap(results[1])['items']).map(NovaOffer.fromJson).take(4).toList();
        categories = (results[2] as List).map((e) => '$e').toList();
        loading = false;
      });
    } catch (e) { if (mounted) setState(() { error = e.toString(); loading = false; }); }
  }

  void _openProduct(NovaProduct product) => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ProductDetailScreen(product: product)));

  @override
  Widget build(BuildContext context) {
    final api = context.read<NovaApiClient>();
    final locale = context.watch<NovaLocaleController>();
    return RefreshIndicator(onRefresh: _load, color: NovaColors.red, child: CustomScrollView(slivers: [
      SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.fromLTRB(18, 15, 18, 12), child: Row(children: [const NovaBrand(compact: true), const Spacer(), NovaLanguageButton(controller: locale), IconButton(tooltip: 'Browse products', onPressed: widget.onOpenShop, icon: const Icon(Icons.search_rounded, color: NovaColors.charcoal))]))),
      SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.symmetric(horizontal: 18), child: InkWell(onTap: widget.onOpenShop, borderRadius: BorderRadius.circular(13), child: Container(padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 13), decoration: BoxDecoration(color: Colors.white, border: Border.all(color: NovaColors.border), borderRadius: BorderRadius.circular(13)), child: Row(children: [const Icon(Icons.search_rounded, color: NovaColors.muted), const SizedBox(width: 10), Text(NovaStrings.t(locale.locale, 'search'), style: const TextStyle(color: NovaColors.muted)), const Spacer(), const Icon(Icons.tune_rounded, size: 18, color: NovaColors.charcoal)]))))),
      SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.fromLTRB(18, 18, 18, 0), child: _buildHero(api))),
      SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.fromLTRB(18, 24, 18, 12), child: NovaSectionTitle(NovaStrings.t(locale.locale, 'categories'), subtitle: 'Find what makes everyday life easier.'))),
      SliverToBoxAdapter(child: SizedBox(height: 84, child: ListView.separated(scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 18), itemCount: categories.length, separatorBuilder: (_, __) => const SizedBox(width: 9), itemBuilder: (context, i) => InkWell(onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => CustomerCatalogScreen(initialCategory: categories[i]))), child: Container(width: 134, padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(13), border: Border.all(color: NovaColors.border)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [const Icon(Icons.kitchen_outlined, color: NovaColors.red, size: 21), const SizedBox(height: 7), Text(categories[i], maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800))]))))),
      SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.fromLTRB(18, 23, 18, 12), child: NovaSectionTitle(NovaStrings.t(locale.locale, 'featured'), subtitle: 'Useful details. Thoughtful design. Everyday performance.'))),
      if (loading) const SliverToBoxAdapter(child: Padding(padding: EdgeInsets.all(28), child: NovaLoading()))
      else if (error != null) SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.all(18), child: NovaErrorState(message: error!, onRetry: _load)))
      else if (products.isEmpty) SliverToBoxAdapter(child: Padding(padding: const EdgeInsets.all(20), child: Text('Products will appear here when your catalog is ready.', style: Theme.of(context).textTheme.bodyMedium)))
      else SliverPadding(padding: const EdgeInsets.fromLTRB(18, 0, 18, 28), sliver: SliverGrid.builder(gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, mainAxisSpacing: 12, crossAxisSpacing: 12, childAspectRatio: .72), itemCount: products.length, itemBuilder: (_, i) => NovaProductCard(api: api, product: products[i], onTap: () => _openProduct(products[i]), onAdd: products[i].stockQty > 0 ? () { context.read<CartController>().add(products[i]); _track(products[i], 'add_to_cart'); ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Added to your cart'))); } : null))),
    ]));
  }

  Widget _buildHero(NovaApiClient api) {
    if (offers.isEmpty) return Container(height: 184, decoration: BoxDecoration(color: NovaColors.charcoal, borderRadius: BorderRadius.circular(18)), padding: const EdgeInsets.all(20), child: const Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.center, children: [NovaEyebrow('A LITTLE MORE FOR YOUR HOME'), SizedBox(height: 8), Text('Good choices.\nEveryday value.', style: TextStyle(color: Colors.white, fontSize: 25, fontWeight: FontWeight.w900)), SizedBox(height: 7), Text('Discover practical appliances for the way you live.', style: TextStyle(color: Colors.white70, fontSize: 12))]));
    return Column(children: [SizedBox(height: 190, child: ClipRRect(borderRadius: BorderRadius.circular(18), child: PageView.builder(controller: _pageController, itemCount: offers.length, onPageChanged: (i) => setState(() => slide = i), itemBuilder: (context, i) {
      final offer = offers[i];
      final path = Uri.tryParse(offer.imageUrl)?.path ?? offer.imageUrl;
      final localAsset = path.startsWith('/images/offers/') ? 'assets/offers/${path.split('/').last}' : null;
      final locale = context.read<NovaLocaleController>();
      final offerTitle = locale.isArabic ? (offer.titleAr?.isNotEmpty == true ? offer.titleAr! : offer.title) : offer.title;
      final offerSubtitle = locale.isArabic ? (offer.subtitleAr?.isNotEmpty == true ? offer.subtitleAr! : offer.subtitle) : offer.subtitle;
      final background = localAsset != null
          ? Image.asset(localAsset, package: 'nova_core', fit: BoxFit.cover, errorBuilder: (_, __, ___) => Image.asset('assets/offers/offer-${i + 1}.webp', package: 'nova_core', fit: BoxFit.cover))
          : Image.network(api.resolveUrl(offer.imageUrl), fit: BoxFit.cover, errorBuilder: (_, __, ___) => Image.asset('assets/offers/offer-${i + 1}.webp', package: 'nova_core', fit: BoxFit.cover));
      return Stack(fit: StackFit.expand, children: [background, Container(decoration: const BoxDecoration(gradient: LinearGradient(colors: [Color(0xCC20252B), Color(0x0020252B)], begin: Alignment.centerLeft, end: Alignment.centerRight))), Positioned(left: 17, top: 24, right: 16, child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [if (offer.badge != null) NovaEyebrow(offer.badge!), const SizedBox(height: 5), Text(offerTitle, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.white, fontSize: 21, fontWeight: FontWeight.w900)), const SizedBox(height: 5), Text(offerSubtitle, maxLines: 2, style: const TextStyle(color: Colors.white70, fontSize: 11)), const SizedBox(height: 12), InkWell(onTap: widget.onOpenShop, borderRadius: BorderRadius.circular(9), child: Container(padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 9), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(9)), child: const Text('Explore offers  →', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: NovaColors.charcoal)))) ]))]);
    }))), const SizedBox(height: 11), Row(mainAxisAlignment: MainAxisAlignment.center, children: [for (var i = 0; i < offers.length; i++) GestureDetector(onTap: () { _pageController.animateToPage(i, duration: const Duration(milliseconds: 300), curve: Curves.easeInOut); }, child: AnimatedContainer(duration: const Duration(milliseconds: 180), margin: const EdgeInsets.symmetric(horizontal: 3), width: slide == i ? 19 : 6, height: 6, decoration: BoxDecoration(color: slide == i ? NovaColors.red : const Color(0xFFD3D6DA), borderRadius: BorderRadius.circular(10))))])]);
  }

  Future<void> _track(NovaProduct product, String type) async { try { await context.read<NovaApiClient>().post('/analytics/events', data: {'product_id': product.id, 'event_type': type, 'quantity': 1}); } catch (_) {} }
}

