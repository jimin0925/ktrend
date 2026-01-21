import React from 'react';
import { motion } from 'framer-motion';

const TrendCard = ({ trend, onClick, isActive }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ x: 4 }}
            onClick={() => onClick(trend)}
            className={`cursor-pointer rounded-xl border p-4 transition-all duration-200 relative overflow-hidden ${isActive
                ? 'bg-indigo-950/30 border-indigo-500/50 ring-1 ring-indigo-500/20'
                : 'bg-neutral-900 border-neutral-800 hover:border-neutral-700 hover:shadow-sm hover:shadow-neutral-900/50'
                }`}
        >
            <div className="flex items-center gap-4">
                <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm font-bold ${trend.rank <= 3
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-900/50'
                    : 'bg-neutral-800 text-gray-400'
                    }`}>
                    {trend.rank}
                </span>

                <div className="flex-1 min-w-0">
                    <h3 className={`font-bold text-lg truncate ${isActive ? 'text-indigo-300' : 'text-gray-100'}`}>
                        {trend.keyword}
                    </h3>
                </div>

                {isActive && (
                    <motion.div
                        layoutId="active-indicator"
                        className="h-2 w-2 rounded-full bg-indigo-500 shrink-0 shadow-[0_0_10px_rgba(99,102,241,0.5)]"
                    />
                )}
            </div>
        </motion.div>
    );
};

export default TrendCard;
