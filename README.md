# YouTube Digest

A serverless app that monitors a YouTube channel, grabs the transcript of new videos, summarizes them with Amazon Bedrock (Claude), and emails the summary via SNS.

## Architecture

```
EventBridge (schedule) → Lambda → YouTube Data API (latest video)
                                → youtube-transcript-api (transcript)
                                → Bedrock Claude (summary)
                                → SNS → Email
                          SSM Parameter Store (dedup last video ID)
```

## Prerequisites

- **Terraform** >= 1.0 installed
- **Docker** installed and running
- **AWS account** with IAM credentials (access key & secret key)
- **YouTube Data API v3 key** — create one at [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- **Amazon Bedrock** — Claude model access enabled in your AWS account

## Configuration

Set the following in your GitHub repository settings:

**Secrets:**

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS access key ID |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key |
| `YOUTUBE_CHANNEL_ID` | Channel ID to monitor (the `UC...` string from the channel URL) |

**Variables:**

| Variable | Description |
|---|---|
| `EMAIL_ADDRESS` | Email address to receive summaries |

## Deploy

Trigger the workflow manually from the **Actions** tab.

After the first deployment, **check your email and confirm the SNS subscription** — you won't receive summaries until you do.

## How It Works

1. **EventBridge** triggers the Lambda on a schedule (default: daily at 14:00 UTC).
2. Lambda calls the **YouTube Data API** to get the latest video from the channel.
3. It checks **SSM Parameter Store** to see if this video was already processed.
4. If new, it fetches the **transcript** (Turkish) using `youtube-transcript-api`.
5. The transcript is sent to **Amazon Bedrock (Claude Sonnet 4.5)** for summarization in Turkish.
6. The summary is published to an **SNS topic**, which delivers it to your email.
7. The video ID is saved to SSM so it won't be processed again.

## Customization

- **Schedule**: Change the `schedule_expression` variable (default: `cron(0 14 * * ? *)`).
- **Model**: Change the `bedrock_model_id` variable to use a different Bedrock model.
- **Prompt**: Edit `PROMPT_TEMPLATE` in `src/summarizer.py` to adjust the summary style.
- **Transcript language**: Edit the `languages` parameter in `src/transcript.py`.

## Destroy

```bash
cd terraform
terraform destroy \
  -var="youtube_api_key=x" \
  -var="youtube_channel_id=x" \
  -var="email_address=x"
```
