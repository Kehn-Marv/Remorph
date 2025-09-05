import React, { useState } from 'react';
import Header from './components/Header';
import Navigation from './components/Navigation';
import AnalyzeSection from './components/AnalyzeSection';
import BatchAnalyzeSection from './components/BatchAnalyzeSection';
import HealthSection from './components/HealthSection';
import StatsSection from './components/StatsSection';
import FamiliesSection from './components/FamiliesSection';

type ActiveSection = 'analyze' | 'batch' | 'health' | 'stats' | 'families';

function App() {
  const [activeSection, setActiveSection] = useState<ActiveSection>('analyze');

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'analyze':
        return <AnalyzeSection />;
      case 'batch':
        return <BatchAnalyzeSection />;
      case 'health':
        return <HealthSection />;
      case 'stats':
        return <StatsSection />;
      case 'families':
        return <FamiliesSection />;
      default:
        return <AnalyzeSection />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Navigation activeSection={activeSection} onSectionChange={setActiveSection} />
        <div className="mt-8">
          {renderActiveSection()}
        </div>
      </div>
    </div>
  );
}

export default App;