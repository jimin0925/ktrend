import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { TrendingUp, RefreshCw } from 'lucide-react';
import TrendCard from './components/TrendCard';
import TrendDetailModal from './components/TrendDetailModal';

function App() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTrend, setSelectedTrend] = useState(null);

  const fetchTrends = async () => {
    setLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.get(`${apiUrl}/api/trends`);
      setTrends(response.data.trends);
    } catch (error) {
      console.error("Failed to fetch trends", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md sticky top-0 z-10 border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg text-white">
              <TrendingUp size={24} />
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight">Trand <span className="text-indigo-600">Korea</span></h1>
          </div>
          <button
            onClick={fetchTrends}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            title="Refresh Trends"
          >
            <RefreshCw size={20} className={`${loading ? 'animate-spin' : ''} text-gray-600`} />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800">오늘의 대한민국 트렌드</h2>
          <p className="text-gray-500">실시간으로 가장 화제가 되고 있는 키워드와 그 이유를 알아보세요.</p>
        </div>

        {loading && trends.length === 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-24 bg-white rounded-xl shadow-sm border border-gray-200 animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {trends.map((trend) => (
              <TrendCard
                key={trend.rank}
                trend={trend}
                onClick={setSelectedTrend}
              />
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-8 text-center text-gray-400 text-sm">
        <p>&copy; 2024 Trand Korea. Powered by Naver DataLab & Google Trends.</p>
      </footer>

      {/* Modal */}
      {selectedTrend && (
        <TrendDetailModal
          isOpen={!!selectedTrend}
          trend={selectedTrend}
          onClose={() => setSelectedTrend(null)}
        />
      )}
    </div>
  );
}

export default App;
