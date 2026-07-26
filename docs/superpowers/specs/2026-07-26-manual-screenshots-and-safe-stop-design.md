# Manual Screenshots and Safe Stop Design

## Goal

Replace the legacy README images with Tom's manually captured, sanitized UI evidence and provide a Windows stop command that only terminates the Resume Growth Coach server started from this checkout.

## Screenshot Contract

The supplied images are accepted as real local UI evidence after visual review: they contain only application chrome, template text, a model name, and fabricated role content. They contain no personal resume, contact detail, recruiting-platform account, or real job-application record.

README assets will be replaced with these names and meanings:

- `docs/images/01-empty-screen.png`: blank local-first analysis form.
- `docs/images/02-analysis-results.png`: score, matching evidence, and model status.
- `docs/images/03-growth-roadmap.png`: roadmap and Portfolio Planner eligibility.
- `docs/images/04-matching-jobs-and-bullets.png`: alternative roles and resume-bullet drafts.

The walkthrough headings and alt text will match those four screens. Obsolete legacy screenshot references are removed. The legacy source PNG files remain as unreferenced tracked history because the local environment rejected file deletion; they are not used by the README. No agent-generated image, crop, or visual reconstruction is permitted.

## Local Server Lifecycle

`Start-ResumeGrowthCoach.cmd` and `Start-ResumeGrowthCoach.ps1` will launch the existing Uvicorn reload process through one common PowerShell launcher. That launcher will write an ignored local PID record containing the root process ID and checkout path only after the HTTP health check succeeds. A small dependency-free Python validator verifies the persisted record metadata before PowerShell evaluates the live Windows process tree.

`Stop-ResumeGrowthCoach.cmd` will call `Stop-ResumeGrowthCoach.ps1`. The stop script will:

1. Read the local PID record.
2. Confirm the recorded process still exists and is a `cmd.exe` ancestor whose command line includes this checkout's absolute Python path and `uvicorn app.main:app`.
3. Confirm a descendant owns the loopback listener on port 8000.
4. Terminate that recorded process tree with `taskkill /PID <pid> /T /F` and remove the PID record.

If any identity check fails, the script will refuse to stop the process and print the check that failed. It will never terminate an arbitrary process merely because it listens on port 8000. A `-WhatIf` option will report the validated target without terminating it.

## Verification

- Unit tests cover PID-record parsing and rejection of mismatched command metadata.
- A Windows smoke starts the app through the common launcher, verifies `/health`, runs `-WhatIf`, stops the process, and confirms port 8000 no longer has the recorded listener.
- README link/image checks ensure every referenced manual screenshot exists and legacy references are gone.
