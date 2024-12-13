# Pizza Customer Feedback Analysis System

This project provides a system for generating simulated pizza customer feedback data and analyzing it using a machine learning model with guardrails.

## Repository Structure

- `create_jsonl_file.py`: Generates simulated customer feedback data in JSONL format.
- `pizza_guardrail_create.py` or `pizza_guardrail_create.ipynb`: Implements a guardrail system for validating input data before invoking a machine learning model.
- `pizza_guardrail_valid.py`or `pizza_guardrail_vaild.ipynb`: Validates guardrail system for checking PII details are redated.

## Usage Instructions

### Installation

1. Ensure you have Python 3.6+ installed.
2. Clone this repository:
   ```
   git clone <repository_url>
   cd <repository_name>
   ```
3. Install the required dependencies:
   ```
   pip install boto3
   ```

### Generating Simulated Data

To generate simulated customer feedback data:

1. Run the `create_jsonl_file.py` script:
   ```
   python create_jsonl_file.py
   ```
2. This will create a file named `claude_batch_input.jsonl` containing 10 simulated customer feedback entries.

### Analyzing Feedback with Guardrails

To analyze the feedback using the machine learning model with guardrails:

1. Ensure you have AWS credentials configured with access to Amazon Bedrock.
2. Set the `AWS_PROFILE` environment variable if needed:
   ```
   export AWS_PROFILE=your-profile-name
   ```
3. Run the `pizza_guardrail_create.py` script or `pizza_guardrail_create.ipynb`
   ```
   python pizza_guardrail_create.py
   ```
4.  Run the `pizza_guardrail_valid.py` script `pizza_guardrail_valid.ipynb`
   ```
   python pizza_guardrail_valid.py
   ```

This script will:
- Apply a guardrail to validate the input data
- If the guardrail check passes, invoke the machine learning model
- Display the model's response

### Configuration

The `PizzaGuardrail` class in `pizza_guardrail_valid.py` can be configured with the following parameters:
- `guardrail_id`: The ID of the guardrail to use
- `guardrail_version`: The version of the guardrail (default is "DRAFT")
- `model_id`: The ID of the machine learning model to use (default is "anthropic.claude-v2")

### Troubleshooting

Common issues and solutions:

1. AWS Credentials Not Found
   - Error: "botocore.exceptions.NoCredentialsError: Unable to locate credentials"
   - Solution: Ensure your AWS credentials are properly configured in `~/.aws/credentials` or set as environment variables.

2. Guardrail Check Failing
   - Error: "Guardrail check failed"
   - Solution: 
     1. Check the input data format in `pizza_guardrail_valid.py`
     2. Ensure all required fields are present
     3. Verify that the guardrail ID and version are correct

3. Model Invocation Error
   - Error: "Error in model invocation: An error occurred (ThrottlingException) when calling the InvokeModel operation"
   - Solution: 
     1. Check your AWS account limits for Bedrock API calls
     2. Implement exponential backoff and retry logic

For debugging:
- Enable verbose logging in boto3:
  ```python
  import boto3
  boto3.set_stream_logger('')
  ```
- Check AWS CloudTrail logs for detailed API call information

## Data Flow

The data flow in this application follows these steps:

1. Simulated customer feedback data is generated using `create_jsonl_file.py`
2. The generated data is saved in JSONL format
3. `pizza_guardrail_create.py`builds the Guardrail based on PII data
4. `pizza_guardrail_valid.py` reads the input data
5. The guardrail is applied to validate the input
6. If validation passes, the data is sent to the machine learning model
7. The model processes the data and returns an analysis
. The analysis is displayed to the user

```
[Generate Data] -> [JSONL File] -> [Apply Guardrail] ->  [Invoke Model] -> [Validate Input] -> [Process Data] -> [Display Results]
```

Note: Ensure that the input data format matches the expected structure for both the guardrail and the machine learning model.
