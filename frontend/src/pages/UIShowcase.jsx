import React, { useState } from 'react';
import { 
  HeartIcon, 
  StethoscopeIcon, 
  ChatIcon, 
  CheckCircleIcon, 
  ExclamationIcon,
  UploadIcon,
  ZapIcon,
  ChipIcon
} from '../components/common/Icons';

const UIShowcase = () => {
  const [activeTab, setActiveTab] = useState('colors');

  const tabs = [
    { id: 'colors', label: 'Colors' },
    { id: 'typography', label: 'Typography' },
    { id: 'buttons', label: 'Buttons' },
    { id: 'cards', label: 'Cards' },
    { id: 'forms', label: 'Forms' },
    { id: 'icons', label: 'Icons' }
  ];

  return (
    <div className="min-h-screen bg-neutral-50">
      <div className="container mx-auto px-4 py-8">
        <div className="page-header">
          <h1 className="page-title">Design System Showcase</h1>
          <p className="page-subtitle">
            Comprehensive overview of MediScan-AI's modern healthcare design system
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-8 justify-center">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-ghost'}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Colors Section */}
        {activeTab === 'colors' && (
          <div className="space-y-8">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Color Palette</h2>
                <p className="card-subtitle">Healthcare-focused color system with accessibility in mind</p>
              </div>

              <div className="space-y-6">
                {/* Primary Colors */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Primary (Medical Blue)</h3>
                  <div className="grid grid-cols-5 md:grid-cols-10 gap-2">
                    {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((shade) => (
                      <div key={shade} className="text-center">
                        <div 
                          className={`w-full h-16 rounded-lg mb-2 bg-primary-${shade}`}
                          style={{ backgroundColor: `var(--primary-${shade})` }}
                        />
                        <div className="text-xs text-neutral-600">{shade}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Secondary Colors */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Secondary (Medical Green)</h3>
                  <div className="grid grid-cols-5 md:grid-cols-10 gap-2">
                    {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((shade) => (
                      <div key={shade} className="text-center">
                        <div 
                          className={`w-full h-16 rounded-lg mb-2 bg-secondary-${shade}`}
                          style={{ backgroundColor: `var(--secondary-${shade})` }}
                        />
                        <div className="text-xs text-neutral-600">{shade}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Status Colors */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Status Colors</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="w-full h-16 bg-success-500 rounded-lg mb-2" />
                      <div className="text-sm font-medium">Success</div>
                    </div>
                    <div className="text-center">
                      <div className="w-full h-16 bg-warning-500 rounded-lg mb-2" />
                      <div className="text-sm font-medium">Warning</div>
                    </div>
                    <div className="text-center">
                      <div className="w-full h-16 bg-error-500 rounded-lg mb-2" />
                      <div className="text-sm font-medium">Error</div>
                    </div>
                    <div className="text-center">
                      <div className="w-full h-16 bg-info-500 rounded-lg mb-2" />
                      <div className="text-sm font-medium">Info</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Typography Section */}
        {activeTab === 'typography' && (
          <div className="space-y-8">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Typography Scale</h2>
                <p className="card-subtitle">Inter font family with medical-grade readability</p>
              </div>

              <div className="space-y-6">
                <div className="text-6xl font-extrabold text-neutral-800">Heading 1 - 60px</div>
                <div className="text-5xl font-bold text-neutral-800">Heading 2 - 48px</div>
                <div className="text-4xl font-bold text-neutral-800">Heading 3 - 36px</div>
                <div className="text-3xl font-semibold text-neutral-800">Heading 4 - 30px</div>
                <div className="text-2xl font-semibold text-neutral-800">Heading 5 - 24px</div>
                <div className="text-xl font-medium text-neutral-800">Heading 6 - 20px</div>
                <div className="text-lg text-neutral-700">Large text - 18px</div>
                <div className="text-base text-neutral-700">Body text - 16px</div>
                <div className="text-sm text-neutral-600">Small text - 14px</div>
                <div className="text-xs text-neutral-500">Extra small - 12px</div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Font Weights</h2>
              </div>
              <div className="space-y-3">
                <div className="text-lg font-light">Light (300) - For subtle text</div>
                <div className="text-lg font-normal">Normal (400) - For body text</div>
                <div className="text-lg font-medium">Medium (500) - For emphasis</div>
                <div className="text-lg font-semibold">Semibold (600) - For headings</div>
                <div className="text-lg font-bold">Bold (700) - For strong emphasis</div>
                <div className="text-lg font-extrabold">Extrabold (800) - For hero text</div>
              </div>
            </div>
          </div>
        )}

        {/* Buttons Section */}
        {activeTab === 'buttons' && (
          <div className="space-y-8">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Button Variants</h2>
                <p className="card-subtitle">Accessible buttons with hover states and focus rings</p>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Primary Buttons</h3>
                  <div className="flex flex-wrap gap-4">
                    <button className="btn btn-primary">Primary</button>
                    <button className="btn btn-primary btn-sm">Small Primary</button>
                    <button className="btn btn-primary btn-lg">Large Primary</button>
                    <button className="btn btn-primary" disabled>Disabled</button>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Secondary Buttons</h3>
                  <div className="flex flex-wrap gap-4">
                    <button className="btn btn-secondary">Secondary</button>
                    <button className="btn btn-secondary btn-sm">Small Secondary</button>
                    <button className="btn btn-secondary btn-lg">Large Secondary</button>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Outline Buttons</h3>
                  <div className="flex flex-wrap gap-4">
                    <button className="btn btn-outline">Outline</button>
                    <button className="btn btn-outline btn-sm">Small Outline</button>
                    <button className="btn btn-outline btn-lg">Large Outline</button>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Ghost Buttons</h3>
                  <div className="flex flex-wrap gap-4">
                    <button className="btn btn-ghost">Ghost</button>
                    <button className="btn btn-ghost btn-sm">Small Ghost</button>
                    <button className="btn btn-ghost btn-lg">Large Ghost</button>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Buttons with Icons</h3>
                  <div className="flex flex-wrap gap-4">
                    <button className="btn btn-primary">
                      <UploadIcon className="w-4 h-4" />
                      Upload File
                    </button>
                    <button className="btn btn-secondary">
                      <ZapIcon className="w-4 h-4" />
                      Analyze
                    </button>
                    <button className="btn btn-outline">
                      <HeartIcon className="w-4 h-4" />
                      Save
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Cards Section */}
        {activeTab === 'cards' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Basic Card */}
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Basic Card</h3>
                  <p className="card-subtitle">Simple card with header</p>
                </div>
                <p className="text-neutral-600">
                  This is a basic card component with a header and body content.
                </p>
              </div>

              {/* Feature Card */}
              <div className="feature-card">
                <div className="feature-icon bg-primary-100 text-primary-600">
                  <StethoscopeIcon className="w-8 h-8" />
                </div>
                <h3 className="feature-title">Feature Card</h3>
                <p className="feature-description">
                  Enhanced card with icon, gradient border, and hover effects.
                </p>
                <button className="btn btn-primary w-full">Action Button</button>
              </div>

              {/* Stats Card */}
              <div className="stats-card">
                <div className="stats-number text-secondary-600">95%</div>
                <div className="stats-label">Accuracy Rate</div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Result Card Example</h2>
                <p className="card-subtitle">Medical analysis result display</p>
              </div>
              
              <div className="result-card">
                <div className="result-header">
                  <h3 className="text-lg font-semibold">Skin Lesion Analysis</h3>
                  <span className="badge badge-success">High Confidence</span>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Benign Nevus</span>
                      <span className="text-sm text-neutral-600">87%</span>
                    </div>
                    <div className="confidence-bar">
                      <div className="confidence-fill confidence-high" style={{ width: '87%' }} />
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Melanoma</span>
                      <span className="text-sm text-neutral-600">8%</span>
                    </div>
                    <div className="confidence-bar">
                      <div className="confidence-fill confidence-low" style={{ width: '8%' }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Forms Section */}
        {activeTab === 'forms' && (
          <div className="space-y-8">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Form Elements</h2>
                <p className="card-subtitle">Accessible form inputs with proper focus states</p>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Text Input
                  </label>
                  <input 
                    type="text" 
                    className="input" 
                    placeholder="Enter your text here..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Email Input
                  </label>
                  <input 
                    type="email" 
                    className="input" 
                    placeholder="your.email@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Textarea
                  </label>
                  <textarea 
                    className="input min-h-[100px] resize-y" 
                    placeholder="Describe your symptoms..."
                    rows={4}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Select Dropdown
                  </label>
                  <select className="input">
                    <option>Choose an option...</option>
                    <option>Skin Analysis</option>
                    <option>Radiology Analysis</option>
                    <option>Virtual Triage</option>
                  </select>
                </div>

                <div className="upload-area">
                  <div className="upload-icon">
                    <UploadIcon className="w-16 h-16" />
                  </div>
                  <h3 className="text-lg font-semibold text-neutral-700 mb-2">
                    Upload Medical Image
                  </h3>
                  <p className="text-neutral-500 mb-4">
                    Drag and drop or click to browse
                  </p>
                  <div className="text-sm text-neutral-400">
                    Supported: JPG, PNG, DICOM
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Icons Section */}
        {activeTab === 'icons' && (
          <div className="space-y-8">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Icon Library</h2>
                <p className="card-subtitle">Medical and healthcare focused icon set</p>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Medical Icons</h3>
                  <div className="grid grid-cols-4 md:grid-cols-8 gap-4">
                    {[
                      { icon: HeartIcon, name: 'Heart' },
                      { icon: StethoscopeIcon, name: 'Stethoscope' },
                      { icon: ChatIcon, name: 'Chat' },
                      { icon: CheckCircleIcon, name: 'Check Circle' },
                      { icon: ExclamationIcon, name: 'Warning' },
                      { icon: UploadIcon, name: 'Upload' },
                      { icon: ZapIcon, name: 'Lightning' },
                      { icon: ChipIcon, name: 'AI Chip' }
                    ].map(({ icon: IconComponent, name }) => (
                      <div key={name} className="text-center p-4 border border-neutral-200 rounded-lg hover:bg-neutral-50">
                        <IconComponent className="w-8 h-8 mx-auto mb-2 text-primary-600" />
                        <div className="text-xs text-neutral-600">{name}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Icon Sizes</h3>
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <HeartIcon className="w-4 h-4 mx-auto mb-2 text-primary-600" />
                      <div className="text-xs">Small (16px)</div>
                    </div>
                    <div className="text-center">
                      <HeartIcon className="w-6 h-6 mx-auto mb-2 text-primary-600" />
                      <div className="text-xs">Medium (24px)</div>
                    </div>
                    <div className="text-center">
                      <HeartIcon className="w-8 h-8 mx-auto mb-2 text-primary-600" />
                      <div className="text-xs">Large (32px)</div>
                    </div>
                    <div className="text-center">
                      <HeartIcon className="w-12 h-12 mx-auto mb-2 text-primary-600" />
                      <div className="text-xs">XL (48px)</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Badges and Status */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Badges & Status Indicators</h2>
            <p className="card-subtitle">Visual status communication</p>
          </div>
          
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-neutral-700 mb-3">Status Badges</h3>
              <div className="flex flex-wrap gap-2">
                <span className="badge badge-success">Success</span>
                <span className="badge badge-warning">Warning</span>
                <span className="badge badge-error">Error</span>
                <span className="badge badge-info">Info</span>
              </div>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-neutral-700 mb-3">Loading States</h3>
              <div className="flex items-center gap-4">
                <div className="loading-spinner" />
                <div className="skeleton h-4 w-32" />
                <div className="skeleton h-8 w-24 rounded-full" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UIShowcase;
