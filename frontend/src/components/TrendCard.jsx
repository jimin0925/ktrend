import React from 'react';
import { motion } from 'framer-motion';

const TrendCard = ({ trend, onClick, isActive }) => {
    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ x: 4 }}
            onClick={() => onClick(trend)}
            className={`cursor-pointer rounded-xl border p-4 transition-all duration-200 relative overflow-hidden ${isActive
                    ? 'bg-indigo-50 border-indigo-200 ring-1 ring-indigo-500/20 shadow-md'
                    : 'bg-white border-gray-100 hover:border-gray-200 hover:shadow-sm'
                }`}
        >
            <div className="flex items-center gap-4">
                <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm font-bold ${trend.rank <= 3
                        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                        : 'bg-gray-100 text-gray-500'
                    }`}>
                    {trend.rank}
                </span>

                <div className="flex-1 min-w-0">
                    <h3 className={`font-bold text-lg truncate ${isActive ? 'text-indigo-900' : 'text-gray-800'}`}>
                        {trend.keyword}
                    </h3>
                </div>

                {isActive && (
                    <motion.div
                        layoutId="active-indicator"
                        className="h-2 w-2 rounded-full bg-indigo-500 shrink-0"
                    />
                )}
            </div>
        </motion.div>
    );
};

export default TrendCard;
