import os
import boto3
import json

def review_code_sagemaker(repo_path, sagemaker_endpoint):
    client = boto3.client('sagemaker-runtime')
    findings = {}

    # Walk through repo files and send each code file to the model
    for subdir, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py') or file.endswith('.js') or file.endswith('.ts') or file.endswith('.java'):  # Add other extensions as needed
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r') as f:
                    file_content = f.read()

                    # Invoke SageMaker endpoint
                    response = client.invoke_endpoint(
                        EndpointName=sagemaker_endpoint,
                        ContentType='application/json',
                        Body=json.dumps({'inputs': file_content})
                    )

                    result = json.loads(response['Body'].read().decode())
                    findings[file_path] = result['generated_text']  # Adjust as per your SageMaker model's output format

    return findings

if __name__ == "__main__":
    repo_path = os.getenv('GITHUB_WORKSPACE')
    sagemaker_endpoint = os.getenv('SAGEMAKER_ENDPOINT')

    results = review_code_sagemaker(repo_path, sagemaker_endpoint)

    # Save the results to a file
    with open('results/review_report.txt', 'w') as f:
        for file, review in results.items():
            f.write(f"File: {file}\n")
            f.write(f"Review: {review}\n\n")

    # Exit with a non-zero status if vulnerabilities are found
    if any('vulnerability' in review.lower() for review in results.values()):
        exit(1)
