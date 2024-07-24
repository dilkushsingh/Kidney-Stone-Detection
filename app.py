import gradio as gr
import requests
import os

# API key for IBM Cloud authentication 
API_KEY = os.getenv('IBM_API_KEY')
if API_KEY is None:
    print("Error: There is some issue with IBM_API_KEY.")
            
# Endpoint URL from IBM Cloud deployment (replace with your actual endpoint)
endpoint_url = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/05450e74-3180-42b5-8a3c-667a7435a3c4/predictions?version=2021-05-01"

# Function to authenticate and make prediction request to IBM Cloud endpoint
def predict_kidney_stone(gravity, ph, osmolality, conductivity, urea, calcium):
    try:
        # Authenticate and get token
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', 
                                       data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]

        # Prepare data payload
        data = {
            "input_data": [
                {
                    "fields": ["gravity", "ph", "osmolality", "conductivity", "urea", "calcium"],
                    "values": [[gravity, ph, osmolality, conductivity, urea, calcium]]
                }
            ]
        }

        # Make POST request to the endpoint with authentication headers
        response = requests.post(endpoint_url, json=data, headers={'Authorization': 'Bearer ' + mltoken})

        # Handle response
        if response.status_code == 200:
            prediction = response.json()['predictions'][0]['values'][0][0]  # Assuming response structure
            return "High Chances" if int(prediction) == 1 else "Low chances"
        else:
            return "Error: Unable to get prediction from endpoint"

    except Exception as e:
        return f"Error: {str(e)}"

# Define Gradio interface
iface = gr.Interface(
    fn=predict_kidney_stone, 
    inputs = [
            gr.Slider(minimum=0.8, maximum=1.5, label="Gravity"),
            gr.Slider(minimum=3, maximum=8, label="pH"),
            gr.Slider(minimum=200, maximum=1200, label="Osmolality"),
            gr.Slider(minimum=5, maximum=30, label="Conductivity"),
            gr.Slider(minimum=50, maximum=700, label="Urea"),
            gr.Slider(minimum=0, maximum=20, label="Calcium")
    ],
    outputs=gr.Textbox(label="Prediction"),  # Output: Textbox to display prediction message
    title="Kidney Stone Detector",
    description="Predicts the likelihood of kidney stone based on input parameters.",
    examples=[
        [1.021, 4.91, 725, 14, 443, 2.45],  # Example input values
        [1.054, 5.57, 869, 29.53, 363, 5.54, 1]   # Another example input
    ]
)

# Launch the Gradio interface
iface.launch()
