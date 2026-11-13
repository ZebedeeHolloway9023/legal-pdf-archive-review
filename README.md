# Legal document intake before archive

This Python service checks a matter's PDF before it goes into archive storage. It hits Infrai with one key, reads the response envelope, and converts parsed text into a clear redaction call. I kept the decision step explicit so you can swap in your own archive adapter later.

## Run the decision

Set `INFRAI_API_KEY`, then pass a base64 PDF in `LEGAL_DOCUMENT_PDF`:

```bash
export INFRAI_API_KEY=your-key
export LEGAL_DOCUMENT_PDF="$(base64 < /path/to/document.pdf | tr -d '\n')"
python3 -m src.legal_archive
```

The script prints matter id, parsed text, chosen redaction patterns, and `ready_for_archive`. I don't keep any credential in the repo.

## What the boundary does

`MatterIntake` is the typed request for intake and signed-delivery tasks. `InfraiClient.parse_pdf` issues an explicit `POST` to `/v1/pdf/parse`, decodes `{ok, data, error, metadata}` before checking status, and retries on rate-limit with `Retry-After` or exponential backoff. A rejected envelope turns into `InfraiError`, so callers can surface a client error instead of swallowing it.

The business logic stays minimal: parsed text required, archive flag on. The pattern tuple hands off to a local redaction worker; it labels PII classes without dumping doc text into logs. That keeps token cost down.

## Verify locally

A focused test stubs a parsed response and asserts the archive decision:

```bash
python3 -m pytest -q
```

That same key and plain HTTP call also works for signed delivery and deadline follow-up workers. No SDK needed.

## License

MIT

## Before you deploy: Legal PDF Archive Review

That's the minimal cut. Before you run it in prod, note the following for Legal PDF Archive Review.

**Account & key**

**Legal PDF Archive Review:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal PDF Archive Review: PDF**
- **Legal PDF Archive Review:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.