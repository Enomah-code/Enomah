---
name: "pm-skills"
description: "Routeur/index pour les 8 skills de gestion de projet inclus dans ce plugin (boîte à outils quantitative pour PM senior, scrum master, Jira/JQL, Confluence, administration Atlassian, modèles Atlassian, analyseur de réunions, communications d'équipe). Utiliser quand une demande de gestion de projet ne correspond pas clairement à un seul skill et qu'il faut choisir le bon (ex. : \"nos sprints semblent déréglés\", \"auditer nos permissions Jira\"). Inclut une configuration MCP distant Atlassian (.mcp.json) pour un accès en direct à Jira/Confluence."
version: 2.9.0
author: Alireza Rezvani
license: MIT
tags:
  - project-management
  - jira
  - confluence
  - atlassian
  - scrum
  - agile
agents:
  - claude-code
  - codex-cli
  - openclaw
---

# Project Management Skills — Router

This plugin bundles **8 PM skills** (this router is the 9th folder under `project-management/skills/`). Each skill is self-contained. The bundled `.mcp.json` wires the Atlassian Remote MCP (`https://mcp.atlassian.com/v1/sse`, OAuth handled by Claude Code).

## Routing table

Match the request, then load `project-management/skills/<skill>/SKILL.md`. If multiple rows match, ask one clarifying question first.

| Request signals | Skill | Path |
|---|---|---|
| Project health, risk EMV, three-point estimates | senior-pm | `skills/senior-pm/` |
| Sprint velocity, retro analysis, ceremony health | scrum-master | `skills/scrum-master/` |
| JQL queries, Jira workflows, boards | jira-expert | `skills/jira-expert/` |
| Confluence spaces, page structure, content audits | confluence-expert | `skills/confluence-expert/` |
| User/permission/scheme administration | atlassian-admin | `skills/atlassian-admin/` |
| Reusable Confluence/Jira templates | atlassian-templates | `skills/atlassian-templates/` |
| Meeting transcripts, talk-time, action items | meeting-analyzer | `skills/meeting-analyzer/` |
| Status updates, 3P updates, stakeholder comms | team-communications | `skills/team-communications/` |

## Quick start

```bash
# Example: route a sprint-health request
cat project-management/skills/scrum-master/SKILL.md
ls project-management/skills/scrum-master/scripts/
```

## Rules

- Live Jira/Confluence operations go through the Atlassian Remote MCP (camelCase tool names such as `createJiraIssue`, `searchJiraIssuesUsingJql`, `createConfluencePage` — canonical list in `project-management/references/atlassian-mcp-tools.md`). Admin operations are NOT covered by the MCP — use admin.atlassian.com or the REST API per atlassian-admin.
- Route to exactly one skill, then follow that skill's workflow. This router ships no tools of its own.
