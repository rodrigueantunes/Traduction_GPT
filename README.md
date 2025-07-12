# 🗂️ Traducteur Excel FR ➔ Multi-Langues industriel avec OpenAI

**Auteur : Antunes Informatique**

Application moderne pour Windows (Tkinter) permettant de traduire en masse des fichiers Excel (XLSX) du français vers plusieurs langues industrielles, avec gestion de l’API OpenAI, estimation des coûts, log détaillé, et interface graphique ergonomique.
Idéal pour la localisation de contenus techniques, catalogues ou documents industriels.

---

## 📥 Fonctionnalités principales

* **Traduction automatique** de colonnes Excel via OpenAI (GPT-4o, GPT-4, O3, etc).
* **Gestion multi-langues** (anglais, espagnol, italien, portugais, chinois, japonais, arabe, russe…).
* **Respect strict** des variables du type `%1`, `%2`, etc.
* **Interface graphique moderne** (Tkinter + ttk).
* **Gestion des clés API OpenAI** (multi-profils, ajout/suppression/sélection).
* **Estimation automatique du coût** OpenAI selon le modèle choisi et la taille du fichier.
* **Auto-save** et **log détaillé** des traductions.
* **Support des modèles récents** : GPT-4o, GPT-4-turbo, GPT-3.5-turbo, O3, etc.
* **Compatibilité multiplateforme** (Windows, Linux, Mac OS).
* **Exemple de fichier modèle fourni**.

---

## 📸 Aperçu

![Aperçu de l'interface](doc/preview.png)
*(À personnaliser avec une capture d’écran de votre interface si besoin)*

---

## 🚀 Installation

1. **Cloner ce dépôt ou télécharger le ZIP**
2. **Installer les dépendances :**

```bash
pip install openai pandas openpyxl
```

* *Tkinter est inclus dans la plupart des distributions Python standard.*
* *Pour Linux, il peut être nécessaire d’installer le paquet `python3-tk`.*

3. **Placer le fichier `modele_traduction.xlsx` dans le dossier de l’application** (ou utiliser le bouton "Modèle Exemple" dans l’interface).

---

## ⚙️ Utilisation

1. **Lancer l’application :**

```bash
python traducteur_excel_openai.py
```

2. **Charger un fichier XLSX** à traduire (le fichier doit contenir une colonne `fr`).
3. **Choisir la langue cible** parmi les options disponibles.
4. **Sélectionner ou renseigner votre clé API OpenAI** via le menu dédié (gestion multi-clés possible).
5. **Choisir le modèle OpenAI** (par défaut GPT-4o, le plus économique et rapide).
6. **Vérifier le coût estimé** avant de lancer la traduction.
7. **Cliquer sur "Traduire tout le fichier"** et patienter.
   *L’auto-save sécurise votre avancement toutes les 10 lignes, et un log détaillé est généré.*
8. **Sauvegarder le résultat** (au format XLSX ou CSV).

---

## 🗂️ Structure du fichier Excel attendu

* **Colonne obligatoire** : `fr` (textes en français à traduire)
* **Colonnes facultatives** : une colonne par langue (`en`, `es`, `it`, etc.), `statut`
* Les variables `%1`, `%2`, etc. doivent être présentes dans le texte source et seront conservées à l’identique.

*Exemple de modèle fourni :* `modele_traduction.xlsx`

---

## 💡 Astuces & Conseils

* **API OpenAI :**
  Créez une clé API sur [platform.openai.com](https://platform.openai.com/api-keys) puis ajoutez-la dans l’application (sécurisé et non partagé).
* **Coût :**
  Les prix sont estimés en fonction du nombre de tokens consommés par modèle ([voir la grille tarifaire OpenAI](https://openai.com/pricing)).
* **Log et sauvegarde automatique :**
  Un fichier `_traduction_log.txt` et une version temporaire du fichier XLSX sont générés à chaque session.
* **Multi-utilisateurs/équipes :**
  Utilisez le gestionnaire de clés API pour basculer rapidement entre plusieurs profils ou comptes OpenAI.

---

## 🛠️ Personnalisation / Développement

* **Ajouter une nouvelle langue**
  Modifier le dictionnaire `LANGUAGES` en début de script.
* **Ajouter un nouveau modèle**
  Compléter le dictionnaire `MODEL_PRICING`.
* **Adapter la logique du prompt**
  Personnaliser la variable `PROMPT_TEMPLATE`.

---

## ❓ FAQ

* **Q : Mon fichier n’est pas reconnu ?**

  > Vérifiez qu’il contient bien une colonne nommée `fr`.
* **Q : Pourquoi ai-je des erreurs "API Key invalide" ?**

  > Assurez-vous que la clé commence par `sk-` et n’a pas expiré sur la plateforme OpenAI.
* **Q : Comment annuler ou corriger une traduction ?**

  > Il suffit de relancer la traduction après modification du fichier source. Les cellules déjà traduites peuvent être écrasées.

---

## 🛡️ Sécurité & Confidentialité

* **Les clés API** sont stockées localement dans un fichier `openai_keys.json`, non partagé ni exporté.
* **Aucune donnée** n’est transmise en dehors des appels nécessaires à l’API OpenAI (pas d’analytics, pas de tracking).
* **Log** uniquement local, sans stockage externe.

---

## 📦 Distribution & Licence

* Projet distribué **librement** pour un usage professionnel ou personnel.
* **Licence :** MIT (à adapter selon vos besoins)
* **Aucune affiliation** avec OpenAI.

---

## 📧 Support & Contact

Pour toute question, suggestion ou bug, ouvrez une *Issue* sur Github ou contactez :

> [rodrigue.antunes@gmail.com](mailto:rodrigue.antunes@gmail.com)

---

## 👏 Remerciements

* **OpenAI** pour l’API et les modèles GPT.
* **Tkinter / pandas / openpyxl** pour la base technique.
* **Tous les utilisateurs & testeurs** pour leurs retours.

---

*Antunes Informatique – Faites parler vos fichiers Excel, dans toutes les langues de l’industrie !*

---

### ⬇️ Exemple d’appel (script) pour développeurs

```python
# Pour usage en script, voir la fonction call_openai(prompt, apikey, model)
# ou adaptez la logique selon vos besoins.
```

---

**N’hésitez pas à contribuer, suggérer ou partager !**

---

> **Un fichier `modele_traduction.xlsx` est fourni à titre d’exemple dans le dépôt.**

