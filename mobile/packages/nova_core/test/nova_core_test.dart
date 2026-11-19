import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nova_core/nova_core.dart';

void main() {
  group('NOVA HOME shared models', () {
    test('product parsing converts decimal API values', () {
      final product = NovaProduct.fromJson({
        'id': 'p-1', 'sku': 'SKU-1', 'slug': 'test-product', 'name': 'Test product',
        'category': 'Kitchen Appliances', 'price': '1599.50', 'stock_qty': 4,
        'image_url': '/media/test.webp', 'featured': true,
      });
      expect(product.price, 1599.5);
      expect(product.stockQty, 4);
      expect(product.featured, isTrue);
    });

    test('user model defaults to customer role', () {
      final user = NovaUser.fromJson({'id': 'u-1', 'name': 'NOVA User'});
      expect(user.role, 'customer');
      expect(user.email, isNull);
    });

    test('offer parsing retains bilingual copy and image URL', () {
      final offer = NovaOffer.fromJson({'id': 'o-1', 'title': 'Home week', 'title_ar': 'أسبوع المنزل', 'subtitle': '', 'image_url': '/media/o.webp', 'link_url': '/en/products'});
      expect(offer.titleAr, 'أسبوع المنزل');
      expect(offer.imageUrl, '/media/o.webp');
    });
  });

  group('NOVA HOME locale', () {
    test('switches direction and localized navigation labels', () {
      final locale = NovaLocaleController();
      expect(locale.direction, TextDirection.ltr);
      locale.setLanguage('ar');
      expect(locale.direction, TextDirection.rtl);
      expect(NovaStrings.t(locale.locale, 'cart'), 'السلة');
      locale.setLanguage('en');
      expect(locale.direction, TextDirection.ltr);
    });
  });

  group('NOVA API client', () {
    test('normalizes server origin to the versioned API root', () {
      final api = NovaApiClient(baseUrl: 'https://api.example.test/', storageNamespace: 'test');
      expect(api.baseUrl, 'https://api.example.test/api/v1');
      expect(api.resolveUrl('/media/a.webp'), 'https://api.example.test/media/a.webp');
    });

    test('does not append the version prefix twice', () {
      final api = NovaApiClient(baseUrl: 'https://api.example.test/api/v1', storageNamespace: 'test');
      expect(api.baseUrl, 'https://api.example.test/api/v1');
    });
  });
}
