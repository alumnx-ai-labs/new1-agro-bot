import React, { useState } from 'react';

const App = () => {
  const [testResult, setTestResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testCloudFunction = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://us-central1-agro-bot-1212.cloudfunctions.net/farmer-assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          inputType: 'text',
          content: 'Hello from React! This is a test message.',
          language: 'en'
        })
      });

      const result = await response.json();
      setTestResult(JSON.stringify(result, null, 2));
    } catch (error) {
      setTestResult('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-green-600 mb-2">
              🌱 Farmer Assistant MVP
            </h1>
            <p className="text-gray-600 text-lg">
              React Frontend + Cloud Function Backend
            </p>
          </div>

          <div className="text-center mb-8">
            <button
              onClick={testCloudFunction}
              disabled={loading}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-3 px-8 rounded-lg transition-colors duration-200"
            >
              {loading ? '🔄 Testing...' : '🧪 Test Cloud Function'}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors">
              🔬 Disease Detection
            </button>
            <button className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors">
              🏛️ Government Schemes
            </button>
            <button className="bg-orange-600 hover:bg-orange-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors">
              �� Talk Now
            </button>
            <button className="bg-cyan-600 hover:bg-cyan-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors">
              🌤️ Weather Stations
            </button>
          </div>

          {testResult && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h3 className="font-bold text-gray-800 mb-2">API Response:</h3>
              <pre className="text-sm text-gray-700 overflow-x-auto whitespace-pre-wrap">
                {testResult}
              </pre>
            </div>
          )}

          <div className="mt-8 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-700 font-semibold text-center">
              ✅ React app is running! Click "Test Cloud Function" to verify backend connection.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
