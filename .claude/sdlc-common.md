# Shared rules for every SDLC step (read by /sdlc and each /sdlc-* command)

You are the ORCHESTRATOR (main session). Subagents cannot start subagents or talk to the
user, so you delegate with the Task tool, validate, commit, and hand the file onward.

## Before a step
- `git branch --show-current` must be `feature/doc-sync-claude`; otherwise stop and tell me.
- Check the step's input file(s) exist. If one is missing, say which and stop (suggest the
  earlier `/sdlc-*` command).

## After a step
1. Verify the output file exists and has its required sections. If not, re-invoke the
   subagent once naming the missing parts; if still bad, stop and tell me.
2. `git add` the output and `git commit` with a Conventional Commit message.
3. Update `docs/sdlc-state.md`: current step, status, last commit sha, pending gate.
   Commit it with the step.

## Always
- Never invent facts or test results; use only real tool output.
- Never put secrets in any file, commit or PR. Never push to main.
- If an MCP tool is unavailable, tell me and ask me to paste the input instead.
