import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, Spacing, BorderRadius, FontSizes } from '../constants/theme';
import { useSettingsStore } from '../store/settingsStore';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: string;
  icon?: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({ title, value, subtitle, color }) => {
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;
  const accentColor = color || colors.primary;

  return (
    <View style={[styles.card, { backgroundColor: colors.card }]}>
      <Text style={[styles.title, { color: colors.textSecondary }]}>{title}</Text>
      <Text style={[styles.value, { color: accentColor }]}>{value}</Text>
      {subtitle && (
        <Text style={[styles.subtitle, { color: colors.textSecondary }]}>{subtitle}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    flex: 1,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginHorizontal: 6,
    marginBottom: Spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    minWidth: 150,
  },
  title: {
    fontSize: FontSizes.sm,
    marginBottom: Spacing.xs,
  },
  value: {
    fontSize: FontSizes.xxl,
    fontWeight: '700',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: FontSizes.xs,
  },
});
