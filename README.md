# Dream plugins

The marketplace for Dream's agent plugins. Install from Claude Code or Codex:

```sh
# Claude Code
claude plugin marketplace add dude-with-a-mug/dream-plugins
claude plugin install dream-substrate@dream

# Codex
codex plugin marketplace add dude-with-a-mug/dream-plugins
codex plugin add dream-substrate@dream
```

Plugins in this marketplace:

- **dream-substrate** (`plugins/dream-substrate/`) — connects a code repo to
  the Dream idea it implements: the hosted `dream` MCP server, the
  participation skill, and a SessionStart hook. See its README for the
  connection flow. It ships no credential; the first call signs you in
  through Dream's consent page.

This repository is a published artifact. Its contents are copied from Dream's
source repository by a release workflow on every plugin release, so pull
requests here are not the way to change a plugin. Report problems at
https://dreamluci.com.
