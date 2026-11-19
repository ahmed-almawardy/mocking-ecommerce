import 'package:flutter/material.dart';
import '../api/nova_api_client.dart';
import '../localization/nova_locale_controller.dart';
import '../models/nova_models.dart';
import '../theme/nova_theme.dart';

class NovaBrand extends StatelessWidget {
  const NovaBrand({super.key, this.compact = false, this.dark = false});
  final bool compact;
  final bool dark;
  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
    Container(width: compact ? 37 : 44, height: compact ? 37 : 44, decoration: BoxDecoration(color: NovaColors.red, borderRadius: BorderRadius.circular(13)), child: const Icon(Icons.home_rounded, color: Colors.white, size: 27)),
    const SizedBox(width: 10),
    Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
      Text('NOVA HOME', style: TextStyle(color: dark ? Colors.white : NovaColors.charcoal, fontSize: compact ? 15 : 18, fontWeight: FontWeight.w900, letterSpacing: -.3)),
      if (!compact) Text('A BETTER HOME. A HAPPIER YOU.', style: TextStyle(color: dark ? Colors.white70 : NovaColors.muted, fontSize: 8, fontWeight: FontWeight.w800, letterSpacing: 1)),
    ]),
  ]);
}

class NovaEyebrow extends StatelessWidget {
  const NovaEyebrow(this.text, {super.key});
  final String text;
  @override
  Widget build(BuildContext context) => Text(text.toUpperCase(), style: const TextStyle(color: NovaColors.red, fontSize: 10, fontWeight: FontWeight.w900, letterSpacing: 1.6));
}

class NovaSectionTitle extends StatelessWidget {
  const NovaSectionTitle(this.title, {super.key, this.subtitle, this.trailing});
  final String title;
  final String? subtitle;
  final Widget? trailing;
  @override
  Widget build(BuildContext context) => Row(crossAxisAlignment: CrossAxisAlignment.end, children: [
    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: Theme.of(context).textTheme.titleLarge), if (subtitle != null) ...[const SizedBox(height: 4), Text(subtitle!, style: Theme.of(context).textTheme.bodySmall)]])),
    if (trailing != null) trailing!,
  ]);
}

class NovaProductImage extends StatelessWidget {
  const NovaProductImage({super.key, required this.api, required this.imageUrl, required this.category, this.fit = BoxFit.contain, this.borderRadius = 14});
  final NovaApiClient api;
  final String imageUrl;
  final String category;
  final BoxFit fit;
  final double borderRadius;

  String get fallbackAsset {
    final value = category.toLowerCase();
    if (value.contains('refriger') || value.contains('fridge')) return 'assets/products/refrigerator.webp';
    if (value.contains('wash')) return 'assets/products/washing-machine.webp';
    if (value.contains('cook') || value.contains('oven') || value.contains('range')) return 'assets/products/gas-cooker.webp';
    if (value.contains('air') || value.contains('cool')) return 'assets/products/air-conditioner.webp';
    if (value.contains('micro')) return 'assets/products/microwave.webp';
    if (value.contains('tv') || value.contains('television')) return 'assets/products/television.webp';
    if (value.contains('coffee')) return 'assets/products/espresso-machine.webp';
    if (value.contains('blend') || value.contains('mixer')) return 'assets/products/blender.webp';
    if (value.contains('vacuum')) return 'assets/products/vacuum-cleaner.webp';
    return 'assets/products/microwave.webp';
  }

  @override
  Widget build(BuildContext context) {
    final url = imageUrl.trim();
    final uri = Uri.tryParse(url);
    final path = uri?.path ?? url;
    final isBundledAsset = path.startsWith('/images/products/');
    final localAsset = isBundledAsset ? 'assets/products/${path.split('/').last}' : fallbackAsset;
    final Widget image = url.isEmpty || isBundledAsset
        ? Image.asset(localAsset, package: 'nova_core', fit: fit, width: double.infinity, height: double.infinity,
            errorBuilder: (_, __, ___) => Image.asset(fallbackAsset, package: 'nova_core', fit: fit))
        : Image.network(api.resolveUrl(url), fit: fit, width: double.infinity, height: double.infinity,
            errorBuilder: (_, __, ___) => Image.asset(fallbackAsset, package: 'nova_core', fit: fit));
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: Container(color: NovaColors.surface, alignment: Alignment.center, child: image),
    );
  }
}

class NovaProductCard extends StatelessWidget {
  const NovaProductCard({super.key, required this.api, required this.product, required this.onTap, this.onAdd});
  final NovaApiClient api;
  final NovaProduct product;
  final VoidCallback onTap;
  final VoidCallback? onAdd;
  @override
  Widget build(BuildContext context) => InkWell(
    onTap: onTap, borderRadius: BorderRadius.circular(17),
    child: Container(
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(17), border: Border.all(color: NovaColors.border)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Expanded(child: Stack(children: [Positioned.fill(child: Padding(padding: const EdgeInsets.all(9), child: NovaProductImage(api: api, imageUrl: product.imageUrl, category: product.category))),
          if (product.badge != null && product.badge!.isNotEmpty) Positioned(top: 9, left: 9, child: Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5), decoration: BoxDecoration(color: const Color(0xFFFFEEEE), borderRadius: BorderRadius.circular(7)), child: Text(product.badge!.toUpperCase(), style: const TextStyle(color: NovaColors.red, fontSize: 8, fontWeight: FontWeight.w900))))])),
        Padding(padding: const EdgeInsets.fromLTRB(11, 2, 11, 11), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(product.name, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, height: 1.2)),
          const SizedBox(height: 6),
          Row(children: [Expanded(child: Text('EGP ${product.price.toStringAsFixed(2)}', style: const TextStyle(color: NovaColors.red, fontWeight: FontWeight.w900, fontSize: 13))),
            if (onAdd != null) InkWell(onTap: onAdd, child: Container(width: 31, height: 31, decoration: BoxDecoration(color: NovaColors.red, borderRadius: BorderRadius.circular(9)), child: const Icon(Icons.add_rounded, color: Colors.white, size: 21)))
          ]),
        ])),
      ]),
    ),
  );
}

class NovaLoading extends StatelessWidget {
  const NovaLoading({super.key, this.label = 'Loading NOVA HOME…'});
  final String label;
  @override
  Widget build(BuildContext context) => Center(child: Column(mainAxisSize: MainAxisSize.min, children: [const SizedBox(width: 28, height: 28, child: CircularProgressIndicator(strokeWidth: 2.7, color: NovaColors.red)), const SizedBox(height: 13), Text(label, style: Theme.of(context).textTheme.bodySmall)]));
}

class NovaErrorState extends StatelessWidget {
  const NovaErrorState({super.key, required this.message, this.onRetry});
  final String message;
  final VoidCallback? onRetry;
  @override
  Widget build(BuildContext context) => Center(child: Padding(padding: const EdgeInsets.all(25), child: Column(mainAxisSize: MainAxisSize.min, children: [const Icon(Icons.cloud_off_rounded, color: NovaColors.muted, size: 42), const SizedBox(height: 12), Text(message, textAlign: TextAlign.center), if (onRetry != null) ...[const SizedBox(height: 14), OutlinedButton.icon(onPressed: onRetry, icon: const Icon(Icons.refresh), label: const Text('Try again'))]])));
}

class NovaLanguageButton extends StatelessWidget {
  const NovaLanguageButton({super.key, required this.controller});
  final NovaLocaleController controller;
  @override
  Widget build(BuildContext context) => TextButton.icon(onPressed: controller.toggle, icon: const Icon(Icons.language_rounded, size: 17), label: Text(NovaStrings.t(controller.locale, 'language'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 12)));
}

class NovaStatusPill extends StatelessWidget {
  const NovaStatusPill(this.label, {super.key});
  final String label;
  @override
  Widget build(BuildContext context) {
    final value = label.toLowerCase();
    final color = value.contains('paid') || value.contains('active') || value.contains('success') ? const Color(0xFF16865A) : value.contains('fail') || value.contains('cancel') ? NovaColors.red : const Color(0xFF9A6700);
    return Container(padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5), decoration: BoxDecoration(color: color.withOpacity(.09), borderRadius: BorderRadius.circular(20)), child: Text(label.replaceAll('_', ' ').toUpperCase(), style: TextStyle(fontSize: 9, fontWeight: FontWeight.w900, color: color)));
  }
}
