import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { LanguageProvider } from './contexts/LanguageContext';
import ErrorBoundary from './components/common/ErrorBoundary';
import NavBar from './components/NavBar';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import About from './pages/About';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LanguageProvider>
          <Router>
            <div className="App min-h-screen bg-gray-50">
              <NavBar />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/about" element={<About />} />
                </Routes>
              </main>
            </div>
          </Router>
        </LanguageProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
