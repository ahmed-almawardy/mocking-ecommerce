class NovaUser {
  const NovaUser({required this.id, required this.name, this.email, this.phone, this.role = 'customer', this.whatsappOptIn = false});
  final String id;
  final String name;
  final String? email;
  final String? phone;
  final String role;
  final bool whatsappOptIn;

  factory NovaUser.fromJson(Map<String, dynamic> json) => NovaUser(
    id: '${json['id'] ?? ''}', name: '${json['name'] ?? 'NOVA HOME user'}',
    email: json['email'] as String?, phone: json['phone'] as String?,
    role: '${json['role'] ?? 'customer'}', whatsappOptIn: json['whatsapp_opt_in'] == true,
  );
}

class NovaProduct {
  const NovaProduct({required this.id, required this.sku, required this.slug, required this.name, required this.category, required this.price, this.description = '', this.imageUrl = '', this.stockQty = 0, this.compareAtPrice, this.badge, this.featured = false});
  final String id, sku, slug, name, category, description, imageUrl;
  final double price;
  final int stockQty;
  final double? compareAtPrice;
  final String? badge;
  final bool featured;

  factory NovaProduct.fromJson(Map<String, dynamic> j) => NovaProduct(
    id: '${j['id']}', sku: '${j['sku'] ?? ''}', slug: '${j['slug'] ?? ''}',
    name: '${j['name'] ?? 'Product'}', category: '${j['category'] ?? ''}',
    description: '${j['description'] ?? ''}', price: double.tryParse('${j['price']}') ?? 0,
    imageUrl: '${j['image_url'] ?? ''}', stockQty: int.tryParse('${j['stock_qty']}') ?? 0,
    compareAtPrice: j['compare_at_price'] == null ? null : double.tryParse('${j['compare_at_price']}'),
    badge: j['badge'] as String?, featured: j['featured'] == true,
  );

  Map<String, dynamic> toJson() => {
    'id': id, 'sku': sku, 'slug': slug, 'name': name, 'category': category,
    'description': description, 'price': price, 'image_url': imageUrl,
    'stock_qty': stockQty, 'compare_at_price': compareAtPrice, 'badge': badge, 'featured': featured,
  };
}

class NovaOffer {
  const NovaOffer({required this.id, required this.title, required this.subtitle, required this.imageUrl, required this.linkUrl, this.titleAr, this.subtitleAr, this.badge});
  final String id, title, subtitle, imageUrl, linkUrl;
  final String? titleAr, subtitleAr, badge;
  factory NovaOffer.fromJson(Map<String, dynamic> j) => NovaOffer(
    id: '${j['id']}', title: '${j['title'] ?? ''}', subtitle: '${j['subtitle'] ?? ''}',
    titleAr: j['title_ar'] as String?, subtitleAr: j['subtitle_ar'] as String?,
    imageUrl: '${j['image_url'] ?? ''}', linkUrl: '${j['link_url'] ?? '/en/products'}', badge: j['badge'] as String?,
  );
}

class NovaOrder {
  const NovaOrder({required this.orderNumber, required this.status, required this.paymentStatus, required this.total, required this.currency, this.createdAt, this.paymentUrl, this.items = const []});
  final String orderNumber, status, paymentStatus, currency;
  final double total;
  final DateTime? createdAt;
  final String? paymentUrl;
  final List<Map<String, dynamic>> items;
  factory NovaOrder.fromJson(Map<String, dynamic> j) => NovaOrder(
    orderNumber: '${j['order_number'] ?? ''}', status: '${j['status'] ?? ''}', paymentStatus: '${j['payment_status'] ?? ''}',
    total: double.tryParse('${j['total']}') ?? 0, currency: '${j['currency'] ?? 'EGP'}',
    createdAt: DateTime.tryParse('${j['created_at'] ?? ''}'), paymentUrl: j['payment_url'] as String?,
    items: (j['items'] is List) ? (j['items'] as List).whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList() : const [],
  );
}

double asDouble(dynamic value) => double.tryParse('$value') ?? 0;
int asInt(dynamic value) => int.tryParse('$value') ?? 0;
Map<String, dynamic> asMap(dynamic value) => value is Map<String, dynamic> ? value : <String, dynamic>{};
List<Map<String, dynamic>> asMapList(dynamic value) => value is List ? value.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList() : <Map<String, dynamic>>[];
