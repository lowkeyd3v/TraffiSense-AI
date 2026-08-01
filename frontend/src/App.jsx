import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/Landing/LandingPage';
import LoginPage from './pages/Login/LoginPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import AnalyticsPage from './pages/Analytics/AnalyticsPage';
import HistoryPage from './pages/History/HistoryPage';
import ReportIncidentPage from './pages/ReportIncident/ReportIncidentPage';
import PredictionPage from './pages/Prediction/PredictionPage';
import DeploymentPage from './pages/Deployment/DeploymentPage';
import SettingsPage from './pages/Settings/SettingsPage';
import ProfilePage from './pages/Profile/ProfilePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/report-incident" element={<ReportIncidentPage />} />
        <Route path="/prediction" element={<PredictionPage />} />
        <Route path="/deployment" element={<DeploymentPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;