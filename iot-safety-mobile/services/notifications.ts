import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import { apiService } from './api';

// Configure how notifications are handled when the app is in the foreground
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

export async function registerForPushNotificationsAsync() {
  let token: string | undefined;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#3b82f6',
    });
  }

  if (Platform.OS !== 'web') {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for push notification!');
      return;
    }

    try {
      token = (await Notifications.getExpoPushTokenAsync()).data;
      console.log('Push token:', token);

      // Register token with backend
      if (token) {
        await apiService.registerDeviceToken(token);
      }
    } catch (error) {
      console.error('Error getting push token:', error);
    }
  } else {
    console.log('Must use physical device for Push Notifications');
  }

  return token;
}

export function setupNotificationHandlers() {
  // Handle notification received while app is in foreground
  Notifications.addNotificationReceivedListener((notification) => {
    console.log('Notification received:', notification);
  });

  // Handle notification response (when user taps on notification)
  Notifications.addNotificationResponseReceivedListener((response) => {
    console.log('Notification response:', response);
    
    // Handle deep linking based on notification data
    const data = response.notification.request.content.data;
    
    if (data.type === 'sensor_alert') {
      // Navigate to dashboard
      // You can use router.push('/') here if needed
    } else if (data.type === 'cv_violation') {
      // Navigate to monitoring screen
      // You can use router.push('/monitoring') here if needed
    }
  });
}

// Function to send a local notification (for testing)
export async function sendLocalNotification(title: string, body: string, data?: any) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title,
      body,
      data,
      sound: true,
    },
    trigger: null, // Send immediately
  });
}
