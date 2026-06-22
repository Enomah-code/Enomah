# Connecteur Frontend Angeleck OS

Ce dossier fait le lien entre **votre interface existante** et l'API backend
d'Angeleck OS.

## Fichier

- `angeleck-client.js` — client JavaScript sans dépendance (navigateur + Node).

## Intégration

```html
<script src="/path/to/angeleck-client.js"></script>
<script>
  const api = new AngeleckClient("http://localhost:8000/api/v1");

  // Inscription / connexion (le token JWT est stocké automatiquement)
  await api.register("user@mail.com", "motdepasse123", "Mon Nom");
  // ou : await api.login("user@mail.com", "motdepasse123");

  // Envoyer une demande au cerveau central
  const res = await api.chat("Crée une stratégie TikTok pour mon produit");
  console.log(res.response);        // réponse synthétisée
  console.log(res.missions);        // détail par agent
  console.log(res.created_agents);  // agents créés à la volée

  // Autres appels
  const agents = await api.getAgents();
  const memory = await api.getMemory();
  await api.createAgent("Facebook Ads", ["ciblage", "optimisation CPM"]);
  // Upload d'un fichier <input type="file">
  // await api.upload(fileInput.files[0]);
</script>
```

## CORS

Ajoutez l'origine de votre frontend dans `CORS_ORIGINS` (`.env`) :

```
CORS_ORIGINS=["http://localhost:3000","https://mon-app.com"]
```
