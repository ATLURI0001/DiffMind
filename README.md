<br />

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://your-org.dev/images/diffmind/logo-dark.png" width="330">
  <source media="(prefers-color-scheme: light)" srcset="https://your-org.dev/images/diffmind/logo-light.png" width="330">
  <img src="https://your-org.dev/images/diffmind/logo-light.png" alt="logo" width="330">
</picture>
<br>
An Open-Source AI PR Reviewer
<br><br>
<a href="https://github.com/your-org/DiffMind/commits/main">
<img alt="GitHub" src="https://img.shields.io/github/last-commit/your-org/DiffMind/main?style=for-the-badge" height="20">
</a>
</div>

---

This repository contains the open-source DiffMind project.

DiffMind is an open-source, AI-powered code review agent that helps teams ship better pull requests faster. It plugs into your existing Git workflow and gives you automated, context-aware reviews without locking you into any single vendor.

## Sponsors

DiffMind is a community-maintained open-source project. If you'd like to support the project, consider [becoming a sponsor](https://github.com/sponsors/your-org).

## Table of Contents

- [Getting Started](#getting-started)
- [Why Use DiffMind?](#why-use-diffmind)
- [Features](#features)
- [See It in Action](#see-it-in-action)
- [How It Works](#how-it-works)
- [Data Privacy](#data-privacy)
- [Contributing](#contributing)

## Getting Started

> [!NOTE]
> **Docker Hub namespace.** Images are published under [`your-org/diffmind`](https://hub.docker.com/r/your-org/diffmind). Update any pinned `image:` / `docker pull` / `uses: docker://` references when upgrading.

### 🚀 Quick Start for DiffMind

#### 1. GitHub Action (Recommended)

Add automated PR reviews to your repository with a simple workflow file:

```yaml
# .github/workflows/diffmind.yml
name: DiffMind
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  diffmind_job:
    runs-on: ubuntu-latest
    steps:
    - name: DiffMind action step
      uses: your-org/DiffMind@main
      env:
        OPENAI_KEY: ${{ secrets.OPENAI_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
[Full GitHub Action setup guide](https://docs.diffmind.dev/installation/github/#run-as-a-github-action)

#### 2. CLI Usage (Local Development)

Run DiffMind locally on your repository:

```bash
pip install diffmind
export OPENAI_KEY=your_key_here
diffmind --pr_url https://github.com/owner/repo/pull/123 review
```
[Complete CLI setup guide](https://docs.diffmind.dev/usage-guide/automations_and_usage/#local-repo-cli)

#### 3. Other Platforms

- [GitLab webhook setup](https://docs.diffmind.dev/installation/gitlab/)
- [BitBucket app installation](https://docs.diffmind.dev/installation/bitbucket/)
- [Azure DevOps setup](https://docs.diffmind.dev/installation/azure/)

## News and Updates

Full notes for every release are on the [Releases page](https://github.com/your-org/DiffMind/releases).

## Why Use DiffMind?

### 🎯 Built for Real Development Teams

**Fast & Affordable**: Each tool (`/review`, `/improve`, `/ask`) uses a single LLM call (~30 seconds, low cost)

**Handles Any PR Size**: Our PR compression strategy effectively processes both small and large PRs

**Highly Customizable**: JSON-based prompting allows easy customization of review categories and behavior via configuration files (`diffmind/settings/configuration.toml`)

**Platform Agnostic**:
- **Git Providers**: GitHub, GitLab, BitBucket, Azure DevOps, Gitea
- **Deployment**: CLI, GitHub Actions, Docker, self-hosted, webhooks
- **AI Models**: OpenAI GPT, Anthropic Claude, Google Gemini, DeepSeek, Mistral, and any other model reachable through LiteLLM (Azure OpenAI, AWS Bedrock, Vertex AI, Databricks, OpenRouter, Ollama, and more) — see [Changing a model](https://docs.diffmind.dev/usage-guide/changing_a_model/)

**Open Source Benefits**:
- Full control over your data and infrastructure
- Customize prompts and behavior for your team's needs
- No vendor lock-in
- Community-driven development

## Features

<div style="text-align:left;">

See the current feature and git-provider support matrix in the DiffMind documentation.

___

## See It in Action

</div>

<h4><a href="https://github.com/your-org/DiffMind/pull/1">/describe</a></h4>
<div align="center">
<p float="center">
<img src="https://your-org.dev/images/diffmind/describe_new_short_main.png" width="512">
</p>
</div>
<hr>

<h4><a href="https://github.com/your-org/DiffMind/pull/1#issuecomment-1">/review</a></h4>
<div align="center">
<p float="center">
<kbd>
<img src="https://your-org.dev/images/diffmind/review_new_short_main.png" width="512">
</kbd>
</p>
</div>
<hr>

<h4><a href="https://github.com/your-org/DiffMind/pull/1#issuecomment-2">/improve</a></h4>
<div align="center">
<p float="center">
<kbd>
<img src="https://your-org.dev/images/diffmind/improve_new_short_main.png" width="512">
</kbd>
</p>
</div>

<hr>

### Usage Examples

DiffMind tools run as a comment on a PR or from the CLI. A few common ones:

```bash
# Comment on a PR (GitHub/GitLab/Bitbucket/…):
/describe
/review
/improve
/ask "What does this PR change?" # free-text Q&A about the PR

# Issue-scoped commands run on an issue instead of a PR:
/similar_issue # find similar issues in the repository

# Or locally via the CLI:
diffmind --pr_url <PR_URL> review
diffmind --issue_url <ISSUE_URL> similar_issue
```

See the Tools docs for the full list of tools with example commands, and each tool's page for screenshots and options.

<hr>

## How It Works

The following diagram illustrates DiffMind tools and their flow:

![DiffMind Tools](https://your-org.dev/images/diffmind/diagram-v0.1.png)

## Data Privacy

### Self-hosted DiffMind

- If you host DiffMind with your own OpenAI API key, data handling is between you and OpenAI. You can read their API data privacy policy here:
https://openai.com/enterprise-privacy

## Contributing

To contribute to the project, get started by reading our [Contributing Guide](https://github.com/your-org/DiffMind/blob/main/CONTRIBUTING.md).

For local verification, run `PYTHONPATH=. uv run pytest` from the repository root; it discovers the unit-test suite under `tests/unittest` by default. End-to-end tests under `tests/e2e_tests` require provider credentials and should be invoked explicitly, for example `PYTHONPATH=. uv run pytest tests/e2e_tests/test_github_app.py`.

## ❤️ Community

DiffMind is community-owned and open for contributions and additional maintainers. If you'd like to get involved, open an issue or a PR!
