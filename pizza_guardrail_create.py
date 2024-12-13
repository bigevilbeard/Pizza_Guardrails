import boto3
import json
from datetime import datetime

def create_pii_guardrail(bedrock_client, name, description):
    # Define the guardrail configuration
    guardrail_config = {
        "name": name,
        "description": description,
        "blockedInputMessaging": "This input contains sensitive personal information and cannot be processed.",
        "blockedOutputsMessaging": "This response contains sensitive information and has been blocked.",
        
        # Configure PII filtering
        "sensitiveInformationPolicyConfig": {
            "piiEntitiesConfig": [
                {
                    "type": "EMAIL",
                    "action": "ANONYMIZE"
                },
                {
                    "type": "PHONE",
                    "action": "ANONYMIZE"
                },
                {
                    "type": "CREDIT_DEBIT_CARD_NUMBER",
                    "action": "ANONYMIZE"
                },
                {
                    "type": "US_SOCIAL_SECURITY_NUMBER",
                    "action": "ANONYMIZE"
                },
                {
                    "type": "ADDRESS",
                    "action": "ANONYMIZE"
                }
            ],
            "regexesConfig": [
                {
                    "name": "CustomEmailPattern",
                    "description": "Custom pattern to catch email addresses",
                    "pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
                    "action": "ANONYMIZE"
                }
            ]
        },
        
        # Add content filtering for additional protection
        "contentPolicyConfig": {
            "filtersConfig": [
                {
                    "inputStrength": "HIGH",
                    "outputStrength": "HIGH",
                    "type": "MISCONDUCT"
                }
            ]
        },
        
        # Add word filtering if needed
        "wordPolicyConfig": {
            "wordsConfig": [
                {
                    "text": "ssn"
                },
                {
                    "text": "social security"
                }
            ]
        }
    }
    
    try:
        # Create the guardrail
        response = bedrock_client.create_guardrail(**guardrail_config)
        print("Guardrail created successfully:")
        print(json.dumps(response, indent=2, default=str))
        return response['guardrailId']
    
    except bedrock_client.exceptions.ValidationException as e:
        print(f"Validation error: {str(e)}")
    except bedrock_client.exceptions.AccessDeniedException as e:
        print(f"Access denied: {str(e)}")
    except bedrock_client.exceptions.ConflictException as e:
        print(f"Conflict error: {str(e)}")
    except bedrock_client.exceptions.InternalServerException as e:
        print(f"Internal server error: {str(e)}")
    except bedrock_client.exceptions.ThrottlingException as e:
        print(f"Throttling error: {str(e)}")
    except bedrock_client.exceptions.TooManyTagsException as e:
        print(f"Too many tags error: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    # Initialize the Bedrock client with your specific profile
    bedrock = boto3.Session(profile_name='stuartck-admin')
    
    # Create the bedrock client (not bedrock-runtime)
    bedrock_client = bedrock.client(service_name='bedrock')
    
    # Example usage
    guardrail_name = "PII_Protection_Guardrail"
    guardrail_description = "Guardrail to protect customer PII information"
    
    guardrail_id = create_pii_guardrail(bedrock_client, guardrail_name, guardrail_description)
    
    if guardrail_id:
        print("\nGuardrail configuration completed successfully")

if __name__ == "__main__":
    main()
