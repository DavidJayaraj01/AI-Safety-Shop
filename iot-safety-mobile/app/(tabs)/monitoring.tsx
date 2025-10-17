import React, { useEffect, useCallback, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { useCameraStore } from '../../store/cameraStore';
import { useSettingsStore } from '../../store/settingsStore';
import { CameraCard } from '../../components/CameraCard';
import { ViolationCard } from '../../components/ViolationCard';
import { AlertBanner } from '../../components/AlertBanner';
import { Colors, Spacing, FontSizes, REFRESH_INTERVAL } from '../../constants/theme';

export default function CVMonitoringScreen() {
  const {
    cameras,
    detections,
    loading,
    error,
    selectedSeverity,
    fetchCameras,
    fetchDetections,
    acknowledgeDetection,
    setSelectedSeverity,
    getFilteredDetections,
    clearError,
  } = useCameraStore();
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchCameras();
    fetchDetections();
    
    const interval = setInterval(() => {
      fetchCameras();
      fetchDetections();
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await Promise.all([fetchCameras(), fetchDetections()]);
    setRefreshing(false);
  }, []);

  const handleAcknowledge = async (detectionId: number) => {
    await acknowledgeDetection(detectionId);
  };

  const filteredDetections = getFilteredDetections();

  const severityFilters: Array<'all' | 'low' | 'medium' | 'high' | 'critical'> = [
    'all',
    'low',
    'medium',
    'high',
    'critical',
  ];

  if (loading && cameras.length === 0) {
    return (
      <View style={[styles.container, styles.centered, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
          Loading cameras...
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {error && <AlertBanner message={error} severity="warning" onDismiss={clearError} />}

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
          <Text style={[styles.title, { color: colors.text }]}>CV Monitoring</Text>
          <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
            {cameras.length} Active Cameras
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Cameras</Text>
          {cameras.map((camera) => (
            <CameraCard key={camera.id} camera={camera} />
          ))}
        </View>

        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>
            Recent Violations ({filteredDetections.length})
          </Text>

          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.filterScroll}
          >
            {severityFilters.map((severity) => (
              <TouchableOpacity
                key={severity}
                style={[
                  styles.filterChip,
                  {
                    backgroundColor:
                      selectedSeverity === severity ? colors.primary : colors.card,
                  },
                ]}
                onPress={() => setSelectedSeverity(severity)}
              >
                <Text
                  style={[
                    styles.filterText,
                    {
                      color: selectedSeverity === severity ? '#fff' : colors.text,
                    },
                  ]}
                >
                  {severity.charAt(0).toUpperCase() + severity.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          {filteredDetections.map((detection) => (
            <ViolationCard
              key={detection.id}
              detection={detection}
              onAcknowledge={() => handleAcknowledge(detection.id)}
            />
          ))}

          {filteredDetections.length === 0 && (
            <View style={styles.emptyState}>
              <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
                No violations found
              </Text>
            </View>
          )}
        </View>
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
  subtitle: {
    fontSize: FontSizes.md,
  },
  section: {
    marginBottom: Spacing.lg,
  },
  sectionTitle: {
    fontSize: FontSizes.lg,
    fontWeight: '600',
    marginBottom: Spacing.md,
  },
  filterScroll: {
    marginBottom: Spacing.md,
  },
  filterChip: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: 20,
    marginRight: Spacing.sm,
  },
  filterText: {
    fontSize: FontSizes.sm,
    fontWeight: '600',
  },
  emptyState: {
    padding: Spacing.xl,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: FontSizes.md,
  },
});
