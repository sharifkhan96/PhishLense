# ML Model Integration

Place your trained ML model file here. The model should be a pickle file (`.pkl`) that can predict whether traffic is normal or malicious.

## Model Requirements

The model should accept features extracted from:
- `source_ip`: Source IP address
- `destination_ip`: Destination IP address  
- `payload`: The payload/request content
- `payload_type`: Type of payload (SQLi, XSS, etc.)
- `port`: Port number
- `date_time`: Date and time of the event

## Model Format

The model should be saved as `model.pkl` in this directory.

Expected input: Array/vector of features
Expected output: Binary classification (0 = normal, 1 = malicious) or ('normal', 'malicious')

## Integration Steps

1. Train your model on the 20 rows × 5 columns dataset
2. Save the model as `model.pkl` in this directory
3. Update `ml_service.py` if your model requires different feature extraction
4. Set `ML_MODEL_ENABLED=True` in `.env`
5. Set `ML_MODEL_PATH=ml_model/model.pkl` in `.env` (or use default)

## Testing

Once the model is placed, the system will automatically:
- Load the model on startup
- Use it to predict traffic classification
- Combine ML predictions with AI analysis for comprehensive threat detection


