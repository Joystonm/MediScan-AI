// Upload skin/X-ray images component
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const UploadImage = ({ onImageUpload, analysisType = 'skin' }) => {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setUploadedImage({
          file,
          preview: reader.result,
          name: file.name,
          size: file.size
        });
      };
      reader.readAsDataURL(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const handleAnalyze = async () => {
    if (!uploadedImage) return;

    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadedImage.file);

      const endpoint = analysisType === 'skin' 
        ? '/api/v1/skin-analysis/analyze' 
        : '/api/v1/radiology-analysis/analyze';

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result = await response.json();
      
      // Pass both result and image data to parent
      onImageUpload(result, uploadedImage);
      
    } catch (error) {
      console.error('Analysis error:', error);
      // Show user-friendly error message
      alert(`Analysis failed: ${error.message}. Please try again.`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const clearImage = () => {
    setUploadedImage(null);
  };

  return (
    <div className="upload-container">
      <div className="upload-section">
        <h3>
          Upload {analysisType === 'skin' ? 'Skin Lesion' : 'X-ray'} Image
        </h3>
        
        {!uploadedImage ? (
          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? 'active' : ''}`}
          >
            <input {...getInputProps()} />
            <div className="dropzone-content">
              <div className="upload-icon">📁</div>
              <p>
                {isDragActive
                  ? 'Drop the image here...'
                  : 'Drag & drop an image here, or click to select'}
              </p>
              <p className="upload-info">
                Supported formats: JPEG, PNG, BMP (Max 10MB)
              </p>
            </div>
          </div>
        ) : (
          <div className="image-preview">
            <img
              src={uploadedImage.preview}
              alt="Uploaded"
              className="preview-image"
            />
            <div className="image-info">
              <p><strong>File:</strong> {uploadedImage.name}</p>
              <p><strong>Size:</strong> {(uploadedImage.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <div className="image-actions">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="btn btn-primary"
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Image'}
              </button>
              <button
                onClick={clearImage}
                className="btn btn-secondary"
                disabled={isAnalyzing}
              >
                Clear
              </button>
            </div>
          </div>
        )}
      </div>

      {analysisType === 'skin' && (
        <div className="guidelines">
          <h4>Image Guidelines for Skin Analysis:</h4>
          <ul>
            <li>Ensure good lighting and clear focus</li>
            <li>Include a ruler or coin for size reference if possible</li>
            <li>Capture the entire lesion and surrounding skin</li>
            <li>Avoid shadows or reflections</li>
          </ul>
        </div>
      )}

      {analysisType === 'radiology' && (
        <div className="guidelines">
          <h4>Image Guidelines for X-ray Analysis:</h4>
          <ul>
            <li>Upload clear, high-resolution X-ray images</li>
            <li>Ensure proper contrast and brightness</li>
            <li>Include patient positioning information if available</li>
            <li>DICOM format preferred, but JPEG/PNG accepted</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default UploadImage;
