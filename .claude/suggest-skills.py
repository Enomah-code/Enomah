#!/usr/bin/env python3
"""
Analyse le projet courant et suggère les skills les plus pertinents.
S'exécute au démarrage de chaque session Claude Code.
"""

import os
import json
import sys

SKILLS_DIR = os.path.expanduser("~/.claude/skills")

# Mapping projet → skills pertinents avec justification
PROJECT_SKILL_MAP = {
    # Détection par fichiers
    "package.json": [
        ("senior-frontend", "Développement React/Next.js/TypeScript"),
        ("senior-fullstack", "Architecture fullstack JavaScript"),
        ("senior-qa", "Tests Jest/Playwright/Vitest"),
        ("performance-profiler", "Optimisation des performances JS/Node.js"),
        ("tdd-guide", "Développement piloté par les tests"),
        ("dependency-auditor", "Audit des dépendances npm"),
    ],
    "next.config.js": [
        ("senior-frontend", "Expert React/Next.js"),
        ("saas-scaffolder", "Scaffolding SaaS Next.js avec auth et paiements"),
        ("landing-page-generator", "Génération de landing pages Next.js/React"),
        ("stripe-integration-expert", "Intégration des paiements Stripe"),
    ],
    "pyproject.toml": [
        ("senior-backend", "APIs Python/FastAPI/Django"),
        ("senior-data-scientist", "Data science et ML"),
        ("senior-ml-engineer", "MLOps et déploiement de modèles"),
        ("rag-architect", "Architecture RAG pour LLMs"),
        ("tdd-guide", "Tests Pytest"),
    ],
    "requirements.txt": [
        ("senior-backend", "Backend Python"),
        ("senior-data-engineer", "Pipelines de données Python"),
        ("docker-development", "Conteneurisation Python"),
    ],
    "Dockerfile": [
        ("docker-development", "Optimisation des Dockerfiles et docker-compose"),
        ("senior-devops", "CI/CD et infrastructure"),
        ("kubernetes-operator", "Déploiement Kubernetes"),
    ],
    "docker-compose.yml": [
        ("docker-development", "Orchestration multi-conteneurs"),
        ("senior-devops", "Infrastructure DevOps"),
    ],
    "terraform": [
        ("terraform-patterns", "Infrastructure as Code Terraform"),
        ("aws-solution-architect", "Architecture AWS"),
        ("senior-devops", "DevOps et infrastructure cloud"),
    ],
    "k8s": [
        ("kubernetes-operator", "Opérateurs Kubernetes"),
        ("helm-chart-builder", "Charts Helm"),
        ("senior-devops", "DevOps Kubernetes"),
    ],
    ".github/workflows": [
        ("senior-devops", "Pipelines CI/CD GitHub Actions"),
        ("ci-cd-pipeline-builder", "Construction de pipelines CI/CD"),
    ],
    "go.mod": [
        ("senior-backend", "APIs et services Go"),
        ("senior-devops", "Infrastructure Go"),
    ],
    "Cargo.toml": [
        ("senior-backend", "Développement Rust"),
        ("senior-architect", "Architecture système Rust"),
    ],
    "pom.xml": [
        ("senior-backend", "Applications Java/Spring"),
        ("senior-qa", "Tests JUnit"),
    ],
    "stripe": [
        ("stripe-integration-expert", "Intégration Stripe et gestion des paiements"),
    ],
    "prisma": [
        ("sql-database-assistant", "Base de données avec Prisma ORM"),
        ("database-schema-designer", "Conception de schéma de base de données"),
    ],
    "drizzle": [
        ("sql-database-assistant", "Base de données avec Drizzle ORM"),
        ("database-schema-designer", "Conception de schéma de base de données"),
    ],
}

# Skills toujours utiles quel que soit le projet
UNIVERSAL_SKILLS = [
    ("code-reviewer", "Revue de code automatisée et détection de bugs"),
    ("security-pen-testing", "Audit de sécurité OWASP et vulnérabilités"),
    ("git-worktree-manager", "Développement parallèle avec git worktrees"),
    ("senior-architect", "Décisions d'architecture et ADR"),
]

def detect_project_type(project_dir):
    """Détecte le type de projet en analysant les fichiers présents."""
    detected = {}

    for indicator, skills in PROJECT_SKILL_MAP.items():
        # Vérifier si c'est un fichier direct
        if os.path.exists(os.path.join(project_dir, indicator)):
            detected[indicator] = skills
        # Vérifier les dossiers
        elif os.path.isdir(os.path.join(project_dir, indicator)):
            detected[indicator] = skills
        # Vérifier dans les sous-dossiers (ex: k8s/, terraform/)
        else:
            for root, dirs, files in os.walk(project_dir):
                # Limiter la profondeur
                depth = root.replace(project_dir, '').count(os.sep)
                if depth > 2:
                    break
                if indicator in dirs or indicator in files:
                    detected[indicator] = skills
                    break
                # Vérifier les fichiers contenant le mot-clé
                for f in files:
                    if indicator in f.lower():
                        detected[indicator] = skills
                        break

    return detected

def get_package_json_skills(project_dir):
    """Analyse package.json pour des suggestions plus précises."""
    pkg_path = os.path.join(project_dir, "package.json")
    if not os.path.exists(pkg_path):
        return []

    try:
        with open(pkg_path) as f:
            pkg = json.load(f)

        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        extra_skills = []

        if "stripe" in deps:
            extra_skills.append(("stripe-integration-expert", "Intégration Stripe détectée dans package.json"))
        if "prisma" in deps or "@prisma/client" in deps:
            extra_skills.append(("sql-database-assistant", "Prisma ORM détecté"))
            extra_skills.append(("database-schema-designer", "Conception de schéma Prisma"))
        if "drizzle-orm" in deps:
            extra_skills.append(("sql-database-assistant", "Drizzle ORM détecté"))
        if "playwright" in deps or "@playwright/test" in deps:
            extra_skills.append(("pw", "Playwright détecté — tests E2E"))
            extra_skills.append(("webapp-testing", "Tests d'applications web avec Playwright"))
        if "openai" in deps or "@anthropic-ai/sdk" in deps or "anthropic" in deps:
            extra_skills.append(("rag-architect", "Intégration LLM détectée — architecture RAG"))
            extra_skills.append(("llm-cost-optimizer", "Optimisation des coûts LLM"))
            extra_skills.append(("claude-api", "Référence API Claude/Anthropic"))
        if "next" in deps:
            extra_skills.append(("saas-scaffolder", "Next.js détecté — scaffolding SaaS"))
        if any(k in deps for k in ["tailwindcss", "@tailwindcss/forms"]):
            extra_skills.append(("frontend-design", "Tailwind CSS — conseils design frontend"))

        return extra_skills
    except Exception:
        return []

def get_python_skills(project_dir):
    """Analyse les fichiers Python pour des suggestions précises."""
    extra = []
    try:
        for fname in ["requirements.txt", "pyproject.toml"]:
            fpath = os.path.join(project_dir, fname)
            if os.path.exists(fpath):
                content = open(fpath).read().lower()
                if "fastapi" in content or "django" in content or "flask" in content:
                    extra.append(("senior-backend", "Framework web Python détecté"))
                if "anthropic" in content or "openai" in content or "langchain" in content:
                    extra.append(("rag-architect", "LLM Python détecté — architecture RAG"))
                    extra.append(("claude-api", "Référence API Claude/Anthropic"))
                if "pandas" in content or "numpy" in content or "scikit" in content:
                    extra.append(("senior-data-scientist", "Stack data science détectée"))
                if "mlflow" in content or "torch" in content or "tensorflow" in content:
                    extra.append(("senior-ml-engineer", "Stack ML/MLOps détectée"))
                if "snowflake" in content:
                    extra.append(("snowflake-development", "Snowflake détecté"))
    except Exception:
        pass
    return extra

def skill_exists(name):
    """Vérifie que le skill est bien installé."""
    return os.path.isdir(os.path.join(SKILLS_DIR, name))

def format_output(suggested_skills, project_dir):
    """Formate la sortie pour Claude."""
    project_name = os.path.basename(project_dir)

    lines = [
        f"## 🎯 Skills recommandés pour le projet `{project_name}`",
        "",
        "Voici les skills les plus adaptés à ce projet. Utilise-les avec `/nom-du-skill` :\n",
    ]

    seen = set()
    categories = {}

    for skill_name, reason in suggested_skills:
        if skill_name in seen:
            continue
        if not skill_exists(skill_name):
            continue
        seen.add(skill_name)

        # Catégoriser
        if any(x in skill_name for x in ["senior-", "engineer", "architect", "devops", "docker", "kubernetes", "terraform", "ci-cd", "tdd", "qa", "database", "sql", "rag"]):
            cat = "🔧 Engineering & Infrastructure"
        elif any(x in skill_name for x in ["security", "pen-test", "vulnerability", "secops"]):
            cat = "🔒 Sécurité"
        elif any(x in skill_name for x in ["saas", "stripe", "landing", "cro", "marketing", "seo"]):
            cat = "🚀 Produit & Croissance"
        elif any(x in skill_name for x in ["code-review", "karpathy", "tech-debt", "dependency", "git"]):
            cat = "✅ Qualité & Maintenance"
        else:
            cat = "⚡ Utilitaires"

        if cat not in categories:
            categories[cat] = []
        categories[cat].append((skill_name, reason))

    for cat, skills in categories.items():
        lines.append(f"### {cat}")
        for skill_name, reason in skills:
            lines.append(f"- **`/{skill_name}`** — {reason}")
        lines.append("")

    lines.append("---")
    lines.append("💡 *Tape `/nom-du-skill` pour activer un skill à tout moment de la conversation.*")

    return "\n".join(lines)

def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    if not os.path.isdir(project_dir):
        project_dir = os.getcwd()

    # Détecter le type de projet
    detected = detect_project_type(project_dir)

    # Collecter les skills suggérés
    suggested = []
    for indicator, skills in detected.items():
        for skill in skills:
            suggested.append(skill)

    # Suggestions précises depuis package.json
    suggested.extend(get_package_json_skills(project_dir))

    # Suggestions précises depuis Python
    suggested.extend(get_python_skills(project_dir))

    # Ajouter les skills universels
    suggested.extend(UNIVERSAL_SKILLS)

    # Dédupliquer tout en préservant l'ordre
    seen = set()
    unique = []
    for item in suggested:
        if item[0] not in seen:
            seen.add(item[0])
            unique.append(item)

    # Limiter à 15 suggestions max
    unique = unique[:15]

    if unique:
        print(format_output(unique, project_dir))

if __name__ == "__main__":
    main()
