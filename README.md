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

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ (Download from [nodejs.org](https://nodejs.org/))
- **Python** 3.11+ (or Python 3.10+)
- **Git**

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/Joystonm/MediScan-AI.git
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

### Development Setup

#### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
npm start
```
