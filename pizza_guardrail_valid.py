import json
import os
import boto3
import re
from typing import Dict, Any

class PizzaGuardrail:
    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client
        self.guardrail_id = "b09i3s9v4evb"
        self.guardrail_version = "DRAFT"
        self.required_fields = ['modelInput', 'metadata', 'recordId']
        self.email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.phone_pattern = r'^\+1-\d{3}-\d{3}-\d{4}$'
        self.model_id = "anthropic.claude-v2"

    def apply_guardrail(self, input_data: Dict[str, Any]):
        try:
            # Format the content as a dictionary within a list
            prompt_content = input_data['modelInput']['prompt']
            
            content_dict = {
                "text": {
                    "text": prompt_content,
                    "qualifiers": ["guard_content"]  # Using valid qualifier from the enum set
                }
            }
            
            # Apply the guardrail with content as a list of dictionaries
            response = self.bedrock_client.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.guardrail_version,
                source="INPUT",  # Using valid enum value
                content=[content_dict]
            )
            
            return response
        except Exception as e:
            print(f"Error applying guardrail: {str(e)}")
            return None

    def invoke_model_with_guardrail(self, input_data: Dict[str, Any]):
        try:
            # First apply guardrail
            guardrail_response = self.apply_guardrail(input_data)
            
            if not guardrail_response:
                print("Guardrail check failed")
                return None

            # If guardrail passes, prepare the request for model
            request_body = {
                "prompt": f"\n\nHuman: {input_data['modelInput']['prompt']}\n\nAssistant:",
                "max_tokens_to_sample": input_data['modelInput']['max_tokens_to_sample'],
                "temperature": input_data['modelInput']['temperature'],
                "anthropic_version": "bedrock-2023-05-31"
            }

            # Invoke the model
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            # Parse and return the response
            response_body = json.loads(response['body'].read())
            return response_body

        except Exception as e:
            print(f"Error in model invocation: {str(e)}")
            return None

def main():
    # Initialize AWS session and client
    session = boto3.Session(profile_name=os.getenv('AWS_PROFILE', 'stuartck-admin'))
    bedrock_runtime = session.client('bedrock-runtime')

    # Test input data
    test_input = {
        "modelInput": {
            "prompt": "Analyze customer feedback for pizza order. Customer says: Too salty for my taste. Pizza type: Supreme. Rating: 3.4",
            "max_tokens_to_sample": 300,
            "temperature": 0.7
        },
        "metadata": {
            "customer_id": "C100",
            "feedback": "Too salty for my taste",
            "pizza_type": "Supreme",
            "rating": 3.4,
            "contact": {
                "name": "Emily Brown",
                "email": "michael.sample@example.com",
                "phone": "+1-555-456-1234"
            }
        },
        "recordId": "100"
    }

    # Create guardrail instance
    guardrail = PizzaGuardrail(bedrock_runtime)

    print("Applying guardrail and invoking model...")
    
    # Apply guardrail and invoke model
    response = guardrail.invoke_model_with_guardrail(test_input)
    
    if response:
        print("\nGuardrail check passed and model response received:")
        print(json.dumps(response, indent=2))
    else:
        print("\n❌ Process failed - check the error messages above.")

if __name__ == "__main__":
    main()
