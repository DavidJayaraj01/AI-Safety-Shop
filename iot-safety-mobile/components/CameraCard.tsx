import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Camera } from '../types/api';
import { Colors, StatusColors, Spacing, BorderRadius, FontSizes } from '../constants/theme';
import { useSettingsStore } from '../store/settingsStore';

interface CameraCardProps {
  camera: Camera;
  onPress?: () => void;
}

export const CameraCard: React.FC<CameraCardProps> = ({ camera, onPress }) => {
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  const getStatusColor = () => {
    return StatusColors[camera.status];
  };

  return (
    <TouchableOpacity
      style={[styles.card, { backgroundColor: colors.card }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Text style={[styles.name, { color: colors.text }]}>{camera.name}</Text>
          <Text style={[styles.location, { color: colors.textSecondary }]}>
            {camera.location}
          </Text>
        </View>
        <View style={[styles.statusIndicator, { backgroundColor: getStatusColor() }]} />
      </View>

      <View style={styles.footer}>
        <View style={styles.violationContainer}>
          <Text style={[styles.violationCount, { color: colors.text }]}>
            {camera.violation_count}
          </Text>
          <Text style={[styles.violationLabel, { color: colors.textSecondary }]}>
            Violations
          </Text>
        </View>
        <Text style={[styles.status, { color: colors.textSecondary }]}>
          {camera.status.toUpperCase()}
        </Text>
      </View>
    </TouchableOpacity>
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
    alignItems: 'flex-start',
    marginBottom: Spacing.md,
  },
  titleContainer: {
    flex: 1,
  },
  name: {
    fontSize: FontSizes.lg,
    fontWeight: '600',
    marginBottom: 4,
  },
  location: {
    fontSize: FontSizes.sm,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginLeft: Spacing.sm,
    marginTop: 4,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  violationContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  violationCount: {
    fontSize: FontSizes.xl,
    fontWeight: '700',
  },
  violationLabel: {
    fontSize: FontSizes.sm,
    marginLeft: Spacing.xs,
  },
  status: {
    fontSize: FontSizes.xs,
    fontWeight: '600',
  },
});
