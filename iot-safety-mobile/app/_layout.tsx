import { Stack } from 'expo-router';
import React, { useEffect } from 'react';
import { useSettingsStore } from '../store/settingsStore';
import { Colors } from '../constants/theme';

export default function RootLayout() {
  const { settings, loadSettingsLocally } = useSettingsStore();
  const isDark = settings.theme === 'dark';
  const colors = isDark ? Colors.dark : Colors.light;

  useEffect(() => {
    // Load settings from local storage with error recovery
    const initializeSettings = async () => {
      try {
        await loadSettingsLocally();
      } catch (error) {
        console.error('Failed to load settings, resetting...', error);
        // Reset settings if loading fails
        const { resetSettings } = useSettingsStore.getState();
        await resetSettings();
      }
    };
    
    initializeSettings();

    // TODO: Setup push notifications
    // Uncomment when notifications are needed
    // const setupNotifications = async () => {
    //   try {
    //     const { registerForPushNotificationsAsync, setupNotificationHandlers } = 
    //       require('../services/notifications');
    //     await registerForPushNotificationsAsync();
    //     setupNotificationHandlers();
    //   } catch (error) {
    //     console.error('Failed to setup notifications:', error);
    //   }
    // };
    // setupNotifications();
  }, []);

  return (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: colors.card,
        },
        headerTintColor: colors.text,
        headerShadowVisible: false,
        contentStyle: {
          backgroundColor: colors.background,
        },
      }}
    >
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
    </Stack>
  );
}
