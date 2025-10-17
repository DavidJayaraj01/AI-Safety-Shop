import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { BarChart, PieChart } from 'react-native-chart-kit';
import { useSettingsStore } from '../../store/settingsStore';
import { StatsCard } from '../../components/StatsCard';
import { AlertBanner } from '../../components/AlertBanner';
import { Colors, Spacing, FontSizes, BorderRadius } from '../../constants/theme';
import { apiService } from '../../services/api';
import { ReportResponse } from '../../types/api';

export default function ReportsScreen() {
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;
  const screenWidth = Dimensions.get('window').width;

  const [reportData, setReportData] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month'>('week');

  const fetchReportData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getReports(selectedPeriod);
      setReportData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch reports');
    } finally {
      setLoading(false);
    }
  }, [selectedPeriod]);

  useEffect(() => {
    fetchReportData();
  }, [selectedPeriod]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchReportData();
    setRefreshing(false);
  }, [fetchReportData]);

  const chartConfig = {
    backgroundColor: colors.card,
    backgroundGradientFrom: colors.card,
    backgroundGradientTo: colors.card,
    decimalPlaces: 0,
    color: (opacity = 1) => colors.primary,
    labelColor: (opacity = 1) => colors.textSecondary,
    style: {
      borderRadius: BorderRadius.lg,
    },
  };

  const getSeverityChartData = () => {
    if (!reportData) return [];
    const dist = reportData.severity_distribution;
    return [
      { name: 'Low', population: dist.low, color: colors.success, legendFontColor: colors.text },
      { name: 'Medium', population: dist.medium, color: colors.warning, legendFontColor: colors.text },
      { name: 'High', population: dist.high, color: colors.danger, legendFontColor: colors.text },
      { name: 'Critical', population: dist.critical, color: '#dc2626', legendFontColor: colors.text },
    ];
  };

  const getIncidentsChartData = () => {
    if (!reportData || !reportData.incidents_by_day) {
      return { labels: [], datasets: [{ data: [0] }] };
    }
    return {
      labels: reportData.incidents_by_day.map((item) => {
        const date = new Date(item.date);
        return `${date.getMonth() + 1}/${date.getDate()}`;
      }),
      datasets: [{ data: reportData.incidents_by_day.map((item) => item.count) }],
    };
  };

  if (loading && !reportData) {
    return (
      <View style={[styles.container, styles.centered, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
          Loading reports...
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {error && <AlertBanner message={error} severity="warning" onDismiss={() => setError(null)} />}

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.primary}
          />
        }
      >
        <View style={styles.header}>
          <Text style={[styles.title, { color: colors.text }]}>Reports & Analytics</Text>
        </View>

        {/* Period Selector */}
        <View style={styles.periodSelector}>
          {(['day', 'week', 'month'] as const).map((period) => (
            <TouchableOpacity
              key={period}
              style={[
                styles.periodButton,
                {
                  backgroundColor: selectedPeriod === period ? colors.primary : colors.card,
                },
              ]}
              onPress={() => setSelectedPeriod(period)}
            >
              <Text
                style={[
                  styles.periodText,
                  { color: selectedPeriod === period ? '#fff' : colors.text },
                ]}
              >
                {period.charAt(0).toUpperCase() + period.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {reportData && (
          <>
            {/* Stats Cards */}
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              style={styles.statsScroll}
            >
              <StatsCard
                title="Total Violations"
                value={reportData.stats.total_violations}
                color={colors.primary}
              />
              <StatsCard
                title="Critical Alerts"
                value={reportData.stats.critical_alerts}
                color={colors.danger}
              />
              <StatsCard
                title="Active Cameras"
                value={reportData.stats.active_cameras}
                color={colors.success}
              />
              <StatsCard
                title="Avg Response Time"
                value={`${reportData.stats.average_response_time}m`}
                color={colors.warning}
              />
            </ScrollView>

            {/* Severity Distribution */}
            <View style={[styles.chartCard, { backgroundColor: colors.card }]}>
              <Text style={[styles.chartTitle, { color: colors.text }]}>
                Severity Distribution
              </Text>
              <PieChart
                data={getSeverityChartData()}
                width={screenWidth - 64}
                height={220}
                chartConfig={chartConfig}
                accessor="population"
                backgroundColor="transparent"
                paddingLeft="15"
                absolute
              />
            </View>

            {/* Incidents by Day */}
            <View style={[styles.chartCard, { backgroundColor: colors.card }]}>
              <Text style={[styles.chartTitle, { color: colors.text }]}>Incidents by Day</Text>
              <BarChart
                data={getIncidentsChartData()}
                width={screenWidth - 64}
                height={220}
                chartConfig={chartConfig}
                style={styles.barChart}
                yAxisLabel=""
                yAxisSuffix=""
                fromZero
              />
            </View>
          </>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: Spacing.md,
    fontSize: FontSizes.md,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: Spacing.md,
  },
  header: {
    marginBottom: Spacing.lg,
  },
  title: {
    fontSize: FontSizes.xxl,
    fontWeight: '700',
  },
  periodSelector: {
    flexDirection: 'row',
    marginBottom: Spacing.lg,
    gap: Spacing.sm,
  },
  periodButton: {
    flex: 1,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
  },
  periodText: {
    fontSize: FontSizes.md,
    fontWeight: '600',
  },
  statsScroll: {
    marginBottom: Spacing.lg,
  },
  chartCard: {
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginBottom: Spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  chartTitle: {
    fontSize: FontSizes.lg,
    fontWeight: '600',
    marginBottom: Spacing.md,
  },
  barChart: {
    marginVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
  },
});
