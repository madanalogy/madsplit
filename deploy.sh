#!/bin/bash

source .env
gcloud functions deploy webhook --runtime python310 --trigger-http --set-env-vars "BOT_TOKEN=${BOT_TOKEN}"