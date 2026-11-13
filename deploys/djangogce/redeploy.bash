#!/usr/bin/env bash
set -o errexit -o nounset -o pipefail

for attempt in {1..30}; do
    if gcloud compute ssh "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --quiet \
        --tunnel-through-iap --command='true'; then
        break
    fi
    [[ $attempt -lt 30 ]] || exit 1
    sleep 10
done
gcloud compute ssh "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --quiet \
    --tunnel-through-iap --command='sudo cloud-init status --wait &&
        sudo systemctl restart django-deploy.service &&
        sudo systemctl is-active django-web django-worker django-beat nginx'
