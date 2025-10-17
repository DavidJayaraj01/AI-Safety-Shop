import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Colors, Spacing, FontSizes } from '../constants/theme';
import { useSettingsStore } from '../store/settingsStore';

interface AlertBannerProps {
  message: string;
  severity: 'info' | 'warning' | 'danger';
  onDismiss?: () => void;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ message, severity, onDismiss }) => {
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  const getBannerColor = () => {
    switch (severity) {
      case 'info':
        return colors.info;
      case 'warning':
        return colors.warning;
      case 'danger':
        return colors.danger;
      default:
        return colors.info;
    }
  };

  return (
    <View style={[styles.banner, { backgroundColor: getBannerColor() }]}>
      <Text style={styles.message}>{message}</Text>
      {onDismiss && (
        <TouchableOpacity onPress={onDismiss} style={styles.dismissButton}>
          <Text style={styles.dismissText}>✕</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  banner: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: Spacing.md,
    marginBottom: Spacing.md,
  },
  message: {
    flex: 1,
    color: '#fff',
    fontSize: FontSizes.sm,
    fontWeight: '600',
  },
  dismissButton: {
    padding: Spacing.xs,
    marginLeft: Spacing.sm,
  },
  dismissText: {
    color: '#fff',
    fontSize: FontSizes.lg,
    fontWeight: '700',
  },
});
