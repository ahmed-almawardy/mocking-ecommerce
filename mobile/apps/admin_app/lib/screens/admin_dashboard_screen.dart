import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:nova_core/nova_core.dart';

class AdminDashboardScreen extends StatefulWidget { const AdminDashboardScreen({super.key}); @override State<AdminDashboardScreen> createState() => _AdminDashboardScreenState(); }
class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  String period = 'week';
  DateTime start = DateTime.now().subtract(const Duration(days: 6));
  DateTime end = DateTime.now();
  Map<String, dynamic> data = {};
  bool loading = true;
  String? error;
  @override void initState() { super.initState(); _load(); }
  String _date(DateTime value) => DateFormat('yyyy-MM-dd').format(value);
  String get groupBy => period == 'year' ? 'month' : ((end.difference(start).inDays > 60) ? 'month' : 'day');
  Future<void> _load() async {
    setState(() { loading = true; error = null; });
    try {
      final raw = await context.read<NovaApiClient>().get('/admin/analytics', query: {'start': _date(start), 'end': _date(end), 'group_by': groupBy});
      if (mounted) setState(() { data = Map<String, dynamic>.from(raw as Map); loading = false; });
    } catch (e) { if (mounted) setState(() { error = '$e'; loading = false; }); }
  }
  Future<void> _setPeriod(String value) async {
    final today = DateTime.now();
    setState(() {
      period = value;
      end = DateTime(today.year, today.month, today.day);
      if (value == 'week') start = end.subtract(const Duration(days: 6));
      if (value == 'month') start = DateTime(today.year, today.month, 1);
      if (value == 'year') start = DateTime(today.year, 1, 1);
    });
    await _load();
  }
  Future<void> _customRange() async {
    final selected = await showDateRangePicker(context: context, firstDate: DateTime(2020), lastDate: DateTime.now(), initialDateRange: DateTimeRange(start: start, end: end));
    if (selected == null || !mounted) return;
    setState(() { period = 'custom'; start = selected.start; end = selected.end; });
    await _load();
  }

  @override Widget build(BuildContext context) {
    final summary = asMap(data['summary']);
    final revenue = asMapList(data['revenue_series']);
    final users = asMapList(data['user_series']);
    final payments = asMapList(data['payment_distribution']);
    final sellers = asMapList(data['top_selling_products']);
    final viewed = asMapList(data['most_viewed_products']);
    final carts = asMapList(data['most_added_to_cart']);
    return RefreshIndicator(onRefresh: _load, color: NovaColors.red, child: ListView(padding: const EdgeInsets.fromLTRB(16, 9, 16, 24), children: [
      Row(children: [Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [const NovaEyebrow('STORE PERFORMANCE'), Text('Dashboard', style: Theme.of(context).textTheme.headlineSmall), Text('Your business, at a glance.', style: Theme.of(context).textTheme.bodySmall)])), IconButton(onPressed: _load, icon: const Icon(Icons.refresh_rounded, color: NovaColors.red))]),
      const SizedBox(height: 15),
      Container(padding: const EdgeInsets.all(5), decoration: BoxDecoration(color: Colors.white, border: Border.all(color: NovaColors.border), borderRadius: BorderRadius.circular(14)), child: Row(children: [for (final value in ['week','month','year','custom']) Expanded(child: InkWell(onTap: value == 'custom' ? _customRange : () => _setPeriod(value), borderRadius: BorderRadius.circular(10), child: Container(padding: const EdgeInsets.symmetric(vertical: 10), decoration: BoxDecoration(color: period == value ? NovaColors.red : Colors.transparent, borderRadius: BorderRadius.circular(10)), alignment: Alignment.center, child: Text(value == 'week' ? 'Week' : value == 'month' ? 'Month' : value == 'year' ? 'Year' : 'Custom', style: TextStyle(color: period == value ? Colors.white : NovaColors.charcoal, fontWeight: FontWeight.w900, fontSize: 11)))))])),
      const SizedBox(height: 9),
      Row(children: [Expanded(child: Text('${DateFormat('d MMM yyyy').format(start)}  –  ${DateFormat('d MMM yyyy').format(end)}', style: const TextStyle(color: NovaColors.muted, fontSize: 11, fontWeight: FontWeight.w700))), TextButton.icon(onPressed: _customRange, icon: const Icon(Icons.calendar_month_outlined, size: 16), label: const Text('Dates', style: TextStyle(fontSize: 11)))]),
      if (loading) const Padding(padding: EdgeInsets.all(35), child: NovaLoading(label: 'Loading business analytics…'))
      else if (error != null) NovaErrorState(message: error!, onRetry: _load)
      else ...[
        GridView.count(crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), childAspectRatio: 1.52, crossAxisSpacing: 10, mainAxisSpacing: 10, children: [
          _KpiCard(title: 'Paid revenue', value: _money(summary['revenue']), detail: '${asInt(summary['paid_orders'])} paid orders', icon: Icons.account_balance_wallet_outlined),
          _KpiCard(title: 'Total orders', value: '${asInt(summary['orders'])}', detail: '${asInt(summary['pending_payments'])} awaiting payment', icon: Icons.shopping_bag_outlined),
          _KpiCard(title: 'New customers', value: '${asInt(summary['new_customers'])}', detail: '${asInt(summary['total_customers'])} registered total', icon: Icons.people_alt_outlined),
          _KpiCard(title: 'Active products', value: '${asInt(summary['active_products'])}', detail: '${asInt(summary['low_stock_products'])} low stock', icon: Icons.inventory_2_outlined),
        ]),
        const SizedBox(height: 13),
        _ChartCard(title: 'Sales overview', subtitle: 'Paid revenue · EGP', kind: _ChartKind.line, rows: revenue.map((e) => {'label': _label(e['date']), 'value': asDouble(e['revenue'])}).toList(), valueLabel: 'EGP', csvName: 'nova-sales-${_date(start)}'),
        const SizedBox(height: 12),
        _ChartCard(title: 'Customer registrations', subtitle: 'New customer accounts', kind: _ChartKind.bar, rows: users.map((e) => {'label': _label(e['date']), 'value': asDouble(e['users'])}).toList(), csvName: 'nova-customers-${_date(start)}'),
        const SizedBox(height: 12),
        _ChartCard(title: 'Payment statistics', subtitle: 'Transactions grouped by status', kind: _ChartKind.pie, rows: payments.map((e) => {'label': '${e['status']}', 'value': asDouble(e['count'])}).toList(), csvName: 'nova-payments-${_date(start)}'),
        const SizedBox(height: 12),
        _ChartCard(title: 'Most-selling products', subtitle: 'Units in paid orders', kind: _ChartKind.bar, rows: sellers.map((e) => {'label': '${e['name']}', 'value': asDouble(e['units_sold'])}).toList(), csvName: 'nova-best-sellers-${_date(start)}'),
        const SizedBox(height: 12),
        _ChartCard(title: 'Most-viewed products', subtitle: 'Product detail views', kind: _ChartKind.bar, rows: viewed.map((e) => {'label': '${e['name']}', 'value': asDouble(e['views'])}).toList(), csvName: 'nova-most-viewed-${_date(start)}'),
        const SizedBox(height: 12),
        _ChartCard(title: 'Most added to cart', subtitle: 'Units added to customer carts', kind: _ChartKind.bar, rows: carts.map((e) => {'label': '${e['name']}', 'value': asDouble(e['quantity'])}).toList(), csvName: 'nova-most-carted-${_date(start)}'),
        const SizedBox(height: 16),
        _recentOrders(asMapList(data['recent_orders'])),
        const SizedBox(height: 10),
        const Text('Reports use persisted orders, payment states, customer registrations and product events. Product views and cart activity accumulate from app/storefront tracking.', style: TextStyle(color: NovaColors.muted, fontSize: 10, height: 1.4)),
      ],
    ]));
  }
  String _money(dynamic value) => 'EGP ${NumberFormat('#,##0.00').format(asDouble(value))}';
  String _label(dynamic value) { final date = DateTime.tryParse('${value ?? ''}'); return date == null ? '$value' : DateFormat('d MMM').format(date); }
  Widget _recentOrders(List<Map<String, dynamic>> rows) => Container(padding: const EdgeInsets.all(14), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(17), border: Border.all(color: NovaColors.border)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [const Text('Recent orders', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 15)), const SizedBox(height: 5), const Text('Latest orders in the selected period', style: TextStyle(color: NovaColors.muted, fontSize: 10)), const SizedBox(height: 11), if (rows.isEmpty) const Text('No orders for this period.', style: TextStyle(color: NovaColors.muted, fontSize: 12)) else ...rows.map((row) => Padding(padding: const EdgeInsets.symmetric(vertical: 8), child: Row(children: [Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('${row['order_number']}', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 11)), Text('${row['customer_name']}', style: const TextStyle(color: NovaColors.muted, fontSize: 10))])), Text(_money(row['total']), style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 11)), const SizedBox(width: 9), NovaStatusPill('${row['payment_status']}')])))]));
}

class _KpiCard extends StatelessWidget {
  const _KpiCard({required this.title, required this.value, required this.detail, required this.icon});
  final String title, value, detail; final IconData icon;
  @override Widget build(BuildContext context) => Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: NovaColors.border)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Container(width: 33, height: 33, decoration: BoxDecoration(color: NovaColors.red.withOpacity(.09), borderRadius: BorderRadius.circular(10)), child: Icon(icon, color: NovaColors.red, size: 18)), Text(value, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: NovaColors.charcoal, fontSize: 17, fontWeight: FontWeight.w900)), Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900)), Text(detail, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 9, color: NovaColors.muted))]) ]));
}

enum _ChartKind { line, bar, pie }
class _ChartCard extends StatefulWidget {
  const _ChartCard({required this.title, required this.subtitle, required this.kind, required this.rows, required this.csvName, this.valueLabel = ''});
  final String title, subtitle, csvName, valueLabel; final _ChartKind kind; final List<Map<String, dynamic>> rows;
  @override State<_ChartCard> createState() => _ChartCardState();
}
class _ChartCardState extends State<_ChartCard> {
  final GlobalKey _chartKey = GlobalKey();
  int? _touchedPieIndex;
  static const chartColors = [NovaColors.red, NovaColors.charcoal, Color(0xFF7A8794), Color(0xFFB9C0C7), Color(0xFFEB777B)];
  Future<void> _shareCsv() => NovaChartExport.shareCsv(widget.csvName, [['Label', 'Value'], ...widget.rows.map((row) => [row['label'], row['value']])]);
  @override Widget build(BuildContext context) => Container(padding: const EdgeInsets.fromLTRB(14, 13, 14, 12), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(17), border: Border.all(color: NovaColors.border)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
    Row(children: [Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(widget.title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w900)), const SizedBox(height: 3), Text(widget.subtitle, style: const TextStyle(fontSize: 10, color: NovaColors.muted))])), PopupMenuButton<String>(icon: const Icon(Icons.download_rounded, size: 20, color: NovaColors.charcoal), onSelected: (v) { if (v == 'csv') _shareCsv(); if (v == 'png') NovaChartExport.sharePng(_chartKey, widget.csvName); }, itemBuilder: (_) => const [PopupMenuItem(value: 'png', child: Text('Share chart as PNG')), PopupMenuItem(value: 'csv', child: Text('Export data as CSV'))])]),
    const SizedBox(height: 13),
    RepaintBoundary(key: _chartKey, child: SizedBox(height: 206, width: double.infinity, child: widget.rows.isEmpty ? const Center(child: Text('No data available for this period.', style: TextStyle(color: NovaColors.muted, fontSize: 11))) : _buildChart())),
  ]));
  Widget _buildChart() {
    if (widget.kind == _ChartKind.line) {
      final spots = [for (var i = 0; i < widget.rows.length; i++) FlSpot(i.toDouble(), asDouble(widget.rows[i]['value']))];
      final maxY = spots.fold<double>(1, (m, e) => e.y > m ? e.y : m);
      return LineChart(LineChartData(minY: 0, maxY: maxY * 1.22, gridData: const FlGridData(show: true, drawVerticalLine: false), borderData: FlBorderData(show: false), titlesData: _titles(), lineTouchData: LineTouchData(touchTooltipData: LineTouchTooltipData(getTooltipItems: (items) => items.map((spot) => LineTooltipItem('${widget.valueLabel} ${NumberFormat.compact().format(spot.y)}', const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 10))).toList())), lineBarsData: [LineChartBarData(spots: spots, isCurved: true, color: NovaColors.red, barWidth: 3, dotData: const FlDotData(show: true), belowBarData: BarAreaData(show: true, color: NovaColors.red.withOpacity(.08))) ]));
    }
    if (widget.kind == _ChartKind.pie) {
      final sections = [for (var i = 0; i < widget.rows.length; i++) PieChartSectionData(value: asDouble(widget.rows[i]['value']), color: chartColors[i % chartColors.length], title: '${widget.rows[i]['label']}\n${widget.rows[i]['value']}', radius: _touchedPieIndex == i ? 72 : 62, titleStyle: const TextStyle(fontSize: 8, color: Colors.white, fontWeight: FontWeight.w900))];
      return PieChart(PieChartData(sections: sections, centerSpaceRadius: 36, sectionsSpace: 3, pieTouchData: PieTouchData(touchCallback: (event, response) {
        final nextIndex = response?.touchedSection?.touchedSectionIndex;
        if (nextIndex != _touchedPieIndex) setState(() => _touchedPieIndex = nextIndex);
      })));
    }
    final bars = [for (var i = 0; i < widget.rows.length; i++) BarChartGroupData(x: i, barRods: [BarChartRodData(toY: asDouble(widget.rows[i]['value']), color: NovaColors.red, width: 18, borderRadius: BorderRadius.circular(5))])];
    final maxY = widget.rows.fold<double>(1, (m, e) => asDouble(e['value']) > m ? asDouble(e['value']) : m);
    return BarChart(BarChartData(maxY: maxY * 1.25, minY: 0, gridData: const FlGridData(show: true, drawVerticalLine: false), borderData: FlBorderData(show: false), barGroups: bars, titlesData: _titles(), barTouchData: BarTouchData(enabled: true, touchTooltipData: BarTouchTooltipData(getTooltipItem: (group, groupIndex, rod, rodIndex) => BarTooltipItem('${widget.rows[group.x]['label']}\n${NumberFormat.compact().format(rod.toY)}', const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 9))))));
  }
  FlTitlesData _titles() => FlTitlesData(leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 36, getTitlesWidget: _leftTitle)), topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 36, interval: widget.rows.length > 7 ? (widget.rows.length / 5).ceilToDouble() : 1, getTitlesWidget: (value, meta) { final i = value.toInt(); if (i < 0 || i >= widget.rows.length) return const SizedBox.shrink(); final label = '${widget.rows[i]['label']}'; return SideTitleWidget(axisSide: meta.axisSide, child: Text(label.length > 7 ? label.substring(0, 7) : label, style: const TextStyle(fontSize: 8, color: NovaColors.muted))); })));
  static Widget _leftTitle(double value, TitleMeta meta) => SideTitleWidget(axisSide: meta.axisSide, child: Text(NumberFormat.compact().format(value), style: const TextStyle(fontSize: 8, color: NovaColors.muted)));
}
