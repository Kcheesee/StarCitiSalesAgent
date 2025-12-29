/**
 * Main App Component
 * StarCiti Sales Agent - AI Ship Consultant
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import ConversationPage from './pages/ConversationPage';
import ThankYouPage from './pages/ThankYouPage';
import './styles/index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/conversation" element={<ConversationPage />} />
        <Route path="/thank-you" element={<ThankYouPage />} />
      </Routes>
    </Router>
  );
}

export default App;
