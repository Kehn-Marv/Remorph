import React from 'react';
import { LucideIcon } from 'lucide-react';

interface ResultCardProps {
  title: string;
  icon: LucideIcon;
  children: React.ReactNode;
  className?: string;
}

const ResultCard: React.FC<ResultCardProps> = ({ title, icon: Icon, children, className = '' }) => {
  return (
    <div className={`card ${className}`}>
      <div className="flex items-center space-x-3 mb-4">
        <Icon className="w-5 h-5 text-primary-600" />
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      {children}
    </div>
  );
};

export default ResultCard;