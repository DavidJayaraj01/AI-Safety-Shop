import React, { useMemo } from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { Colors, Spacing, BorderRadius, FontSizes } from '../constants/theme';
import { useSettingsStore } from '../store/settingsStore';

interface LiveChartProps {
  data: number[];
  labels: string[];
  title: string;
  color: string;
  unit: string;
}

export const LiveChart: React.FC<LiveChartProps> = ({ data, labels, title, color, unit }) => {
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;
  const screenWidth = Dimensions.get('window').width;

  const chartConfig = useMemo(() => ({
    backgroundColor: colors.card,
    backgroundGradientFrom: colors.card,
    backgroundGradientTo: colors.card,
    decimalPlaces: 1,
    color: (opacity = 1) => color,
    labelColor: (opacity = 1) => colors.textSecondary,
    style: {
      borderRadius: BorderRadius.lg,
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
      stroke: color,
    },
  }), [colors, color]);

  const chartData = {
    labels: labels.length > 6 ? labels.filter((_, i) => i % Math.ceil(labels.length / 6) === 0) : labels,
    datasets: [
      {
        data: data.length > 0 ? data : [0],
        color: (opacity = 1) => color,
        strokeWidth: 2,
      },
    ],
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.card }]}>
      <Text style={[styles.title, { color: colors.text }]}>{title}</Text>
      <LineChart
        data={chartData}
        width={screenWidth - 48}
        height={200}
        chartConfig={chartConfig}
        bezier
        style={styles.chart}
        withInnerLines={false}
        withOuterLines={true}
        withVerticalLabels={true}
        withHorizontalLabels={true}
        withVerticalLines={false}
        withHorizontalLines={true}
        withDots={true}
        withShadow={false}
      />
      <Text style={[styles.unit, { color: colors.textSecondary }]}>Unit: {unit}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginBottom: Spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: FontSizes.lg,
    fontWeight: '600',
    marginBottom: Spacing.md,
  },
  chart: {
    marginVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
  },
  unit: {
    fontSize: FontSizes.sm,
    marginTop: Spacing.xs,
  },
});
