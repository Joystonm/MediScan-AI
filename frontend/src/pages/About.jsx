import React from 'react';

const About = () => {
  const features = [
    {
      title: 'Advanced AI Models',
      description: 'State-of-the-art deep learning models trained on millions of medical images',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      )
    },
    {
      title: 'Medical Grade Accuracy',
      description: '95%+ accuracy validated by healthcare professionals and medical institutions',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    },
    {
      title: 'HIPAA Compliant',
      description: 'Enterprise-grade security and privacy protection for all medical data',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      )
    },
    {
      title: 'Real-time Analysis',
      description: 'Get instant results with our optimized AI inference pipeline',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      )
    },
    {
      title: 'Multi-language Support',
      description: 'Available in 10+ languages with medical terminology translation',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
        </svg>
      )
    },
    {
      title: '24/7 Availability',
      description: 'Access medical AI assistance anytime, anywhere with cloud infrastructure',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    }
  ];

  const models = [
    {
      name: 'ISIC ResNet-50',
      purpose: 'Skin Cancer Detection',
      accuracy: '95.2%',
      dataset: '25,000+ dermatoscopic images',
      conditions: ['Melanoma', 'Basal Cell Carcinoma', 'Squamous Cell Carcinoma', 'Actinic Keratosis', 'Benign Keratosis', 'Dermatofibroma', 'Nevus'],
      color: 'primary'
    },
    {
      name: 'CheXNet DenseNet-121',
      purpose: 'Chest X-ray Analysis',
      accuracy: '94.8%',
      dataset: '112,000+ chest X-rays',
      conditions: ['Pneumonia', 'Pneumothorax', 'Cardiomegaly', 'Pleural Effusion', 'Atelectasis', 'Consolidation', 'Mass'],
      color: 'secondary'
    },
    {
      name: 'Groq + Medical LLM',
      purpose: 'Virtual Triage',
      accuracy: '92.5%',
      dataset: 'Medical knowledge base + symptom patterns',
      conditions: ['Symptom Analysis', 'Urgency Assessment', 'Care Recommendations', 'Follow-up Guidance'],
      color: 'info'
    }
  ];

  const team = [
    {
      name: 'Dr. Sarah Chen',
      role: 'Chief Medical Officer',
      specialty: 'Dermatology & AI Ethics',
      image: '👩‍⚕️'
    },
    {
      name: 'Dr. Michael Rodriguez',
      role: 'Head of Radiology AI',
      specialty: 'Radiology & Computer Vision',
      image: '👨‍⚕️'
    },
    {
      name: 'Dr. Emily Watson',
      role: 'Clinical Research Director',
      specialty: 'Emergency Medicine & Triage',
      image: '👩‍⚕️'
    },
    {
      name: 'Alex Thompson',
      role: 'Lead AI Engineer',
      specialty: 'Deep Learning & MLOps',
      image: '👨‍💻'
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-extrabold mb-6">
              About MediScan-AI
            </h1>
            <p className="text-xl leading-relaxed mb-8">
              We're revolutionizing healthcare accessibility through advanced artificial intelligence, 
              making medical expertise available to everyone, everywhere, at any time.
            </p>
            <div className="flex gap-4 justify-center">
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
                <div className="text-2xl font-bold">2.5M+</div>
                <div className="text-sm opacity-90">Images Analyzed</div>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
                <div className="text-2xl font-bold">50K+</div>
                <div className="text-sm opacity-90">Healthcare Users</div>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
                <div className="text-2xl font-bold">95%+</div>
                <div className="text-sm opacity-90">Accuracy Rate</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center mb-16">
          <h2 className="text-4xl font-bold text-neutral-800 mb-6">Our Mission</h2>
          <p className="text-xl text-neutral-600 leading-relaxed">
            To democratize access to high-quality medical analysis through cutting-edge AI technology, 
            empowering healthcare professionals and patients with instant, accurate diagnostic insights 
            that improve health outcomes worldwide.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card text-center">
              <div className="w-12 h-12 bg-primary-100 text-primary-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-neutral-800 mb-3">{feature.title}</h3>
              <p className="text-neutral-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* AI Models Section */}
      <section className="bg-neutral-0 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-neutral-800 mb-4">
              Our AI Models
            </h2>
            <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
              State-of-the-art deep learning models trained on millions of medical images 
              and validated by healthcare professionals
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {models.map((model, index) => (
              <div key={index} className="card">
                <div className="card-header">
                  <h3 className="card-title">{model.name}</h3>
                  <p className="card-subtitle">{model.purpose}</p>
                </div>
                
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-neutral-600">Accuracy</span>
                    <span className={`badge badge-success font-semibold`}>{model.accuracy}</span>
                  </div>
                  
                  <div>
                    <span className="text-sm text-neutral-600 block mb-2">Training Dataset</span>
                    <p className="text-sm text-neutral-800">{model.dataset}</p>
                  </div>
                  
                  <div>
                    <span className="text-sm text-neutral-600 block mb-2">Detectable Conditions</span>
                    <div className="flex flex-wrap gap-1">
                      {model.conditions.slice(0, 4).map((condition, idx) => (
                        <span key={idx} className="badge badge-info text-xs">
                          {condition}
                        </span>
                      ))}
                      {model.conditions.length > 4 && (
                        <span className="badge badge-info text-xs">
                          +{model.conditions.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-neutral-800 mb-4">
            Meet Our Team
          </h2>
          <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
            A diverse team of medical professionals, AI researchers, and engineers 
            working together to advance healthcare technology
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {team.map((member, index) => (
            <div key={index} className="card text-center">
              <div className="text-6xl mb-4">{member.image}</div>
              <h3 className="text-lg font-semibold text-neutral-800 mb-1">{member.name}</h3>
              <p className="text-sm text-primary-600 font-medium mb-2">{member.role}</p>
              <p className="text-sm text-neutral-600">{member.specialty}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Technology Stack */}
      <section className="bg-neutral-0 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-neutral-800 mb-4">
              Technology Stack
            </h2>
            <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
              Built with cutting-edge technologies for reliability, scalability, and performance
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {[
              { name: 'PyTorch', category: 'Deep Learning' },
              { name: 'FastAPI', category: 'Backend' },
              { name: 'React', category: 'Frontend' },
              { name: 'AWS', category: 'Cloud' },
              { name: 'PostgreSQL', category: 'Database' }
            ].map((tech, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-neutral-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">⚡</span>
                </div>
                <h4 className="font-medium text-neutral-800">{tech.name}</h4>
                <p className="text-xs text-neutral-500">{tech.category}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-neutral-800 mb-4">
              Get in Touch
            </h2>
            <p className="text-lg text-neutral-600">
              Have questions about our AI models or want to collaborate? We'd love to hear from you.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card text-center">
              <div className="w-12 h-12 bg-primary-100 text-primary-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-neutral-800 mb-2">Email Us</h3>
              <p className="text-neutral-600 text-sm">support@mediscan-ai.com</p>
            </div>

            <div className="card text-center">
              <div className="w-12 h-12 bg-secondary-100 text-secondary-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-neutral-800 mb-2">Documentation</h3>
              <p className="text-neutral-600 text-sm">docs.mediscan-ai.com</p>
            </div>

            <div className="card text-center">
              <div className="w-12 h-12 bg-info-100 text-info-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a2 2 0 01-2-2v-6a2 2 0 012-2h8z" />
                </svg>
              </div>
              <h3 className="font-semibold text-neutral-800 mb-2">Community</h3>
              <p className="text-neutral-600 text-sm">Join our Discord</p>
            </div>
          </div>
        </div>
      </section>

      {/* Medical Disclaimer */}
      <section className="bg-warning-50 border-t border-warning-200 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-warning-100 text-warning-600 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-warning-800 mb-2">Medical Disclaimer</h3>
                <p className="text-sm text-warning-700 leading-relaxed">
                  <strong>IMPORTANT:</strong> MediScan-AI is designed as a diagnostic assistance tool and should not replace 
                  professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare 
                  professionals for medical concerns. In case of medical emergencies, call emergency services immediately. 
                  Our AI models are continuously improving but should be used as a supplementary tool alongside 
                  professional medical judgment.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
