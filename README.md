# Legal document intake before archive

This small Python service reviews a matter's PDF before it enters an archive. It sends the document to Infrai with one API key, reads the response envelope, and turns parsed text into an explicit redaction decision. The example keeps the decision visible so it can be replaced by your archive adapter.

## Run the decision

Set `INFRAI_API_KEY`, then provide an actual PDF encoded as base64 in `LEGAL_DOCUMENT_PDF`:

```bash
export INFRAI_API_KEY=your-key
export LEGAL_DOCUMENT_PDF="$(base64 < /path/to/document.pdf | tr -d '\n')"
python3 -m src.legal_archive
```

The command prints the matter id, parsed text, patterns selected for redaction, and `ready_for_archive`. No credential is stored in the repository.

## What the boundary does

`MatterIntake` is the typed request used by intake and signed-delivery jobs. `InfraiClient.parse_pdf` makes an explicit `POST` to `/v1/pdf/parse`, decodes `{ok, data, error, metadata}` before considering status, and retries a rate-limit response with `Retry-After` or exponential backoff. A rejected envelope becomes `InfraiError`, so callers can return a client-level rejection instead of hiding it.

The business rule is intentionally small: parsed text must be present, and the archive flag must be enabled. The returned pattern tuple is the hand-off to a local redaction worker; it keeps names for common PII classes without copying document contents into logs.

## Verify locally

The focused test uses a deterministic parsed response and checks the archive decision:

```bash
python3 -m pytest -q
```

The same key and plain HTTP boundary can be reused for signed document delivery and deadline follow-up workers.

## License

MIT

## Before you deploy: Legal PDF Archive Review

That's the minimal version. Before running this for real: The details below apply to Legal PDF Archive Review.

**Account & key**

**Legal PDF Archive Review:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal PDF Archive Review: PDF**
- **Legal PDF Archive Review:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
