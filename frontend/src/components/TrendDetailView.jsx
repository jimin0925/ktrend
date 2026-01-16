import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, Newspaper, TrendingUp, Search } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TrendDetailView = ({ trend }) => {
    const [analysis, setAnalysis] = React.useState(null);
    const [chartData, setChartData] = React.useState([]);
    const [loading, setLoading] = React.useState(false);
    const [chartPeriod, setChartPeriod] = React.useState('1mo'); // '1mo' or '1yr'
    const [chartLoading, setChartLoading] = React.useState(false);

    // Initial Analysis Fetch
    React.useEffect(() => {
        if (trend) {
            setLoading(true);
            setAnalysis(null);
            setChartData([]);
            setChartPeriod('1mo');

            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            fetch(`${apiUrl}/api/analyze/${encodeURIComponent(trend.keyword)}`)
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
    }, [trend]);

    // Fetch Chart Data when Period Changes
    const handlePeriodChange = (period) => {
        if (period === chartPeriod || !trend) return;
        setChartPeriod(period);
        setChartLoading(true);

        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        fetch(`${apiUrl}/api/trend-data/${encodeURIComponent(trend.keyword)}?period=${period}`)
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

    // Helper for X-Axis formatting
    const formatXAxis = (tickItem) => {
        if (!tickItem) return "";
        const parts = tickItem.split('-'); // YYYY-MM-DD
        if (chartPeriod === '1yr') {
            return `${parts[0].slice(2)}.${parts[1]}`;
        }
        return `${parts[1]}.${parts[2]}`;
    };

    if (!trend) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 bg-neutral-900 rounded-2xl border border-neutral-800 p-8 shadow-sm">
                <Search size={48} className="mb-4 opacity-20" />
                <p className="text-lg font-medium text-gray-400">트렌드를 선택하여 상세 분석을 확인하세요</p>
                <p className="text-sm mt-2 opacity-40">왼쪽 목록에서 키워드를 클릭하면 분석이 시작됩니다.</p>
            </div>
        );
    }

    return (
        <div className="bg-neutral-900 rounded-2xl border border-neutral-800 shadow-xl h-full flex flex-col overflow-hidden">
            {/* Header */}
            <div className="p-8 pb-6 border-b border-neutral-800 bg-neutral-900">
                <div className="flex items-center gap-3 mb-2">
                    <span className="px-2.5 py-0.5 rounded-full bg-indigo-950/50 text-indigo-400 font-bold text-xs ring-1 ring-indigo-500/20">
                        #{trend.rank} Trending
                    </span>
                    {trend.source && (
                        <span className="text-gray-500 text-xs font-medium uppercase tracking-wide">
                            {trend.source}
                        </span>
                    )}
                </div>
                <h1 className="text-4xl font-black text-white tracking-tight">{trend.keyword}</h1>
            </div>

            {/* Content Scroll Area */}
            <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">

                {/* 1. Analyzed Reason */}
                <section>
                    <h3 className="text-sm uppercase tracking-wider text-gray-500 font-bold mb-4 flex items-center gap-2">
                        <TrendingUp size={16} />
                        AI 트렌드 분석
                    </h3>
                    <div className="bg-neutral-800/50 p-6 rounded-2xl border border-neutral-800 relative overflow-hidden group hover:border-neutral-700 transition-colors">
                        {loading ? (
                            <div className="flex flex-col items-center justify-center py-8 text-gray-500 gap-3">
                                <div className="animate-spin rounded-full h-6 w-6 border-2 border-neutral-600 border-t-indigo-500"></div>
                                <span className="text-sm font-medium animate-pulse">AI가 트렌드를 분석하고 있습니다...</span>
                            </div>
                        ) : (
                            <p className="text-gray-300 leading-8 text-[16px] font-medium whitespace-pre-wrap">
                                {analysis?.reason || trend.reason || "잠시만 기다려주세요..."}
                            </p>
                        )}
                    </div>
                </section>

                {/* 2. Chart */}
                <section>
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm uppercase tracking-wider text-gray-500 font-bold flex items-center gap-2">
                            📊 검색량 추이
                        </h3>
                        <div className="flex bg-neutral-800 p-1 rounded-xl">
                            {['1mo', '1yr'].map((p) => (
                                <button
                                    key={p}
                                    onClick={() => handlePeriodChange(p)}
                                    className={`text-xs px-4 py-1.5 rounded-lg font-bold transition-all duration-200 ${chartPeriod === p
                                        ? 'bg-neutral-700 text-indigo-400 shadow-sm'
                                        : 'text-gray-500 hover:text-gray-300 hover:bg-neutral-700/50'
                                        }`}
                                >
                                    {p === '1mo' ? '1개월' : '1년'}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="h-[320px] w-full bg-neutral-900 rounded-2xl border border-neutral-800 p-4 shadow-sm relative group hover:border-neutral-700 transition-colors">
                        {(loading || chartLoading) && chartData.length === 0 && (
                            <div className="absolute inset-0 bg-neutral-900/80 z-10 flex items-center justify-center rounded-2xl backdrop-blur-sm">
                                <div className="animate-spin rounded-full h-8 w-8 border-[3px] border-neutral-700 border-t-indigo-500"></div>
                            </div>
                        )}

                        {(!loading || chartData.length > 0) ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorRatio" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#262626" />
                                    <XAxis
                                        dataKey="date"
                                        tick={{ fontSize: 11, fill: '#6B7280', fontWeight: 500 }}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={formatXAxis}
                                        minTickGap={40}
                                        dy={10}
                                    />
                                    <YAxis hide domain={['auto', 'auto']} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#171717', borderRadius: '12px', border: '1px solid #262626', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.5)', padding: '12px' }}
                                        labelStyle={{ color: '#9CA3AF', fontSize: '12px', marginBottom: '8px', fontWeight: 600 }}
                                        itemStyle={{ color: '#818cf8', fontSize: '14px', fontWeight: 'bold' }}
                                        formatter={(value) => [value.toFixed(1), '검색량']}
                                        cursor={{ stroke: '#6366f1', strokeWidth: 1, strokeDasharray: '4 4' }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="ratio"
                                        stroke="#6366f1"
                                        strokeWidth={3}
                                        dot={false}
                                        activeDot={{ r: 6, strokeWidth: 0, fill: '#818cf8' }}
                                        fill="url(#colorRatio)"
                                        isAnimationActive={true}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-sm text-gray-600 font-medium bg-neutral-800/20 rounded-xl">
                                데이터가 없습니다
                            </div>
                        )}
                    </div>
                </section>

                {/* 3. External Links & Media */}
                <section>
                    <h3 className="text-sm uppercase tracking-wider text-gray-500 font-bold mb-4 flex items-center gap-2">
                        🔗 더보기
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                        <a
                            href={`https://search.naver.com/search.naver?where=news&query=${trend.keyword}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-center gap-3 p-4 rounded-xl bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 hover:border-neutral-600 transition-all group"
                        >
                            <span className="p-2 bg-green-900/30 rounded-lg text-green-400 group-hover:scale-110 transition-transform">
                                <Newspaper size={20} />
                            </span>
                            <span className="font-bold text-gray-300 group-hover:text-green-400">네이버 뉴스</span>
                        </a>
                        <a
                            href={`https://www.youtube.com/results?search_query=${trend.keyword}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-center gap-3 p-4 rounded-xl bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 hover:border-neutral-600 transition-all group"
                        >
                            <span className="p-2 bg-red-900/30 rounded-lg text-red-400 group-hover:scale-110 transition-transform">
                                <ExternalLink size={20} />
                            </span>
                            <span className="font-bold text-gray-300 group-hover:text-red-400">유튜브 영상</span>
                        </a>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default TrendDetailView;
