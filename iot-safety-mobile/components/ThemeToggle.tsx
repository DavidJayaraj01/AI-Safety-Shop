import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useSettingsStore } from '../store/settingsStore';
import { Colors, Spacing, BorderRadius, FontSizes } from '../constants/theme';

export const ThemeToggle: React.FC = () => {
  const { settings, toggleTheme } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  const getThemeIcon = () => {
    switch (settings.theme) {
      case 'light':
        return '☀️';
      case 'dark':
        return '🌙';
      case 'auto':
        return '⚙️';
      default:
        return '☀️';
    }
  };

  const getThemeLabel = () => {
    switch (settings.theme) {
      case 'light':
        return 'Light Mode';
      case 'dark':
        return 'Dark Mode';
      case 'auto':
        return 'Auto Mode';
      default:
        return 'Light Mode';
    }
  };

  return (
    <TouchableOpacity
      style={[styles.container, { backgroundColor: colors.card }]}
      onPress={toggleTheme}
      activeOpacity={0.7}
    >
      <View style={styles.content}>
        <Text style={styles.icon}>{getThemeIcon()}</Text>
        <View style={styles.textContainer}>
          <Text style={[styles.label, { color: colors.text }]}>Theme</Text>
          <Text style={[styles.value, { color: colors.textSecondary }]}>
            {getThemeLabel()}
          </Text>
        </View>
      </View>
      <Text style={[styles.arrow, { color: colors.textSecondary }]}>›</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 28,
    marginRight: Spacing.md,
  },
  textContainer: {
    flex: 1,
  },
  label: {
    fontSize: FontSizes.md,
    fontWeight: '600',
    marginBottom: 4,
  },
  value: {
    fontSize: FontSizes.sm,
  },
  arrow: {
    fontSize: 24,
    fontWeight: '300',
  },
});
