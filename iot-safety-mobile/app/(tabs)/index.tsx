import React, { useEffect, useCallback, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useSensorStore } from '../../store/sensorStore';
import { useSettingsStore } from '../../store/settingsStore';
import { SensorCard } from '../../components/SensorCard';
import { LiveChart } from '../../components/LiveChart';
import { AlertBanner } from '../../components/AlertBanner';
import { Colors, Spacing, FontSizes, REFRESH_INTERVAL } from '../../constants/theme';

export default function DashboardScreen() {
  const {
    sensorData,
    chartData,
    loading,
    error,
    lastUpdated,
    isOffline,
    fetchSensorData,
    clearError,
  } = useSensorStore();
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  const [refreshing, setRefreshing] = useState(false);

  // Auto-refresh every 15 seconds
  useEffect(() => {
    fetchSensorData();
    const interval = setInterval(() => {
      fetchSensorData();
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchSensorData();
    setRefreshing(false);
  }, []);

  const formatLastUpdated = () => {
    if (!lastUpdated) return 'Never';
    const now = new Date();
    const diff = now.getTime() - lastUpdated.getTime();
    const seconds = Math.floor(diff / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ago`;
  };

  if (loading && !sensorData) {
    return (
      <View style={[styles.container, styles.centered, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
          Loading sensor data...
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {isOffline && (
        <AlertBanner
          message="Offline: Unable to connect to server"
          severity="danger"
          onDismiss={clearError}
        />
      )}

      {error && !isOffline && (
        <AlertBanner message={error} severity="warning" onDismiss={clearError} />
      )}

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
          <Text style={[styles.title, { color: colors.text }]}>Sensor Dashboard</Text>
          <Text style={[styles.lastUpdated, { color: colors.textSecondary }]}>
            Last updated: {formatLastUpdated()}
          </Text>
        </View>

        {sensorData && (
          <>
            <View style={styles.section}>
              <Text style={[styles.sectionTitle, { color: colors.text }]}>Live Readings</Text>
              <SensorCard
                title="Temperature"
                data={sensorData.sensors.temperature}
                icon="🌡️"
              />
              <SensorCard
                title="Humidity"
                data={sensorData.sensors.humidity}
                icon="💧"
              />
              <SensorCard
                title="Gas (MQ-135)"
                data={sensorData.sensors.gas}
                icon="💨"
              />
              <SensorCard
                title="Distance (HC-SR04)"
                data={sensorData.sensors.ultrasonic}
                icon="📏"
              />
              <SensorCard
                title="RFID Scanner"
                data={sensorData.sensors.rfid}
                icon="🔖"
              />
            </View>

            {chartData.length > 0 && (
              <View style={styles.section}>
                <Text style={[styles.sectionTitle, { color: colors.text }]}>
                  Historical Data
                </Text>
                <LiveChart
                  title="Temperature Trend"
                  data={chartData.map((d) => d.temperature)}
                  labels={chartData.map((d) => new Date(d.timestamp).toLocaleTimeString().slice(0, 5))}
                  color={colors.danger}
                  unit="°C"
                />
                <LiveChart
                  title="Humidity Trend"
                  data={chartData.map((d) => d.humidity)}
                  labels={chartData.map((d) => new Date(d.timestamp).toLocaleTimeString().slice(0, 5))}
                  color={colors.info}
                  unit="%"
                />
                <LiveChart
                  title="Gas Level Trend"
                  data={chartData.map((d) => d.gas)}
                  labels={chartData.map((d) => new Date(d.timestamp).toLocaleTimeString().slice(0, 5))}
                  color={colors.warning}
                  unit="ppm"
                />
              </View>
            )}
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
    marginBottom: Spacing.xs,
  },
  lastUpdated: {
    fontSize: FontSizes.sm,
  },
  section: {
    marginBottom: Spacing.lg,
  },
  sectionTitle: {
    fontSize: FontSizes.lg,
    fontWeight: '600',
    marginBottom: Spacing.md,
  },
});
