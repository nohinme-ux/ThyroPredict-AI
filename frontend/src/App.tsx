import React, { useState } from 'react';
import { AppLayout } from './layouts/AppLayout';
import { OverviewPage } from './pages/OverviewPage';
import { NewPredictionPage } from './pages/NewPredictionPage';
import { ParticipantsPage } from './pages/ParticipantsPage';
import { PredictionHistoryPage } from './pages/PredictionHistoryPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { DatasetInsightsPage } from './pages/DatasetInsightsPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');

  const renderActivePage = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewPage onNavigate={(tab) => setActiveTab(tab)} />;
      case 'new-prediction':
        return <NewPredictionPage onNavigate={(tab) => setActiveTab(tab)} />;
      case 'participants':
        return <ParticipantsPage onNavigate={(tab) => setActiveTab(tab)} />;
      case 'history':
        return <PredictionHistoryPage />;
      case 'performance':
        return <ModelPerformancePage />;
      case 'dataset':
        return <DatasetInsightsPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <OverviewPage onNavigate={(tab) => setActiveTab(tab)} />;
    }
  };

  return (
    <AppLayout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderActivePage()}
    </AppLayout>
  );
}

export default App;
