# 🏥 MediScan-AI

**AI-Powered Medical Diagnosis Assistant**

MediScan-AI is a comprehensive medical diagnosis assistance platform that leverages advanced artificial intelligence to provide instant analysis of skin lesions, chest X-rays, and virtual triage assessments. Built with modern web technologies and state-of-the-art machine learning models.

## 🌟 Features

### 🔬 Skin Lesion Analysis
- **ISIC-trained ResNet-50** model for skin cancer detection
- **7 condition classifications** including melanoma, basal cell carcinoma, and benign lesions
- **Risk assessment** with confidence scoring
- **Lesion characteristic analysis** (asymmetry, border, color, diameter)
- **Personalized recommendations** based on analysis results

### 🩻 Chest X-ray Analysis
- **CheXNet DenseNet-121** model for pathology detection
- **14 pathology classifications** including pneumonia, pneumothorax, and cardiomegaly
- **Multi-label detection** capabilities
- **Urgency level assessment** (routine, urgent, emergency)
- **Clinical findings generation** with confidence scores

### 🩺 Virtual Triage Assistant
- **Intelligent chatbot** powered by Groq, Tavily, and Keyword AI
- **Natural language symptom assessment**
- **Urgency level determination**
- **Personalized medical guidance**
- **Integration with medical knowledge bases**

## 🏗️ Architecture

```
├── backend/                        # FastAPI + AI models
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── routes/                 # API endpoints
│   │   ├── services/               # Business logic
│   │   ├── models/                 # AI model loaders
│   │   └── utils/                  # Utilities
│   └── requirements.txt
│
├── frontend/                       # React.js frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
│
├── tests/                          # Test suites
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ (Download from [nodejs.org](https://nodejs.org/))
- **Python** 3.11+ (or Python 3.10+)
- **Git**

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/MediScan-AI.git
   cd MediScan-AI
   ```

2. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env.local
   # Edit .env.local with your real API keys
   # Note: .env.local is ignored by git for security
   ```

3. **Install and run the backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Install and run the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm start
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Setup

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### ✅ **Testing Upload Functionality**

The Upload Image button is now fully functional! Test it by:

1. **Start both backend and frontend**
2. **Navigate to Dashboard**
3. **Click "Upload Image" on any analysis module**
4. **Upload a medical image** (JPG, PNG, BMP, DICOM supported)
5. **Click "Analyze"** to get AI-powered results
6. **View structured results** with confidence scores and recommendations

**Test Script Available**: Run `python test_upload.py` to verify all endpoints work correctly.

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
KEYWORD_AI_KEY=your_keyword_ai_key

# Model Paths
SKIN_MODEL_PATH=models/isic_model.pth
RADIOLOGY_MODEL_PATH=models/chexnet_model.pth

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

### Model Setup

1. **Download pretrained models** (links to be provided):
   - ISIC skin cancer model: `models/isic_model.pth`
   - CheXNet radiology model: `models/chexnet_model.pth`

2. **Place models in the models directory**:
   ```bash
   mkdir -p models
   # Copy your model files here
   ```

## 📊 API Documentation

### Health Endpoints
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system status
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

### Skin Analysis
- `POST /api/v1/skin-analysis` - Analyze skin lesion image
- `GET /api/v1/skin-analysis/supported-formats` - Get supported formats

### Radiology Analysis
- `POST /api/v1/radiology-analysis` - Analyze X-ray image
- `GET /api/v1/radiology-analysis/supported-types` - Get supported types

### Virtual Triage
- `POST /api/v1/triage` - Perform triage assessment
- `POST /api/v1/triage/chat` - Chat with triage assistant

## 🧪 Testing

### Run All Tests
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Test Coverage
```bash
# Backend coverage
pytest --cov=app tests/

# Frontend coverage
npm run test:coverage
```

## 🔒 Security & Privacy

### Data Protection
- **No persistent storage** of medical images without consent
- **End-to-end encryption** for data transmission
- **HIPAA-compliant** design principles
- **Secure API endpoints** with rate limiting

### Privacy Features
- **Local processing** option for sensitive data
- **Anonymized analytics** only
- **User consent** required for data retention
- **Audit logging** for compliance

## 📈 Performance

### Benchmarks
- **Skin analysis**: ~2-3 seconds per image
- **X-ray analysis**: ~3-5 seconds per image
- **Triage response**: ~1-2 seconds per query
- **Concurrent users**: 100+ supported

### Optimization
- **Model quantization** for faster inference
- **Caching** for repeated requests
- **Load balancing** for high availability
- **CDN integration** for static assets

## 🛠️ Development

### Code Style
```bash
# Backend formatting
black backend/app/
flake8 backend/app/

# Frontend formatting
npm run format
npm run lint
```

### Adding New Features

1. **Backend**: Add routes in `backend/app/routes/`
2. **Frontend**: Add components in `frontend/src/components/`
3. **Tests**: Add tests in `tests/`
4. **Documentation**: Update README and API docs

### Model Integration

To add a new AI model:

1. Create model loader in `backend/app/models/`
2. Add service in `backend/app/services/`
3. Create API routes in `backend/app/routes/`
4. Add frontend components
5. Write comprehensive tests

## 🚀 Deployment

### Production Deployment

1. **Set up production environment**
   ```bash
   cp .env.example .env.production
   # Configure production settings
   ```

2. **Build and deploy the application**
   ```bash
   # Backend deployment
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   
   # Frontend deployment
   cd ../frontend
   npm install
   npm run build
   # Serve the build folder with a web server like Nginx or Apache
   ```

3. **Set up reverse proxy** (Nginx configuration recommended)

4. **Configure SSL certificates**

### Cloud Deployment

#### AWS
- Use **EC2** instances with **Application Load Balancer**
- **S3** for model storage and static assets
- **RDS** for database
- **CloudFront** for CDN

#### Google Cloud
- Use **Compute Engine** or **App Engine**
- **Cloud Storage** for models
- **Cloud SQL** for database

#### Azure
- Use **Virtual Machines** or **App Service**
- **Blob Storage** for models
- **Azure Database** for PostgreSQL

## 📊 Monitoring

### Metrics
- **API response times**
- **Model inference latency**
- **Error rates**
- **Resource utilization**

### Logging
- **Structured logging** with JSON format
- **Request/response logging**
- **Error tracking**
- **Audit trails**

### Alerting
- **Health check failures**
- **High error rates**
- **Resource exhaustion**
- **Security incidents**

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code of Conduct
Please read our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Medical Disclaimer

**IMPORTANT**: MediScan-AI is designed as a diagnostic assistance tool and should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns. In case of medical emergencies, call emergency services immediately.

## 📞 Support

- **Documentation**: [docs.mediscan-ai.com](https://docs.mediscan-ai.com)
- **Issues**: [GitHub Issues](https://github.com/your-username/MediScan-AI/issues)
- **Email**: support@mediscan-ai.com
- **Discord**: [Join our community](https://discord.gg/mediscan-ai)

## 🙏 Acknowledgments

- **ISIC** for skin lesion datasets
- **NIH** for ChestX-ray14 dataset
- **Stanford ML Group** for CheXNet architecture
- **Open source community** for tools and libraries

## 🗺️ Roadmap

### Q2 2024
- [ ] Mobile app development
- [ ] Additional imaging modalities (MRI, CT)
- [ ] Multi-language support
- [ ] Offline mode capabilities

### Q3 2024
- [ ] EHR system integration
- [ ] Telemedicine platform integration
- [ ] Advanced reporting features
- [ ] Real-time collaboration tools

### Q4 2024
- [ ] AI model improvements
- [ ] Federated learning implementation
- [ ] API for third-party integrations
- [ ] Advanced analytics dashboard

---

**Made with ❤️ for better healthcare accessibility**
