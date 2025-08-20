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

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-neutral-800 mb-4">
            Comprehensive Medical AI Suite
          </h2>
          <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
            Three powerful AI modules working together to provide accurate, 
            fast, and reliable medical analysis and guidance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Skin Analysis Feature */}
          <div className="feature-card">
            <div className="feature-icon bg-primary-100 text-primary-600">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="feature-title">Skin Cancer Detection</h3>
            <p className="feature-description">
              Advanced ISIC-trained ResNet-50 model analyzes skin lesions for different 
              conditions including melanoma, basal cell carcinoma, and benign lesions with 
              high accuracy.
            </p>
            <Link to="/dashboard" className="btn btn-primary w-full">
              Analyze Skin Lesion
            </Link>
          </div>

          {/* Radiology Feature */}
          <div className="feature-card">
            <div className="feature-icon bg-secondary-100 text-secondary-600">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="feature-title">Radiology Analysis</h3>
            <p className="feature-description">
              CheXNet DenseNet-121 powered analysis of chest X-rays and CT scans, detecting 
              multiple pathologies including pneumonia, pneumothorax, and cardiomegaly.
            </p>
            <Link to="/dashboard" className="btn btn-secondary w-full">
              Upload X-ray/CT
            </Link>
          </div>

          {/* Triage Feature */}
          <div className="feature-card">
            <div className="feature-icon bg-info-100 text-info-600">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="feature-title">Virtual Triage Assistant</h3>
            <p className="feature-description">
              AI-powered symptom analysis using advanced language models and medical knowledge bases to provide 
              intelligent triage assessment and personalized medical guidance.
            </p>
            <Link to="/dashboard" className="btn btn-outline w-full">
              Start Triage Chat
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-neutral-800 mb-4">
            How It Works
          </h2>
          <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
            Get medical insights in three simple steps using our advanced AI technology
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
              1
            </div>
            <h3 className="text-xl font-semibold text-neutral-800 mb-3">Upload & Describe</h3>
            <p className="text-neutral-600">
              Upload your medical image or describe your symptoms using our secure, 
              HIPAA-compliant platform.
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-secondary-100 text-secondary-600 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
              2
            </div>
            <h3 className="text-xl font-semibold text-neutral-800 mb-3">AI Analysis</h3>
            <p className="text-neutral-600">
              Our advanced AI models analyze your data using state-of-the-art deep learning 
              algorithms trained on millions of medical cases.
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-info-100 text-info-600 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
              3
            </div>
            <h3 className="text-xl font-semibold text-neutral-800 mb-3">Get Results</h3>
            <p className="text-neutral-600">
              Receive detailed analysis results with visual overlays, confidence scores, 
              and personalized recommendations within seconds.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-primary-600 to-secondary-600 py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Experience AI-Powered Healthcare?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join thousands of healthcare professionals who trust MediScan-AI for 
            accurate, fast, and reliable medical analysis.
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/dashboard" className="btn bg-white text-primary-600 hover:bg-neutral-100 btn-lg">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Start Free Analysis
            </Link>
            <Link to="/about" className="btn btn-ghost text-white border-white hover:bg-white hover:text-primary-600 btn-lg">
              View Documentation
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
