"""Constants for the Frankfurter integration."""

from datetime import timedelta

DOMAIN = "frankfurter"

DEFAULT_NAME = "Frankfurter"
DEFAULT_SCAN_INTERVAL = timedelta(hours=24)

API_PATH_CURRENCIES = "https://api.frankfurter.dev/v2/currencies"
API_PATH_RATE = "https://api.frankfurter.dev/v2/rate/{base}/{target}"
