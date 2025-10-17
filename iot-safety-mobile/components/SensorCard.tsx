import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SensorData, RFIDData } from '../types/api';
import { Colors, StatusColors, Spacing, BorderRadius, FontSizes } from '../constants/theme';
import { useSettingsStore } from '../store/settingsStore';

interface SensorCardProps {
  title: string;
  data: SensorData | RFIDData;
  icon?: string;
}

export const SensorCard: React.FC<SensorCardProps> = ({ title, data, icon }) => {
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  const getStatusColor = () => {
    if ('status' in data) {
      return StatusColors[data.status as keyof typeof StatusColors];
    }
    return StatusColors.normal;
  };

  const getStatusText = () => {
    if ('status' in data) {
      return data.status.toUpperCase();
    }
    return 'NORMAL';
  };

  return (
    <View style={[styles.card, { backgroundColor: colors.card }]}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text }]}>{title}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor() }]}>
          <Text style={styles.statusText}>{getStatusText()}</Text>
        </View>
      </View>
      
      <View style={styles.content}>
        {'value' in data && typeof data.value === 'number' && 'unit' in data ? (
          <>
            <Text style={[styles.value, { color: colors.text }]}>
              {data.value.toFixed(1)}
            </Text>
            <Text style={[styles.unit, { color: colors.textSecondary }]}>
              {data.unit}
            </Text>
          </>
        ) : (
          <Text style={[styles.rfidValue, { color: colors.text }]}>
            {String(data.value)}
          </Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginBottom: Spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  title: {
    fontSize: FontSizes.md,
    fontWeight: '600',
  },
  statusBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: BorderRadius.sm,
  },
  statusText: {
    color: '#fff',
    fontSize: FontSizes.xs,
    fontWeight: '700',
  },
  content: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  value: {
    fontSize: FontSizes.xxl,
    fontWeight: '700',
  },
  unit: {
    fontSize: FontSizes.md,
    marginLeft: Spacing.xs,
  },
  rfidValue: {
    fontSize: FontSizes.lg,
    fontWeight: '600',
    fontFamily: 'monospace',
  },
});
