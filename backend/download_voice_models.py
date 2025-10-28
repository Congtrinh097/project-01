#!/usr/bin/env python3
"""
Download Piper Voice Models
Downloads Vietnamese and English voice models for TTS functionality
"""

import os
import requests
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Voice models to download
VOICE_MODELS = {
    "vi": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx",
        "filename": "vi_VN-vais1000-medium.onnx"
    },
    "vi_config": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx.json",
        "filename": "vi_VN-vais1000-medium.onnx.json"
    },
    "en": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        "filename": "en_US-lessac-medium.onnx"
    },
    "en_config": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
        "filename": "en_US-lessac-medium.onnx.json"
    }
}

def download_file(url: str, filepath: Path) -> bool:
    """Download a file from URL"""
    try:
        logger.info(f"Downloading {filepath.name}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"✅ Downloaded {filepath.name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download {filepath.name}: {e}")
        return False

def main():
    """Main download function"""
    logger.info("🎤 Starting Piper Voice Models Download")
    
    # Create models directory
    models_dir = Path("backend/models/piper")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Models directory: {models_dir.absolute()}")
    
    # Download all models
    success_count = 0
    total_count = len(VOICE_MODELS)
    
    for model_name, model_info in VOICE_MODELS.items():
        filepath = models_dir / model_info["filename"]
        
        # Skip if file already exists
        if filepath.exists():
            logger.info(f"⏭️ {model_info['filename']} already exists, skipping...")
            success_count += 1
            continue
        
        if download_file(model_info["url"], filepath):
            success_count += 1
    
    # Summary
    logger.info("=" * 60)
    logger.info(f"📊 Download Summary: {success_count}/{total_count} files")
    
    if success_count == total_count:
        logger.info("🎉 All voice models downloaded successfully!")
        logger.info("🔊 TTS functionality is now available")
    else:
        logger.warning(f"⚠️ {total_count - success_count} files failed to download")
        logger.info("💡 You can manually download from: https://huggingface.co/rhasspy/piper-voices")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
