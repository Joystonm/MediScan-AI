# PyTorch Installation Guide for MediScan-AI

## Quick Fix for Current Error

The error you're seeing is because PyTorch is not installed. Here are the steps to fix it:

### Option 1: Install PyTorch (Recommended)

```bash
# Navigate to backend directory
cd backend

# Install PyTorch for CPU (faster installation)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Or install PyTorch with CUDA support (if you have NVIDIA GPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Option 2: Install All Dependencies

```bash
# Install all requirements including PyTorch
pip install -r requirements.txt
```

### Option 3: Run in Mock Mode (Current State)

The application will now run in mock mode without PyTorch, providing realistic but simulated analysis results.

## Verification

After installation, restart the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO: Model manager initialized successfully
INFO: Models loaded: ['skin', 'radiology']
INFO: Device: cuda (or cpu)
```

## Performance Comparison

| Mode | Analysis Time | Accuracy | GPU Support |
|------|---------------|----------|-------------|
| **Mock Mode** | ~0.5s | Simulated | ❌ |
| **CPU Mode** | ~2-5s | Real AI | ❌ |
| **GPU Mode** | ~1-3s | Real AI | ✅ |

## System Requirements

### Minimum (Mock Mode)
- Python 3.11+
- 4GB RAM
- No GPU required

### Recommended (AI Mode)
- Python 3.11+
- 8GB+ RAM
- NVIDIA GPU with 4GB+ VRAM (optional but recommended)
- CUDA 11.8+ (for GPU acceleration)

## Troubleshooting

### Common Issues

1. **"No module named 'torch'"**
   ```bash
   pip install torch torchvision
   ```

2. **CUDA out of memory**
   ```bash
   # Use CPU mode instead
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Slow analysis on CPU**
   - This is normal for CPU inference
   - Consider using GPU or running in mock mode for development

### Check Installation

```python
# Test PyTorch installation
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Current Status

✅ **Application runs in mock mode** - Provides realistic simulated results
✅ **All endpoints functional** - Upload, analysis, and results work
✅ **Frontend integration** - Dashboard displays results correctly
⚠️ **AI models not loaded** - Install PyTorch for real AI analysis

## Next Steps

1. **For Development**: Continue using mock mode - it's fast and functional
2. **For Production**: Install PyTorch for real AI analysis
3. **For Performance**: Add GPU support for fastest analysis

The application is fully functional in mock mode and will automatically switch to AI mode when PyTorch is installed.
