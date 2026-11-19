import 'package:flutter/material.dart';

class NovaLocaleController extends ChangeNotifier {
  Locale _locale = const Locale('en');
  Locale get locale => _locale;
  bool get isArabic => _locale.languageCode == 'ar';
  TextDirection get direction => isArabic ? TextDirection.rtl : TextDirection.ltr;

  void setLanguage(String code) {
    if (code != 'en' && code != 'ar') return;
    _locale = Locale(code);
    notifyListeners();
  }

  void toggle() => setLanguage(isArabic ? 'en' : 'ar');
}

class NovaStrings {
  static const Map<String, Map<String, String>> _values = {
    'en': {
      'brand': 'NOVA HOME', 'tagline': 'A better home. A happier you.', 'home': 'Home',
      'shop': 'Shop', 'cart': 'Cart', 'orders': 'Orders', 'account': 'Account',
      'search': 'Search appliances', 'featured': 'Featured products', 'offers': 'Special offers',
      'categories': 'Shop by category', 'add_cart': 'Add to cart', 'checkout': 'Checkout',
      'total': 'Total', 'continue': 'Continue', 'sign_in': 'Sign in', 'create_account': 'Create account',
      'email': 'Email address', 'password': 'Password', 'name': 'Full name', 'phone': 'Phone number',
      'address': 'Delivery address', 'city': 'City', 'payment': 'Payment', 'logout': 'Sign out',
      'empty_cart': 'Your cart is empty', 'empty_orders': 'Your orders will appear here',
      'language': 'العربية', 'no_data': 'No data available for this period',
      'dashboard': 'Dashboard', 'products': 'Products', 'customers': 'Customers', 'payments': 'Payments',
      'revenue': 'Paid revenue', 'total_orders': 'Total orders', 'new_customers': 'New customers',
      'active_products': 'Active products', 'week': 'Week', 'month': 'Month', 'year': 'Year', 'custom': 'Custom',
      'save': 'Save', 'cancel': 'Cancel', 'offers_manage': 'Offers', 'overview': 'Overview',
    },
    'ar': {
      'brand': 'نوفا هوم', 'tagline': 'منزل أفضل، حياة أسعد.', 'home': 'الرئيسية',
      'shop': 'تسوق', 'cart': 'السلة', 'orders': 'طلباتي', 'account': 'حسابي',
      'search': 'ابحث عن الأجهزة', 'featured': 'منتجات مميزة', 'offers': 'عروض خاصة',
      'categories': 'تسوق حسب الفئة', 'add_cart': 'أضف إلى السلة', 'checkout': 'إتمام الشراء',
      'total': 'الإجمالي', 'continue': 'متابعة', 'sign_in': 'تسجيل الدخول', 'create_account': 'إنشاء حساب',
      'email': 'البريد الإلكتروني', 'password': 'كلمة المرور', 'name': 'الاسم بالكامل', 'phone': 'رقم الهاتف',
      'address': 'عنوان التوصيل', 'city': 'المدينة', 'payment': 'الدفع', 'logout': 'تسجيل الخروج',
      'empty_cart': 'سلة التسوق فارغة', 'empty_orders': 'ستظهر طلباتك هنا',
      'language': 'English', 'no_data': 'لا توجد بيانات لهذه الفترة',
      'dashboard': 'لوحة التحكم', 'products': 'المنتجات', 'customers': 'العملاء', 'payments': 'المدفوعات',
      'revenue': 'الإيرادات المحصلة', 'total_orders': 'إجمالي الطلبات', 'new_customers': 'العملاء الجدد',
      'active_products': 'المنتجات النشطة', 'week': 'أسبوع', 'month': 'شهر', 'year': 'سنة', 'custom': 'فترة محددة',
      'save': 'حفظ', 'cancel': 'إلغاء', 'offers_manage': 'العروض', 'overview': 'نظرة عامة',
    },
  };

  static String t(Locale locale, String key) => _values[locale.languageCode]?[key] ?? _values['en']![key] ?? key;
}
