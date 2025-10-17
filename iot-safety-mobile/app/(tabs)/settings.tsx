import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TextInput,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useSettingsStore } from '../../store/settingsStore';
import { ThemeToggle } from '../../components/ThemeToggle';
import { AlertBanner } from '../../components/AlertBanner';
import { Colors, Spacing, FontSizes, BorderRadius } from '../../constants/theme';
import { clearAllStorage, debugStorage } from '../../utils/storage';

export default function SettingsScreen() {
  const { settings, loading, error, fetchSettings, updateSettings, resetSettings, clearError } =
    useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  const [tempThresholds, setTempThresholds] = useState(settings.thresholds.temperature);
  const [humidityThresholds, setHumidityThresholds] = useState(settings.thresholds.humidity);
  const [gasThreshold, setGasThreshold] = useState(settings.thresholds.gas);
  const [ultrasonicThreshold, setUltrasonicThreshold] = useState(settings.thresholds.ultrasonic);

  useEffect(() => {
    fetchSettings();
  }, []);

  useEffect(() => {
    setTempThresholds(settings.thresholds.temperature);
    setHumidityThresholds(settings.thresholds.humidity);
    setGasThreshold(settings.thresholds.gas);
    setUltrasonicThreshold(settings.thresholds.ultrasonic);
  }, [settings]);

  const handleToggleNotifications = async (value: boolean) => {
    await updateSettings({ notifications_enabled: value });
  };

  const handleSaveThresholds = async () => {
    try {
      await updateSettings({
        thresholds: {
          temperature: tempThresholds,
          humidity: humidityThresholds,
          gas: gasThreshold,
          ultrasonic: ultrasonicThreshold,
        },
      });
      Alert.alert('Success', 'Thresholds updated successfully');
    } catch (err) {
      Alert.alert('Error', 'Failed to update thresholds');
    }
  };

  const handleResetSettings = async () => {
    Alert.alert(
      'Reset Settings',
      'This will reset all settings to default values and clear the cache. Continue?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: async () => {
            try {
              await clearAllStorage();
              await resetSettings();
              Alert.alert('Success', 'Settings reset successfully. Please restart the app.');
            } catch (err) {
              Alert.alert('Error', 'Failed to reset settings');
            }
          },
        },
      ]
    );
  };

  const handleDebugStorage = async () => {
    await debugStorage();
    Alert.alert('Debug', 'Storage debug info logged to console');
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {error && <AlertBanner message={error} severity="warning" onDismiss={clearError} />}

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={[styles.title, { color: colors.text }]}>Settings</Text>
        </View>

        {/* Theme Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Appearance</Text>
          <ThemeToggle />
        </View>

        {/* Notifications Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Notifications</Text>
          <View style={[styles.settingRow, { backgroundColor: colors.card }]}>
            <View style={styles.settingInfo}>
              <Text style={[styles.settingLabel, { color: colors.text }]}>
                Push Notifications
              </Text>
              <Text style={[styles.settingDescription, { color: colors.textSecondary }]}>
                Receive alerts for critical events
              </Text>
            </View>
            <Switch
              value={Boolean(settings.notifications_enabled)}
              onValueChange={handleToggleNotifications}
              trackColor={{ false: colors.border, true: colors.primary }}
              thumbColor="#fff"
            />
          </View>
        </View>

        {/* Thresholds Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Sensor Thresholds</Text>

          {/* Temperature */}
          <View style={[styles.thresholdCard, { backgroundColor: colors.card }]}>
            <Text style={[styles.thresholdTitle, { color: colors.text }]}>Temperature (°C)</Text>
            <View style={styles.thresholdInputs}>
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: colors.textSecondary }]}>Min</Text>
                <TextInput
                  style={[styles.input, { backgroundColor: colors.background, color: colors.text }]}
                  value={tempThresholds.min.toString()}
                  onChangeText={(text) =>
                    setTempThresholds({ ...tempThresholds, min: Number(text) || 0 })
                  }
                  keyboardType="numeric"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: colors.textSecondary }]}>Max</Text>
                <TextInput
                  style={[styles.input, { backgroundColor: colors.background, color: colors.text }]}
                  value={tempThresholds.max.toString()}
                  onChangeText={(text) =>
                    setTempThresholds({ ...tempThresholds, max: Number(text) || 0 })
                  }
                  keyboardType="numeric"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>
            </View>
          </View>

          {/* Humidity */}
          <View style={[styles.thresholdCard, { backgroundColor: colors.card }]}>
            <Text style={[styles.thresholdTitle, { color: colors.text }]}>Humidity (%)</Text>
            <View style={styles.thresholdInputs}>
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: colors.textSecondary }]}>Min</Text>
                <TextInput
                  style={[styles.input, { backgroundColor: colors.background, color: colors.text }]}
                  value={humidityThresholds.min.toString()}
                  onChangeText={(text) =>
                    setHumidityThresholds({ ...humidityThresholds, min: Number(text) || 0 })
                  }
                  keyboardType="numeric"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: colors.textSecondary }]}>Max</Text>
                <TextInput
                  style={[styles.input, { backgroundColor: colors.background, color: colors.text }]}
                  value={humidityThresholds.max.toString()}
                  onChangeText={(text) =>
                    setHumidityThresholds({ ...humidityThresholds, max: Number(text) || 0 })
                  }
                  keyboardType="numeric"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>
            </View>
          </View>

          {/* Gas */}
          <View style={[styles.thresholdCard, { backgroundColor: colors.card }]}>
            <Text style={[styles.thresholdTitle, { color: colors.text }]}>Gas (ppm)</Text>
            <View style={styles.thresholdInputs}>
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: colors.textSecondary }]}>Max</Text>
                <TextInput
                  style={[styles.input, { backgroundColor: colors.background, color: colors.text }]}
                  value={gasThreshold.max.toString()}
                  onChangeText={(text) =>
                    setGasThreshold({ ...gasThreshold, max: Number(text) || 0 })
                  }
                  keyboardType="numeric"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>
            </View>
          </View>

          {/* Ultrasonic */}
          <View style={[styles.thresholdCard, { backgroundColor: colors.card }]}>
            <Text style={[styles.thresholdTitle, { color: colors.text }]}>Distance (cm)</Text>
            <View style={styles.thresholdInputs}>
              <View style={styles.inputGroup}>
                <Text style={[styles.inputLabel, { color: colors.textSecondary }]}>Min</Text>
                <TextInput
                  style={[styles.input, { backgroundColor: colors.background, color: colors.text }]}
                  value={ultrasonicThreshold.min.toString()}
                  onChangeText={(text) =>
                    setUltrasonicThreshold({ ...ultrasonicThreshold, min: Number(text) || 0 })
                  }
                  keyboardType="numeric"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>
            </View>
          </View>

          <TouchableOpacity
            style={[styles.saveButton, { backgroundColor: colors.primary }]}
            onPress={handleSaveThresholds}
            disabled={loading}
          >
            <Text style={styles.saveButtonText}>
              {loading ? 'Saving...' : 'Save Thresholds'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>About</Text>
          <View style={[styles.settingRow, { backgroundColor: colors.card }]}>
            <Text style={[styles.settingLabel, { color: colors.text }]}>Version</Text>
            <Text style={[styles.settingValue, { color: colors.textSecondary }]}>1.0.0</Text>
          </View>
          <View style={[styles.settingRow, { backgroundColor: colors.card }]}>
            <Text style={[styles.settingLabel, { color: colors.text }]}>Refresh Interval</Text>
            <Text style={[styles.settingValue, { color: colors.textSecondary }]}>
              {settings.refresh_interval / 1000}s
            </Text>
          </View>
        </View>

        {/* Debug & Reset Section */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Advanced</Text>
          
          <TouchableOpacity
            style={[styles.dangerButton, { backgroundColor: colors.card, borderColor: colors.danger }]}
            onPress={handleDebugStorage}
          >
            <Text style={[styles.dangerButtonText, { color: colors.text }]}>
              Debug Storage (Check Console)
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.dangerButton, { backgroundColor: colors.danger }]}
            onPress={handleResetSettings}
          >
            <Text style={[styles.dangerButtonText, { color: '#fff' }]}>
              Reset All Settings
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
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
  section: {
    marginBottom: Spacing.xl,
  },
  sectionTitle: {
    fontSize: FontSizes.lg,
    fontWeight: '600',
    marginBottom: Spacing.md,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.sm,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  settingInfo: {
    flex: 1,
  },
  settingLabel: {
    fontSize: FontSizes.md,
    fontWeight: '600',
  },
  settingDescription: {
    fontSize: FontSizes.sm,
    marginTop: 4,
  },
  settingValue: {
    fontSize: FontSizes.md,
  },
  thresholdCard: {
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  thresholdTitle: {
    fontSize: FontSizes.md,
    fontWeight: '600',
    marginBottom: Spacing.md,
  },
  thresholdInputs: {
    flexDirection: 'row',
    gap: Spacing.md,
  },
  inputGroup: {
    flex: 1,
  },
  inputLabel: {
    fontSize: FontSizes.sm,
    marginBottom: Spacing.xs,
  },
  input: {
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    fontSize: FontSizes.md,
  },
  saveButton: {
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    marginTop: Spacing.md,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: FontSizes.md,
    fontWeight: '600',
  },
  dangerButton: {
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    marginBottom: Spacing.sm,
    borderWidth: 1,
  },
  dangerButtonText: {
    fontSize: FontSizes.md,
    fontWeight: '600',
  },
});
