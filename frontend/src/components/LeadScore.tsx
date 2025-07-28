import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { getScoreColor, getScoreCategory } from '../services/leadScoring';

interface LeadScoreProps {
  score: number | null;
  confidence?: number;
  showDetails?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function LeadScore({ 
  score, 
  confidence, 
  showDetails = false, 
  size = 'md',
  className = '' 
}: LeadScoreProps) {
  if (score === null || score === undefined) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className="text-gray-400 text-sm">No score</div>
      </div>
    );
  }

  const scoreColor = getScoreColor(score);
  const category = getScoreCategory(score);
  
  // Size classes
  const sizeClasses = {
    sm: {
      container: 'text-xs',
      score: 'text-lg font-bold',
      category: 'text-xs',
      circle: 'w-8 h-8'
    },
    md: {
      container: 'text-sm',
      score: 'text-xl font-bold',
      category: 'text-sm',
      circle: 'w-12 h-12'
    },
    lg: {
      container: 'text-base',
      score: 'text-2xl font-bold',
      category: 'text-base',
      circle: 'w-16 h-16'
    }
  };

  const currentSize = sizeClasses[size];

  // Calculate circle progress
  const radius = size === 'sm' ? 14 : size === 'md' ? 20 : 28;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const strokeDasharray = `${progress} ${circumference}`;

  // Get trend indicator
  const getTrendIcon = () => {
    if (score >= 80) return <TrendingUp className="w-3 h-3 text-green-600" />;
    if (score >= 60) return <TrendingUp className="w-3 h-3 text-orange-600" />;
    if (score >= 40) return <Minus className="w-3 h-3 text-yellow-600" />;
    return <TrendingDown className="w-3 h-3 text-gray-600" />;
  };

  return (
    <div className={`flex items-center gap-3 ${currentSize.container} ${className}`}>
      {/* Score Circle */}
      <div className="relative">
        <svg className={currentSize.circle}>
          {/* Background circle */}
          <circle
            cx={radius + 2}
            cy={radius + 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx={radius + 2}
            cy={radius + 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            strokeDasharray={strokeDasharray}
            strokeLinecap="round"
            className={`${
              score >= 80 ? 'text-red-500' :
              score >= 60 ? 'text-orange-500' :
              score >= 40 ? 'text-yellow-500' : 'text-gray-400'
            }`}
            style={{ transform: 'rotate(-90deg)', transformOrigin: 'center' }}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`${currentSize.score} ${
            score >= 80 ? 'text-red-600' :
            score >= 60 ? 'text-orange-600' :
            score >= 40 ? 'text-yellow-600' : 'text-gray-600'
          }`}>
            {score}
          </span>
        </div>
      </div>

      {/* Score details */}
      <div className="flex flex-col">
        <div className="flex items-center gap-1">
          <span className={`font-semibold ${currentSize.category}`}>
            {category}
          </span>
          {getTrendIcon()}
        </div>
        
        {showDetails && confidence !== undefined && (
          <div className="text-gray-500 text-xs">
            Confidence: {Math.round(confidence * 100)}%
          </div>
        )}
      </div>

      {/* Score badge for compact view */}
      {!showDetails && (
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${scoreColor}`}>
          {score}
        </span>
      )}
    </div>
  );
} 