import { Tabs } from 'expo-router';
import React from 'react';
import { Text, View } from 'react-native';
import { useSettingsStore } from '../../store/settingsStore';
import { Colors } from '../../constants/theme';

// Simple icon component
const TabIcon = ({ name }: { name: string }) => {
  const icons: Record<string, string> = {
    dashboard: '📊',
    camera: '📹',
    chart: '📈',
    settings: '⚙️',
  };

  return (
    <View style={{ justifyContent: 'center', alignItems: 'center' }}>
      <Text style={{ fontSize: 24 }}>{icons[name]}</Text>
    </View>
  );
};

export default function TabLayout() {
  const { settings } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: {
          backgroundColor: colors.card,
          borderTopColor: colors.border,
        },
        headerStyle: {
          backgroundColor: colors.card,
        },
        headerTintColor: colors.text,
        headerShadowVisible: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Dashboard',
          tabBarIcon: () => <TabIcon name="dashboard" />,
        }}
      />
      <Tabs.Screen
        name="monitoring"
        options={{
          title: 'CV Monitor',
          tabBarIcon: () => <TabIcon name="camera" />,
        }}
      />
      <Tabs.Screen
        name="reports"
        options={{
          title: 'Reports',
          tabBarIcon: () => <TabIcon name="chart" />,
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: 'Settings',
          tabBarIcon: () => <TabIcon name="settings" />,
        }}
      />
    </Tabs>
  );
}
