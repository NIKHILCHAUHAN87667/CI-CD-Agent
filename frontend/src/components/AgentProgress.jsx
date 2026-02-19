import React from 'react';
import { AlertCircle, CheckCircle, Clock, Loader2 } from 'lucide-react';

const AgentProgress = ({ progress, currentStatus, isConnected }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'info':
      case 'cloning':
      case 'analyzing':
      case 'installing':
      case 'testing':
      case 'fixing':
      case 'pushing':
      case 'completing':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
      case 'cloning':
      case 'analyzing':
      case 'installing':
      case 'testing':
      case 'fixing':
      case 'pushing':
      case 'completing':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const formatTime = (timestamp) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return '';
    }
  };

  if (!progress || progress.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <div className="flex items-center justify-center text-gray-500">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          <span>Waiting for agent to start...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-3 flex items-center justify-between">
        <h3 className="text-white font-semibold flex items-center">
          <Loader2 className="h-5 w-5 mr-2 animate-spin" />
          Agent Live Progress
        </h3>
        <div className="flex items-center space-x-2">
          <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
          <span className="text-white text-sm">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Progress Log */}
      <div className="max-h-96 overflow-y-auto divide-y divide-gray-100">
        {progress.map((item, index) => (
          <div
            key={index}
            className={`px-4 py-3 transition-colors ${getStatusColor(item.status)}`}
          >
            <div className="flex items-start space-x-3">
              <div className="mt-0.5">{getStatusIcon(item.status)}</div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{item.message}</p>
                {item.data && (
                  <div className="mt-1 text-xs text-gray-600">
                    {Object.entries(item.data).map(([key, value]) => (
                      <div key={key} className="flex items-center space-x-1">
                        <span className="font-semibold">{key}:</span>
                        <span>{JSON.stringify(value)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <span className="text-xs text-gray-500 flex-shrink-0">
                {formatTime(item.timestamp)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Current Status Footer */}
      {currentStatus && (
        <div className="bg-gray-50 px-4 py-2 border-t border-gray-200">
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-semibold mr-2">Current State:</span>
            <span className="capitalize">{currentStatus.replace('_', ' ')}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentProgress;
