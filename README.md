# Carbon Footprint Calculator with AI Recommendations

This project calculates a user's carbon footprint based on daily kilometers driven, electricity usage (kWh), and meat-based meals. It then uses AWS Lambda, API Gateway, and Amazon Bedrock (Titan Text Express) to generate personalized recommendations for reducing the carbon footprint.

## Project Components

- **Front-End (index.html):**  
  A simple web form that collects user input and displays the results.

- **AWS Lambda:**  
  A serverless function that:
  - Parses input data.
  - Calculates carbon emissions.
  - Invokes Amazon Bedrock to generate AI recommendations.
  - Returns the results via API Gateway.

- **API Gateway:**  
  Routes HTTP requests from the front-end to the Lambda function and returns the response.

- **Amazon Bedrock:**  
  Uses the Titan Text Express model to generate detailed, AI-powered recommendations.

## AWS Setup

- **Lambda Function Code:**  
  (See `lambda_function.py` for the complete code.)
- **Environment Variable:**  
  `BEDROCK_MODEL_ID` is set to `amazon.titan-text-express-v1`.
- **IAM Permissions:**  
  The Lambda execution role includes permission for `bedrock:InvokeModel`.
- **API Gateway:**  
  Configured to accept POST requests at the `/calculate` resource.
- **CORS:**  
  Enabled in API Gateway to allow cross-origin requests from the front-end.

## How to Run Locally

1. Open `index.html` in your web browser using a local server (e.g., VS Code Live Server or Python's `http.server`).
2. Enter your details and click "Calculate" to see the emissions and AI-generated recommendation.

## Future Enhancements

- Save user inputs and track changes over time.
- Improve UI with additional styling or visualizations.
