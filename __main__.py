import pulumi
import pulumi_aws as aws
import boto3
import logging
import base64

logger = logging.getLogger()

config = pulumi.Config()

key_id = config.get('kms_key_id')

# Define a map of secrets to be created.  
# This could be read from a file or Pulumi Config for a specific stack / environment
secrets_map = {
    "dbPassword": "AQICAHh48ep6TDJBe46IGpKOrl+YBtGz6aT2r7QxqM0Xg+gO3wH5Tuh9MWZ71mfmjqrfphcTAAAAZjBkBgkqhkiG9w0BBwagVzBVAgEAMFAGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMTstJBmCP6BSkYzTvAgEQgCMD/vg4152NRF/pVYtmYtLbde2tMmaJ8QPAZsh7QTzuHSnvVA==",
    "apiKey": "AQICAHh48ep6TDJBe46IGpKOrl+YBtGz6aT2r7QxqM0Xg+gO3wHjZYmZI3/GlHNYGgwqfsaZAAAAZzBlBgkqhkiG9w0BBwagWDBWAgEAMFEGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMYV0ZONyTCE2RAf9mAgEQgCRtA9wXJtmv8bHz/NpWnhUs/IGa+xZLYm6t5sCpvLYGrthEKTg=",
    "configString": "AQICAHh48ep6TDJBe46IGpKOrl+YBtGz6aT2r7QxqM0Xg+gO3wFct+VT0G+Lv7B6AL/P22qZAAAAazBpBgkqhkiG9w0BBwagXDBaAgEAMFUGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMbh897LoV8n2Gyv1eAgEQgCj0I7LeShOxOCQAaQAFuV4i5015t+zdtxiu5IXj1/fil8nmSm7H8H3R",
}

secrets = {}

def decrypt(cipher_text):
    kms_client = boto3.client('kms')

    text = kms_client.decrypt(
        KeyId=key_id, CiphertextBlob=base64.b64decode(cipher_text)
    )["Plaintext"]

    return text.decode()


# Iterate over the map to create secrets and corresponding secret versions.
for key, value in secrets_map.items():

    # # Create the secret
    secret = aws.secretsmanager.Secret(key,
        name=key,
        description=f"Secret for {key}"
    )

    # # Create the secret version
    secret_version = aws.secretsmanager.SecretVersion(f"{key}-version",
        secret_id=secret.id,
        secret_string=decrypt(value),
    )

    secrets[key] = secret_version

# Export the secret ARNs
pulumi.export("secret_arns", [secret.arn for secret in secrets.values()])