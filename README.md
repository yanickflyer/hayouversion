# hayouversion

Get Verse of the Day from YouVersion for Home Assistant.

## Overview

This repository contains a custom Home Assistant integration named `youversion` that fetches the YouVersion Verse of the Day and exposes it as a sensor.

The integration uses the YouVersion API:
- `GET https://api.youversion.com/v1/verse_of_the_days/{day}` to resolve the daily passage ID
- `GET https://api.youversion.com/v1/bibles/{bible_id}/passages/{passage_id}?format=text` to fetch the passage text

## Installation

1. Copy the `custom_components/YouVersion` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from Home Assistant's Integrations UI.

## Configuration

During setup you must provide:
- `api_key` — your YouVersion API key or bearer token
- `bible_id` — optional Bible version ID (default: `1`)

The integration tries common YouVersion auth headers:
- `Authorization: Bearer <token>`
- `x-yvp-app-key: <key>`
- `X-YouVersion-Developer-Token: <key>`

## Sensor entity

The integration creates one sensor entity:
- `sensor.youversion_verse_of_the_day`

Attributes provided:
- `reference` — human-readable Bible reference
- `passage_id` — Bible passage identifier, e.g. `JHN.3.16`
- `day` — day of year value used for the verse

## Notes

- If the default `bible_id` does not return the expected passage text, update the integration configuration with a Bible ID from the YouVersion API.
- The integration currently uses the YouVersion `verse_of_the_days` endpoints and resolves a passage through the `bibles/{bible_id}/passages` endpoint.

## Troubleshooting

- If setup fails, verify your API key and the header type your YouVersion app requires.
- Check Home Assistant logs for `youversion` errors.

