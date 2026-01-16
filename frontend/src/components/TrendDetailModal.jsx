import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ExternalLink, Newspaper } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TrendDetailModal = ({ isOpen, onClose, trend }) => {
    const [analysis, setAnalysis] = React.useState(null);
    const [chartData, setChartData] = React.useState([]);
    const [loading, setLoading] = React.useState(false);
    const [chartPeriod, setChartPeriod] = React.useState('1mo'); // '1mo' or '1yr'
    const [chartLoading, setChartLoading] = React.useState(false);

    // Initial Analysis Fetch
    React.useEffect(() => {
        if (isOpen && trend) {
            setLoading(true);
            setAnalysis(null);
            setChartData([]);
            setChartPeriod('1mo');

            // Fetch analysis from backend (includes initial 1mo data)
            fetch(`http://localhost:8000/api/analyze/${encodeURIComponent(trend.keyword)}`)
                .then(res => res.json())
                .then(data => {
                    setAnalysis(data);
                    setChartData(data.chart_data || []);
                    setLoading(false);
                })
                .catch(err => {
                    console.error("Failed to analyze:", err);
                    setLoading(false);
                });
        }
    }, [isOpen, trend]);

    // Fetch Chart Data when Period Changes (skip initial load as analyze returns 1mo)
    const handlePeriodChange = (period) => {
        if (period === chartPeriod) return;
        setChartPeriod(period);
        setChartLoading(true);

        fetch(`http://localhost:8000/api/trend-data/${encodeURIComponent(trend.keyword)}?period=${period}`)
            .then(res => res.json())
            .then(data => {
                setChartData(data.chart_data || []);
                setChartLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch trend data:", err);
                setChartLoading(false);
            });
    };

    if (!isOpen || !trend) return null;

    // Helper for X-Axis formatting
    const formatXAxis = (tickItem) => {
        if (!tickItem) return "";
        const parts = tickItem.split('-'); // YYYY-MM-DD
        if (chartPeriod === '1yr') {
            // Show YY.MM for 1 year view
            return `${parts[0].slice(2)}.${parts[1]}`;
        }
        // Show MM.DD for 1 month view
        return `${parts[1]}.${parts[2]}`;
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" onClick={onClose}>
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden relative max-h-[90vh] overflow-y-auto"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="bg-white p-6 pb-4 text-left border-b border-gray-100">
                        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
                            <X size={24} />
                        </button>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-indigo-600 font-bold text-sm">#{trend.rank} Trending</span>
                            {trend.source && <span className="text-gray-400 text-sm">• {trend.source}</span>}
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900">{trend.keyword}</h2>
                    </div>

                    {/* Content */}
                    <div className="p-6 pt-4 text-left space-y-6">
                        {/* 1. Analyzed Reason */}
                        <div>
                            <h3 className="text-xs uppercase tracking-wider text-gray-500 font-bold mb-3 flex items-center gap-2">
                                💡 AI 분석 결과
                            </h3>
                            <div className="bg-gray-50 p-4 rounded-xl border border-gray-100 min-h-[80px]">
                                {loading ? (
                                    <div className="flex items-center justify-center h-full py-4 text-gray-500 text-sm gap-2">
                                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-indigo-600"></div>
                                        분석 중...
                                    </div>
                                ) : (
                                    <p className="text-gray-800 leading-relaxed text-[15px] whitespace-pre-wrap">
                                        {analysis?.reason || trend.reason || "잠시만 기다려주세요, 분석 정보를 불러오는 중입니다."}
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* 2. Chart (New Feature) */}
                        {(!loading || chartData.length > 0) && (
                            <div>
                                <div className="flex items-center justify-between mb-3">
                                    <h3 className="text-xs uppercase tracking-wider text-gray-500 font-bold flex items-center gap-2">
                                        📊 검색량 추이
                                    </h3>
                                    <div className="flex gap-1 bg-gray-100 p-0.5 rounded-lg">
                                        <button
                                            onClick={() => handlePeriodChange('1mo')}
                                            className={`text-xs px-2 py-1 rounded-md font-medium transition-all ${chartPeriod === '1mo' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                                        >
                                            1개월
                                        </button>
                                        <button
                                            onClick={() => handlePeriodChange('1yr')}
                                            className={`text-xs px-2 py-1 rounded-md font-medium transition-all ${chartPeriod === '1yr' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                                        >
                                            1년
                                        </button>
                                    </div>
                                </div>

                                <div className="h-48 w-full bg-white rounded-xl border border-gray-100 p-2 relative">
                                    {chartLoading && (
                                        <div className="absolute inset-0 bg-white/60 backdrop-blur-[1px] z-10 flex items-center justify-center">
                                            <div className="animate-spin rounded-full h-5 w-5 border-2 border-indigo-600 border-t-transparent"></div>
                                        </div>
                                    )}

                                    {chartData.length > 0 ? (
                                        <ResponsiveContainer width="100%" height="100%">
                                            <LineChart data={chartData}>
                                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
                                                <XAxis
                                                    dataKey="date"
                                                    tick={{ fontSize: 10, fill: '#9CA3AF' }}
                                                    tickLine={false}
                                                    axisLine={false}
                                                    tickFormatter={formatXAxis}
                                                    minTickGap={30} // Prevent overlap
                                                />
                                                <YAxis hide domain={['auto', 'auto']} />
                                                <Tooltip
                                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                                    labelStyle={{ color: '#6B7280', fontSize: '12px', marginBottom: '4px' }}
                                                    itemStyle={{ color: '#4F46E5', fontSize: '14px', fontWeight: 'bold' }}
                                                    formatter={(value) => [value, '검색량']}
                                                    labelFormatter={(label) => label}
                                                />
                                                <Line
                                                    type="monotone"
                                                    dataKey="ratio"
                                                    stroke="#4F46E5"
                                                    strokeWidth={2}
                                                    dot={false}
                                                    activeDot={{ r: 4 }}
                                                    isAnimationActive={true}
                                                />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    ) : (
                                        <div className="flex items-center justify-center h-full text-sm text-gray-400">
                                            데이터가 없습니다.
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* 3. Media Links */}
                        <div>
                            <h3 className="text-xs uppercase tracking-wider text-gray-500 font-bold mb-3 flex items-center gap-2">
                                🔗 관련 링크
                            </h3>
                            <div className="flex gap-2">
                                <a href={`https://search.naver.com/search.naver?where=news&query=${trend.keyword}`} target="_blank" rel="noopener noreferrer"
                                    className="flex-1 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 border border-gray-100 transition-colors text-center text-sm font-medium text-gray-700">
                                    네이버 검색
                                </a>
                                <a href={`https://www.youtube.com/results?search_query=${trend.keyword}`} target="_blank" rel="noopener noreferrer"
                                    className="flex-1 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 border border-gray-100 transition-colors text-center text-sm font-medium text-gray-700">
                                    유튜브 검색
                                </a>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default TrendDetailModal;
