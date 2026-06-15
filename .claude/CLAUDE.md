# Instructions globales Claude Code

## Proposition proactive de skills

À chaque nouvelle session ou quand l'utilisateur commence une nouvelle tâche :

1. **Analyse le projet courant** (fichiers présents : package.json, pyproject.toml, Dockerfile, etc.)
2. **Propose les skills les plus pertinents** avec leur utilité concrète
3. **Rappelle les skills utiles** quand la conversation change de sujet (ex: si on passe du code à la sécurité, propose `/security-pen-testing`)

### Format de suggestion
Quand tu proposes des skills, utilise ce format concis :
```
💡 Skills utiles pour cette tâche :
- `/nom-skill` — Ce qu'il fait concrètement
```

### Règle principale
**Ne jamais commencer à travailler sur une tâche sans d'abord vérifier si un skill installé peut améliorer le résultat.** Si un skill pertinent existe, mentionne-le avant de commencer.

### Exemples de déclencheurs
- Utilisateur parle de tests → proposer `/tdd-guide`, `/senior-qa`
- Utilisateur parle de sécurité → proposer `/security-pen-testing`, `/senior-secops`
- Utilisateur parle d'architecture → proposer `/senior-architect`, `/database-schema-designer`
- Utilisateur parle de déploiement → proposer `/senior-devops`, `/docker-development`, `/terraform-patterns`
- Utilisateur parle de performances → proposer `/performance-profiler`, `/llm-cost-optimizer`
- Utilisateur parle de marketing/SEO → proposer `/seo-audit`, `/content-strategist`, `/marketing-strategy-pmm`
- Utilisateur parle de conformité → proposer `/gdpr-dsgvo-expert`, `/soc2-compliance`, `/compliance-os`
- Utilisateur parle de LLM/IA → proposer `/rag-architect`, `/claude-api`, `/llm-cost-optimizer`
- Utilisateur parle de base de données → proposer `/sql-database-assistant`, `/database-schema-designer`
- Utilisateur parle de revue de code → proposer `/code-reviewer`, `/karpathy-coder`
