import React, { useEffect, useState } from 'react'
import axios from 'axios'
import TrendCard from './components/TrendCard'
import TrendDetailView from './components/TrendDetailView'

function App() {
  /* State for Mobile View Navigation */
  const [showMobileDetail, setShowMobileDetail] = useState(false)

  const fetchTrends = async (category) => {
    setLoading(true)
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.get(`${apiUrl}/api/trends?category=${category}`);

      const fetchedTrends = response.data.trends || [];
      setTrends(fetchedTrends);

      if (fetchedTrends.length > 0) {
        setSelectedTrend(fetchedTrends[0]);
        // Note: We do NOT set showMobileDetail(true) here, 
        // so mobile users see the list first data loads.
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

  const handleTrendClick = (trend) => {
    setSelectedTrend(trend);
    setShowMobileDetail(true);
  }

  useEffect(() => {
    fetchTrends(selectedCategory)
    setShowMobileDetail(false) // Reset to list view when changing category
  }, [selectedCategory])

  return (
    <div className="min-h-screen bg-neutral-950 text-white font-sans flex flex-col">
      {/* Top Navigation */}
      <header className={`bg-neutral-900 border-b border-neutral-800 z-10 shrink-0 ${showMobileDetail ? 'hidden md:block' : 'block'}`}>
        <div className="max-w-[1600px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-black tracking-tight text-white">
              K-TREND <span className="text-indigo-500">NOW</span>
            </h1>
          </div>

          <nav className="flex gap-1 bg-neutral-800 p-1 rounded-xl overflow-x-auto no-scrollbar max-w-[200px] md:max-w-none">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`whitespace-nowrap px-4 py-1.5 rounded-lg text-sm font-bold transition-all duration-200 ${selectedCategory === cat.id
                  ? 'bg-neutral-700 text-indigo-400 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-neutral-700/50'
                  }`}
              >
                {cat.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main Content - Split View */}
      <main className="flex-1 max-w-[1600px] mx-auto w-full p-4 md:p-6 grid grid-cols-1 md:grid-cols-12 gap-6 h-[calc(100vh-64px)] md:h-auto overflow-hidden md:overflow-visible">

        {/* Left Sidebar: Trend List */}
        <div className={`
            md:col-span-4 flex flex-col bg-neutral-900 rounded-2xl border border-neutral-800 shadow-sm h-full
            ${showMobileDetail ? 'hidden md:flex' : 'flex'}
        `}>
          <div className="p-4 border-b border-neutral-800 bg-neutral-900/50">
            <h2 className="text-sm font-bold text-gray-400 uppercase tracking-wider">
              {categories.find(c => c.id === selectedCategory)?.label} 트렌드 순위
            </h2>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
            {loading ? (
              <div className="flex justify-center py-20">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent"></div>
              </div>
            ) : trends.length > 0 ? (
              trends.map((trend) => (
                <TrendCard
                  key={trend.rank}
                  trend={trend}
                  isActive={selectedTrend?.keyword === trend.keyword}
                  onClick={handleTrendClick}
                />
              ))
            ) : (
              <div className="text-center py-20 text-gray-500">
                데이터를 불러올 수 없습니다.
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Detail View */}
        <div className={`
            md:col-span-8 h-full z-20
            ${showMobileDetail
            ? 'fixed inset-0 z-50 bg-neutral-950 flex flex-col md:static md:bg-transparent md:block md:z-auto md:inset-auto'
            : 'hidden md:block'}
        `}>
          <TrendDetailView
            key={selectedTrend?.keyword}
            trend={selectedTrend}
            onBack={() => setShowMobileDetail(false)}
          />
        </div>

      </main>
    </div>
  )
}

export default App
