import json
import logging
import os
import time
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the Bedrock runtime client for ap-south-1
bedrock_client = boto3.client('bedrock-runtime', region_name='ap-south-1')

# Retrieve the Bedrock model ID from environment variables.
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")

def get_ai_recommendation(total_emissions, kilometers_driven, kwh_used, meat_meals):
    """
    Invokes Amazon Bedrock's Titan Text Express model to generate a personalized recommendation.
    Measures the invocation time and logs the duration.
    """
    prompt = (
        f"User drives {kilometers_driven:.2f} km/day, uses {kwh_used:.2f} kWh, and eats {meat_meals} meat meals. "
        f"Current footprint is {total_emissions:.2f} kg CO₂. Recommend how to reduce it."
    )
    
    payload_body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 8192,
            "stopSequences": [],
            "temperature": 0,
            "topP": 1
        }
    }
    
    logger.info("Sending prompt to Bedrock: " + prompt)
    
    try:
        start_time = time.time()
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload_body)
        )
        end_time = time.time()
        invocation_time = end_time - start_time
        logger.info("Bedrock invocation time: {:.2f} seconds".format(invocation_time))
        
        # Safely retrieve the response body
        raw_response = response.get('Body') or response.get('body')
        if raw_response is None:
            logger.error("No response body found in Bedrock response. Keys: " + json.dumps(list(response.keys())))
            return "No personalized recommendation available."
        
        if hasattr(raw_response, 'read'):
            raw_response_str = raw_response.read().decode('utf-8')
        else:
            raw_response_str = raw_response
        
        response_body = json.loads(raw_response_str)
        logger.info("Bedrock response: " + json.dumps(response_body))
        
        # Try extracting recommendation from the 'results' list if present.
        recommendation = "No recommendation available."
        if "results" in response_body and isinstance(response_body["results"], list) and response_body["results"]:
            recommendation = response_body["results"][0].get("outputText", recommendation)
        else:
            recommendation = response_body.get('generated_text', recommendation)
        
        return recommendation.strip()
    except Exception as e:
        logger.error("Error invoking Bedrock model: " + str(e))
        return "No personalized recommendation available at this time."

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event))
    
    raw_body = event.get('body', '{}')
    logger.info("Raw body: " + raw_body)
    
    try:
        body = json.loads(raw_body)
        logger.info("Parsed body: " + json.dumps(body))
        # Handle potential double-nesting if present
        if isinstance(body, dict) and "body" in body:
            try:
                inner_body = json.loads(body["body"])
                logger.info("Double parsed body: " + json.dumps(inner_body))
                body = inner_body
            except Exception as e:
                logger.error("Error during double parsing: " + str(e))
    except Exception as e:
        logger.error("Error parsing input: " + str(e))
        return {
            'statusCode': 400,
            'headers': {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            'body': json.dumps({'error': 'Invalid input data', 'message': str(e)})
        }
    
    try:
        # Expect input keys: kilometers, kwh, meals
        kilometers_driven = float(body.get('kilometers', 0))
        kwh_used = float(body.get('kwh', 0))
        meat_meals = int(body.get('meals', 0))
        logger.info("Kilometers: {}, kWh: {}, Meals: {}".format(kilometers_driven, kwh_used, meat_meals))
    except Exception as e:
        logger.error("Error converting values: " + str(e))
        return {
            'statusCode': 400,
            'headers': {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            'body': json.dumps({'error': 'Invalid input data', 'message': str(e)})
        }
    
    # Define emission factors (using km-based values)
    emission_per_km = 0.255  # kg CO₂ per kilometer
    emission_kwh = 0.588     # kg CO₂ per kWh
    emission_meal = 1.2        # kg CO₂ per meat-based meal
    
    total_emissions = (kilometers_driven * emission_per_km) + (kwh_used * emission_kwh) + (meat_meals * emission_meal)
    predicted_emissions = (kilometers_driven * emission_per_km * 1.15) + (kwh_used * emission_kwh * 1.10) + (meat_meals * emission_meal * 1.20)
    
    ai_recommendation = get_ai_recommendation(total_emissions, kilometers_driven, kwh_used, meat_meals)
    
    response_data = {
        'current_emissions': total_emissions,
        'predicted_emissions': predicted_emissions,
        'recommendation': ai_recommendation,
        'kilometers_driven': round(kilometers_driven, 2)
    }
    logger.info("Response: " + json.dumps(response_data))
    
    return {
        'statusCode': 200,
        'headers': {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        'body': json.dumps(response_data)
    }
