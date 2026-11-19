import 'package:flutter_test/flutter_test.dart';
import 'package:nova_core/nova_core.dart';

void main() {
  test('analytics numeric values are parsed safely from API strings', () {
    expect(asDouble('2345.75'), 2345.75);
    expect(asInt('18'), 18);
    expect(asMap({'total': '10'})['total'], '10');
  });
}
