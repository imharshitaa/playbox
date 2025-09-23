IAM/policy documents — JSON/YAML policy blobs, wildcard principals, staged changes.
Example: {"Effect":"Allow","Action":"*","Resource":"*"}

Signed URLs / presigned tokens — valid, expired, tampered querystring signature.

Metadata requests — HTTP requests to metadata endpoints (e.g., 169.254.169.254/...).

Resource names / ARNs — different encodings, traversal-style names, overly long names.

Cloud config files — Terraform, CloudFormation, ARM templates (valid/invalid).

CLI commands & flags — simulate CLI inputs with unexpected flags, environment vars.

Storage objects — object names with special chars, nested keys, different ACL headers.

Kubernetes manifests — Pod spec YAMLs (privileged true/false, hostPath mounts, env secrets).
