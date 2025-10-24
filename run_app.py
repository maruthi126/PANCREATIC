#!/usr/bin/env python3
"""
Optimized startup script for MedAI Vision
This script suppresses all warnings and provides a clean startup experience.
"""

import os
import sys
import warnings

# Suppress all warnings before importing any libraries
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use first GPU if available

# Suppress specific library warnings
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Redirect stderr to suppress TensorFlow warnings
class SuppressStderr:
    def __enter__(self):
        self.stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self.stderr

if __name__ == '__main__':
    print("🚀 Starting MedAI Vision...")
    print("📦 Loading models (this may take a moment)...")
    
    with SuppressStderr():
        # Import and run the app
        from app import app
        
        print("\n" + "="*60)
        print("🎉 MedAI Vision - MRI Segmentation Platform")
        print("="*60)
        print("✅ All models loaded successfully!")
        print("✅ Application is ready!")
        print("🌐 Open your browser and go to: http://localhost:5002")
        print("🔄 Press Ctrl+C to stop the server")
        print("="*60 + "\n")
        
        app.run(host='0.0.0.0', port=5002, debug=False)  # Set debug=False for production 