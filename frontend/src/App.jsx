import React, { useEffect, useState } from 'react';
import axios from 'axios';
import TrendCard from './components/TrendCard';
import TrendDetailView from './components/TrendDetailView';

function App() {
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedTrend, setSelectedTrend] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState("all")

  const categories = [
    { id: "all", label: "통합" },
    { id: "Fashion", label: "패션" },
    { id: "Digital", label: "디지털" },
    { id: "Food", label: "식품" },
    { id: "Living", label: "생활" }
  ]

  const fetchTrends = async (category) => {
    setLoading(true)
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      // In a real scenario, you'd pass ?category=${category} to the backend.
      // For now, we fetch 'all' and filter client-side if needed, or backend handles it.
      // Since our scraper does separate calls, let's assume backend supports it or we filter mock data.
      // Current backend only supports 'all' cache mostly, but let's pass it.
      const response = await axios.get(`${apiUrl}/api/trends?category=${category}`);

      const fetchedTrends = response.data.trends || [];
      setTrends(fetchedTrends);

      // Auto-select first trend if detailed view is empty
      if (fetchedTrends.length > 0) {
        setSelectedTrend(fetchedTrends[0]);
      } else {
        setSelectedTrend(null);
      }
    } catch (error) {
      console.error("Failed to fetch trends", error)
      setTrends([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTrends(selectedCategory)
  }, [selectedCategory])

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans flex flex-col h-screen overflow-hidden">
      {/* Top Navigation */}
      <header className="bg-white border-b border-gray-200 z-10 shrink-0">
        <div className="max-w-[1600px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🇰🇷</span>
            <h1 className="text-xl font-black tracking-tight text-gray-900">
              K-TREND <span className="text-indigo-600">NOW</span>
            </h1>
          </div>

          <nav className="flex gap-1 bg-gray-100 p-1 rounded-xl">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-4 py-1.5 rounded-lg text-sm font-bold transition-all duration-200 ${selectedCategory === cat.id
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200/50'
                  }`}
              >
                {cat.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

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
  )
}
      </main >

  {/* Footer */ }
  < footer className = "mt-12 py-8 text-center text-gray-400 text-sm" >
    <p>&copy; 2024 Trand Korea. Powered by Naver DataLab & Google Trends.</p>
      </footer >

  {/* Modal */ }
{
  selectedTrend && (
    <TrendDetailModal
      isOpen={!!selectedTrend}
      trend={selectedTrend}
      onClose={() => setSelectedTrend(null)}
    />
  )
}
    </div >
  );
}

export default App;
