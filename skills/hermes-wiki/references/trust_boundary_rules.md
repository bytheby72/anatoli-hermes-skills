# Trust Boundary Rules

## Risk Classes

- LOW: read-only, no network, no secrets
- MEDIUM: file write OR network call, no secrets
- HIGH: reads confidential paths AND has network/API call
- CRITICAL: reads secret-looking paths AND can send data externally
- SECRET_OR_UNKNOWN: touches secret files or unknown risk

## Network Call Indicators

- `requests.get/post/put/delete`
- `urllib.request`
- `http.client`
- `httpx`
- `aiohttp`
- `curl`
- `wget`
- `fetch`
- `socket.connect`
- `subprocess.*curl`
- `subprocess.*wget`

## File Read Indicators

- `open(` with read mode
- `read_file(`
- `Path.read_text`
- `Path.read_bytes`
- `json.load`
- `yaml.safe_load`
- `csv.reader`
- `pandas.read_*`

## File Write Indicators

- `open(` with write/append mode
- `write_file(`
- `Path.write_text`
- `Path.write_bytes`
- `json.dump`
- `yaml.dump`
- `shutil.copy/move`
- `os.rename`

## External Service Indicators

- `google`
- `gmail`
- `drive`
- `telegram`
- `discord`
- `slack`
- `openrouter`
- `openai`
- `anthropic`
- `cloudflare`
- `aws`
- `azure`
- `gcp`

## System Modification Indicators

- `systemctl`
- `crontab`
- `cron`
- `service`
- `update-rc.d`
- `chkconfig`
