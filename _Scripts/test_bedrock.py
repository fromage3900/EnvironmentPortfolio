import boto3
from botocore.config import Config

client = boto3.client('bedrock-runtime', region_name='us-east-1', config=Config(retries={'max_attempts': 5, 'mode': 'adaptive'}, read_timeout=60))
resp = client.converse(modelId='us.anthropic.claude-haiku-4-5-20251001-v1:0', messages=[{'role': 'user', 'content': [{'text': 'Hello'}]}], system=[{'text': 'You are a helpful assistant.'}], inferenceConfig={'maxTokens': 100, 'temperature': 0.2})
print('Response:', resp['output']['message']['content'][0]['text'])
print('Usage:', resp.get('usage'))