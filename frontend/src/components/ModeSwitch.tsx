import { useModeStore } from '../context/ModeContext';
import { Factory, Store } from 'lucide-react';

export const ModeSwitch = () => {
  const { mode, setMode } = useModeStore();

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
        Operating Mode
      </h3>
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => setMode('heavy_industry')}
          className={`p-4 rounded-lg border-2 transition-all ${
            mode === 'heavy_industry'
              ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
          }`}
        >
          <Factory
            className={`w-8 h-8 mx-auto mb-2 ${
              mode === 'heavy_industry'
                ? 'text-primary-600'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          />
          <h4 className="font-semibold text-gray-900 dark:text-white">
            Heavy Industry
          </h4>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Gas detection, auto-shutdown
          </p>
        </button>

        <button
          onClick={() => setMode('shop_floor')}
          className={`p-4 rounded-lg border-2 transition-all ${
            mode === 'shop_floor'
              ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
          }`}
        >
          <Store
            className={`w-8 h-8 mx-auto mb-2 ${
              mode === 'shop_floor'
                ? 'text-primary-600'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          />
          <h4 className="font-semibold text-gray-900 dark:text-white">
            Shop Floor
          </h4>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            PPE detection, fall alerts
          </p>
        </button>
      </div>
    </div>
  );
};
