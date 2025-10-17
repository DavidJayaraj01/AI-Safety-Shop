import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Detection } from '../types/api';
import { Colors, SeverityColors, Spacing, BorderRadius, FontSizes } from '../constants/theme';
import { useSettingsStore } from '../store/settingsStore';

interface ViolationCardProps {
  detection: Detection;
  onAcknowledge?: () => void;
}

export const ViolationCard: React.FC<ViolationCardProps> = ({ detection, onAcknowledge }) => {
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  const getSeverityColor = () => {
    return SeverityColors[detection.severity];
  };

  const formatDetectionType = (type: string) => {
    return type
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <View style={[styles.card, { backgroundColor: colors.card }]}>
      <View style={styles.header}>
        <View style={[styles.severityBadge, { backgroundColor: getSeverityColor() }]}>
          <Text style={styles.severityText}>{detection.severity.toUpperCase()}</Text>
        </View>
        <Text style={[styles.timestamp, { color: colors.textSecondary }]}>
          {formatTimestamp(detection.timestamp)}
        </Text>
      </View>

      <Text style={[styles.type, { color: colors.text }]}>
        {formatDetectionType(detection.detection_type)}
      </Text>

      <View style={styles.details}>
        <View style={styles.detailItem}>
          <Text style={[styles.detailLabel, { color: colors.textSecondary }]}>Camera</Text>
          <Text style={[styles.detailValue, { color: colors.text }]}>
            #{detection.camera_id}
          </Text>
        </View>
        <View style={styles.detailItem}>
          <Text style={[styles.detailLabel, { color: colors.textSecondary }]}>Confidence</Text>
          <Text style={[styles.detailValue, { color: colors.text }]}>
            {(detection.confidence * 100).toFixed(0)}%
          </Text>
        </View>
      </View>

      {!detection.acknowledged && onAcknowledge && (
        <TouchableOpacity
          style={[styles.button, { backgroundColor: colors.primary }]}
          onPress={onAcknowledge}
        >
          <Text style={styles.buttonText}>Acknowledge</Text>
        </TouchableOpacity>
      )}

      {detection.acknowledged && (
        <View style={[styles.acknowledgedBadge, { backgroundColor: colors.success }]}>
          <Text style={styles.acknowledgedText}>✓ Acknowledged</Text>
        </View>
      )}
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
  severityBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: BorderRadius.sm,
  },
  severityText: {
    color: '#fff',
    fontSize: FontSizes.xs,
    fontWeight: '700',
  },
  timestamp: {
    fontSize: FontSizes.xs,
  },
  type: {
    fontSize: FontSizes.lg,
    fontWeight: '600',
    marginBottom: Spacing.md,
  },
  details: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: Spacing.md,
  },
  detailItem: {
    flex: 1,
  },
  detailLabel: {
    fontSize: FontSizes.xs,
    marginBottom: 4,
  },
  detailValue: {
    fontSize: FontSizes.md,
    fontWeight: '600',
  },
  button: {
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: FontSizes.md,
    fontWeight: '600',
  },
  acknowledgedBadge: {
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
  },
  acknowledgedText: {
    color: '#fff',
    fontSize: FontSizes.sm,
    fontWeight: '600',
  },
});
