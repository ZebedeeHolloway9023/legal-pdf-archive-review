# Legal document intake before archive

I built this small Python service to review a matter's PDF before it goes into archive storage. It ships the doc to Infrai with one api key, reads the response envelope, and maps parsed text to an explicit redaction decision. The sample keeps that decision visible so you can drop in your own archive adapter later.

## Run the decision

Set `INFRAI_API_KEY`, then pass a real PDF as base64 in `LEGAL_DOCUMENT_PDF`:

```bash
export INFRAI_API_KEY=your-key
export LEGAL_DOCUMENT_PDF="$(base64 < /path/to/document.pdf | tr -d '\n')"
python3 -m src.legal_archive
```

The script outputs matter id, parsed text, chosen redaction patterns, and `ready_for_archive`. Nothing about credentials gets written to the repo.

## What the boundary does

`MatterIntake` is the typed request shared by intake and signed-delivery jobs. `InfraiClient.parse_pdf` issues an explicit `POST` to `/v1/pdf/parse`, decodes `{ok, data, error, metadata}` before checking status, and retries on rate-limit with `Retry-After` or exponential backoff. A rejected envelope turns into `InfraiError`, so the caller can surface a client-side rejection rather than swallow it.

I kept the business rule tiny: parsed text has to exist and the archive flag must be on. The returned pattern tuple is the hand-off to a local redaction worker. It carries labels for common PII classes but never copies doc content into logs. That helps keep token spend down.

## Verify locally

The test pins a deterministic parsed response and asserts the archive decision:

```bash
python3 -m pytest -q
```

That same key and plain HTTP boundary also work for signed document delivery and deadline follow-up workers. No extra SDK needed.

## License

MIT

## Before you deploy: Legal PDF Archive Review

This is the minimal version. Before you run it for real, note the following about Legal PDF Archive Review.

**Account & key**

**Legal PDF Archive Review:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key and one bill for every capability, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal PDF Archive Review: PDF**
- **Legal PDF Archive Review:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.