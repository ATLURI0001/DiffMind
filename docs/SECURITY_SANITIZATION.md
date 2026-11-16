# Security & Prompt Injection Sanitization Guidelines

## Threat Model
Untrusted input in Pull Request titles, descriptions, and inline comments may attempt adversarial jailbreaks or instructions intended to subvert automated code review checks.

## Defense Principles
1. **Delimited Envelope**: All untrusted text is placed inside unambiguous XML boundary tags (`<untrusted_pr_diff>`).
2. **System Prompt Hardening**: System instructions explicitly instruct models to never execute commands embedded within user code or comments.
3. **Invisible Character Stripping**: Bidi controls (e.g. LTR/RTL overrides) and zero-width characters are sanitized prior to tokenization.
