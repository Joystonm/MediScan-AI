import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="page-header">
          <h1 className="page-title">
            AI-Powered Medical Diagnosis
            <br />
            <span className="text-secondary-600">Made Simple</span>
          </h1>
          <p className="page-subtitle">
            Advanced artificial intelligence meets healthcare to provide instant, accurate analysis 
            of skin lesions, chest X-rays, and virtual triage assessments. Trusted by healthcare 
            professionals worldwide.
          </p>
          <div className="flex gap-4 justify-center mt-8">
            <Link to="/dashboard" className="btn btn-primary btn-lg">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Get Started
            </Link>
            <Link to="/about" className="btn btn-outline btn-lg">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Learn More
            </Link>
          </div>
        </div>
      </section>


    </div>
  );
};

export default Home;
