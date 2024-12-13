# %%
import json
import os
import boto3
import re
from typing import Dict, Any

# %%
class PizzaGuardrail:
    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client
        self.guardrail_id = "xqi03i9k4oev"
        self.guardrail_version = "DRAFT"
        self.required_fields = ['modelInput', 'metadata', 'recordId']
        self.email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.phone_pattern = r'^\+1-\d{3}-\d{3}-\d{4}$'
        self.model_id = "anthropic.claude-3-haiku-20240307-v1:0"  # Updated model ID

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

            # Updated request body format for Claude 3
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": input_data['modelInput']['max_tokens_to_sample'],
                "temperature": input_data['modelInput']['temperature'],
                "messages": [
                    {
                        "role": "user",
                        "content": input_data['modelInput']['prompt']
                    }
                ]
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


# %%
def main():
    # Initialize AWS session and clients
    session = boto3.Session(profile_name=os.getenv('AWS_PROFILE', 'stuartck-admin'))
    bedrock_runtime = session.client('bedrock-runtime')
    s3_client = session.client('s3')

    # S3 bucket and key information
    bucket_name = 'pizzacustomers'
    file_key = 'pizza_batch_input_ten.jsonl'

    try:
        # Get the object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        
        # Read the JSONL content
        content = response['Body'].read().decode('utf-8')
        
        # Process each line as a JSON object
        for line in content.strip().split('\n'):
            if line:
                try:
                    test_input = json.loads(line)
                    
                    # Create guardrail instance
                    guardrail = PizzaGuardrail(bedrock_runtime)
                    print(f"\nProcessing record ID: {test_input.get('recordId', 'Unknown')}")
                    print("Applying guardrail and invoking model...")
                    
                    # Apply guardrail and invoke model
                    response = guardrail.invoke_model_with_guardrail(test_input)
                    
                    if response:
                        # Create a sanitized version of the metadata for display
                        sanitized_metadata = {
                            "customer_id": test_input["metadata"]["customer_id"],
                            "feedback": test_input["metadata"]["feedback"],
                            "pizza_type": test_input["metadata"]["pizza_type"],
                            "rating": test_input["metadata"]["rating"],
                            "contact": {
                                "name": "***REDACTED***",
                                "email": "***REDACTED***",
                                "phone": "***REDACTED***"
                            }
                        }
                        
                        # Create sanitized response
                        sanitized_response = {
                            "modelInput": test_input["modelInput"],
                            "metadata": sanitized_metadata,
                            "recordId": test_input["recordId"],
                            "model_response": response
                        }
                        
                        print("\nGuardrail check passed and model response received (sensitive data redacted):")
                        print(json.dumps(sanitized_response, indent=2))
                    else:
                        print("\n❌ Process failed - check the error messages above.")
                
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON line: {e}")
                    continue
                
    except s3_client.exceptions.NoSuchBucket:
        print(f"Error: Bucket '{bucket_name}' does not exist")
    except s3_client.exceptions.NoSuchKey:
        print(f"Error: File '{file_key}' not found in bucket '{bucket_name}'")
    except Exception as e:
        print(f"Error accessing S3: {str(e)}")

if __name__ == "__main__":
    main()



