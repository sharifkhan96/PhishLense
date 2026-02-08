"""
ML Model Service for Traffic Classification
This service integrates with the trained ML model for phishing detection
"""
import os
import pickle
import numpy as np
import pandas as pd
import re
from urllib.parse import urlparse
from django.conf import settings
from typing import Dict, Optional
import joblib


class MLModelService:
    """Service for ML model integration"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.feature_names = None
        self.payload_type_encoder = None
        self.load_model()
    
    def load_model(self):
        """Load the ML model and related files from disk"""
        if not settings.ML_MODEL_ENABLED:
            print("⚠️ ML_MODEL_ENABLED is False, skipping model load")
            return
        
        model_path = settings.ML_MODEL_PATH
        model_dir = os.path.dirname(model_path) if os.path.dirname(model_path) else 'ml_model'
        
        # Load model
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.model_loaded = True
                print(f"✅ ML Model loaded successfully from {model_path}")
            except Exception as e:
                print(f"❌ Error loading ML model: {e}")
                self.model_loaded = False
        else:
            print(f"⚠️ ML Model file not found at {model_path}")
            self.model_loaded = False
        
        # Load feature names
        feature_names_path = os.path.join(model_dir, 'feature_names.pkl')
        if os.path.exists(feature_names_path):
            try:
                with open(feature_names_path, 'rb') as f:
                    self.feature_names = pickle.load(f)
                print(f"✅ Loaded {len(self.feature_names)} feature names")
            except Exception as e:
                print(f"⚠️ Error loading feature names: {e}")
        
        # Load payload type encoder
        encoder_path = os.path.join(model_dir, 'payload_type_encoder.pkl')
        if os.path.exists(encoder_path):
            try:
                with open(encoder_path, 'rb') as f:
                    self.payload_type_encoder = pickle.load(f)
                print(f"✅ Loaded payload type encoder")
            except Exception as e:
                print(f"⚠️ Error loading payload type encoder: {e}")
    
    def predict(self, source_ip: str, destination_ip: str, payload: str, 
                payload_type: str, port: int, date_time) -> Dict[str, any]:
        """
        Predict if traffic is normal or malicious using trained ML model
        
        Args:
            source_ip: Source IP address
            destination_ip: Destination IP/email
            payload: Payload content
            payload_type: Type of payload (link, text, image, etc.)
            port: Port number
            date_time: DateTime of the event
        
        Returns:
            {
                'prediction': 'normal' or 'malicious',
                'confidence': float (0-1)
            }
        """
        if not self.model_loaded or self.model is None:
            return {
                'prediction': 'unknown',
                'confidence': 0.0,
                'note': 'ML model not loaded'
            }
        
        try:
            # Extract features using the same logic as training
            features = self._extract_features(source_ip, destination_ip, payload, payload_type, port, date_time)
            
            # Ensure features are in the same order as training
            if self.feature_names:
                # Create DataFrame and reorder columns
                features_df = pd.DataFrame([features], columns=self.feature_names[:len(features)])
                # Fill any missing columns with 0
                for col in self.feature_names:
                    if col not in features_df.columns:
                        features_df[col] = 0
                features_array = features_df[self.feature_names].values[0]
            else:
                features_array = np.array(features)
            
            # Make prediction
            prediction = self.model.predict([features_array])[0]
            prediction_proba = self.model.predict_proba([features_array])[0] if hasattr(self.model, 'predict_proba') else None
            
            # Map prediction (1 = malicious, 0 = benign/normal)
            if isinstance(prediction, (int, np.integer)):
                prediction_label = 'malicious' if prediction == 1 else 'normal'
            else:
                prediction_label = str(prediction).lower()
            
            # Get confidence (probability of predicted class)
            if prediction_proba is not None:
                confidence = float(prediction_proba.max())
            else:
                confidence = 0.5
            
            return {
                'prediction': prediction_label,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"❌ Error making ML prediction: {e}")
            import traceback
            traceback.print_exc()
            return {
                'prediction': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _extract_features(self, source_ip: str, destination_ip: str, payload: str,
                         payload_type: str, port: int, date_time) -> list:
        """
        Extract features from traffic data - MUST match training feature extraction exactly
        """
        features = {}
        
        # Basic payload features
        features['payload_length'] = len(payload)
        features['payload_word_count'] = len(payload.split())
        features['payload_has_url'] = 1 if re.search(r'http[s]?://', payload) else 0
        features['payload_has_short_url'] = 1 if re.search(r'bit\.ly|tinyurl|goo\.gl|t\.co', payload) else 0
        features['payload_has_ip'] = 1 if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', payload) else 0
        
        # Phishing keywords (must match training exactly)
        phishing_keywords = ['urgent', 'verify', 'suspended', 'click', 'immediately', 'limited time', 
                            'winner', 'prize', 'claim', 'update', 'secure', 'alert', 'action required']
        for keyword in phishing_keywords:
            features[f'has_{keyword.replace(" ", "_")}'] = 1 if keyword.lower() in payload.lower() else 0
        
        # URL features
        url_match = re.search(r'http[s]?://([^\s]+)', payload)
        if url_match:
            url = url_match.group(1)
            features['url_length'] = len(url)
            features['url_has_hyphen'] = 1 if '-' in url else 0
            features['url_has_digits'] = 1 if re.search(r'\d', url) else 0
        else:
            features['url_length'] = 0
            features['url_has_hyphen'] = 0
            features['url_has_digits'] = 0
        
        # Port features
        features['port'] = float(port) if port else 0.0
        features['is_common_port'] = 1 if port in [80, 443, 25, 587, 993, 22] else 0
        features['is_suspicious_port'] = 1 if port in [8080, 8000, 6667, 21, 23] else 0
        
        # IP features
        if '.' in source_ip:
            ip_parts = [float(x) for x in source_ip.split('.')]
            features['ip_first_octet'] = ip_parts[0] if len(ip_parts) > 0 else 0.0
            is_private = (ip_parts[0] == 192) or (ip_parts[0] == 10) or ((ip_parts[0] == 172) and (len(ip_parts) > 1 and 16 <= ip_parts[1] <= 31))
            features['is_private_ip'] = 1 if is_private else 0
        else:
            features['ip_first_octet'] = 0.0
            features['is_private_ip'] = 0
        
        # Destination features
        features['destination_is_email'] = 1 if '@' in (destination_ip or '') else 0
        
        # Text patterns
        features['has_exclamation'] = payload.count('!')
        features['has_question_mark'] = payload.count('?')
        payload_length = features['payload_length']
        features['uppercase_ratio'] = len(re.findall(r'[A-Z]', payload)) / (payload_length + 1)
        features['number_ratio'] = len(re.findall(r'\d', payload)) / (payload_length + 1)
        
        # Payload type encoding (use saved encoder if available)
        if self.payload_type_encoder:
            try:
                features['payload_type_encoded'] = float(self.payload_type_encoder.transform([payload_type])[0])
            except:
                # If payload_type not in encoder, use 0
                features['payload_type_encoded'] = 0.0
        else:
            # Fallback encoding
            payload_type_map = {'link': 0, 'text': 1, 'image': 2, 'video': 3, 'audio': 4, 'pdf': 5, 'txt': 6, 'file': 7}
            features['payload_type_encoded'] = float(payload_type_map.get(payload_type.lower(), 0))
        
        # Convert to list in the same order as feature_names (if available)
        if self.feature_names:
            feature_list = [features.get(name, 0.0) for name in self.feature_names]
        else:
            feature_list = list(features.values())
        
        return feature_list


# Global ML service instance
ml_service = MLModelService()

