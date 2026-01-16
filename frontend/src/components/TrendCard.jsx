import React from 'react';
import { motion } from 'framer-motion';

const TrendCard = ({ trend, onClick }) => {
    return (
        <motion.div
            whileHover={{ y: -5, boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)" }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onClick(trend)}
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 cursor-pointer relative overflow-hidden group transition-all"
        >
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                {/* Decorative elements or Category Icon could go here */}
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full blur-xl"></div>
            </div>

            <div className="flex items-center gap-4">
                <span className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-indigo-600 to-purple-600 font-mono">
                    {trend.rank}
                </span>
                <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                        <h3 className="text-xl font-bold text-gray-800 group-hover:text-indigo-700 transition-colors">
                            {trend.keyword}
                        </h3>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${trend.source === 'Naver Shopping' ? 'bg-green-100 text-green-700' :
                                trend.source === 'YouTube' ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                            }`}>
                            {trend.source}
                        </span>
                    </div>
                    <p className="text-xs text-gray-500 line-clamp-1">
                        {trend.reason ? trend.reason.substring(0, 30) + (trend.reason.length > 30 ? "..." : "") : "클릭하여 이유 확인하기"}
                    </p>
                </div>
            </div>
        </motion.div>
    );
};

export default TrendCard;
