import React from 'react';
import { 
  Search, 
  Layers, 
  Activity, 
  BarChart3, 
  Database,
  Stethoscope
} from 'lucide-react';

type ActiveSection = 'analyze' | 'batch' | 'health' | 'stats' | 'families';

interface NavigationProps {
  activeSection: ActiveSection;
  onSectionChange: (section: ActiveSection) => void;
}

const Navigation: React.FC<NavigationProps> = ({ activeSection, onSectionChange }) => {
  const navItems = [
    {
      id: 'analyze' as const,
      label: 'Single Analysis',
      icon: Search,
      description: 'Analyze individual images for deepfake detection',
      priority: 1
    },
    {
      id: 'batch' as const,
      label: 'Batch Analysis',
      icon: Layers,
      description: 'Process multiple images simultaneously',
      priority: 2
    },
    {
      id: 'health' as const,
      label: 'System Health',
      icon: Stethoscope,
      description: 'Check system status and component health',
      priority: 3
    },
    {
      id: 'stats' as const,
      label: 'Statistics',
      icon: BarChart3,
      description: 'View system and attribution statistics',
      priority: 4
    },
    {
      id: 'families' as const,
      label: 'Attribution Families',
      icon: Database,
      description: 'Explore deepfake generation families',
      priority: 5
    }
  ];

  return (
    <nav className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSection === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              className={`
                p-4 rounded-lg text-left transition-all duration-200 group
                ${isActive 
                  ? 'bg-primary-50 border-2 border-primary-200 text-primary-700' 
                  : 'hover:bg-gray-50 border-2 border-transparent text-gray-600 hover:text-gray-900'
                }
              `}
            >
              <div className="flex items-center space-x-3 mb-2">
                <Icon className={`w-5 h-5 ${isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-600'}`} />
                <span className="font-medium text-sm">{item.label}</span>
              </div>
              <p className="text-xs text-gray-500 leading-relaxed">
                {item.description}
              </p>
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default Navigation;