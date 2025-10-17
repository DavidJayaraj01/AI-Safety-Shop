import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Clear all AsyncStorage data
 * Use this if you encounter persistent type casting errors
 */
export const clearAllStorage = async (): Promise<void> => {
  try {
    await AsyncStorage.clear();
    console.log('AsyncStorage cleared successfully');
  } catch (error) {
    console.error('Failed to clear AsyncStorage:', error);
  }
};

/**
 * Get all keys stored in AsyncStorage
 */
export const getAllKeys = async (): Promise<readonly string[]> => {
  try {
    const keys = await AsyncStorage.getAllKeys();
    console.log('AsyncStorage keys:', keys);
    return keys;
  } catch (error) {
    console.error('Failed to get AsyncStorage keys:', error);
    return [];
  }
};

/**
 * Debug function to log all stored data
 */
export const debugStorage = async (): Promise<void> => {
  try {
    const keys = await AsyncStorage.getAllKeys();
    const items = await AsyncStorage.multiGet(keys);
    
    console.log('=== AsyncStorage Debug ===');
    items.forEach(([key, value]) => {
      console.log(`${key}:`, value);
      if (value) {
        try {
          const parsed = JSON.parse(value);
          console.log(`${key} (parsed):`, parsed);
        } catch {
          console.log(`${key} is not JSON`);
        }
      }
    });
    console.log('=========================');
  } catch (error) {
    console.error('Failed to debug AsyncStorage:', error);
  }
};

/**
 * Safely get an item from AsyncStorage with type validation
 */
export const safeGetItem = async <T>(
  key: string,
  validator?: (data: unknown) => data is T
): Promise<T | null> => {
  try {
    const value = await AsyncStorage.getItem(key);
    if (!value) return null;
    
    const parsed = JSON.parse(value);
    
    if (validator && !validator(parsed)) {
      console.warn(`Invalid data type for key: ${key}`);
      await AsyncStorage.removeItem(key);
      return null;
    }
    
    return parsed as T;
  } catch (error) {
    console.error(`Failed to get item ${key}:`, error);
    return null;
  }
};

/**
 * Type guard for Settings
 */
export const isSettings = (data: unknown): data is {
  theme: string;
  notifications_enabled: boolean;
  refresh_interval: number;
} => {
  if (typeof data !== 'object' || data === null) return false;
  
  const obj = data as Record<string, unknown>;
  
  return (
    typeof obj.theme === 'string' &&
    typeof obj.notifications_enabled === 'boolean' &&
    typeof obj.refresh_interval === 'number'
  );
};
