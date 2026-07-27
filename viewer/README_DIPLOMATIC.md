# Éditeur de transcription diplomatique

`viewer/diplomatic_editor.html` — saisie manuelle d'un gold **diplomatique** pour le
benchmark HTR Sieyès, en remplacement du gold éditorial actuel
(`Bench_HTR/gold_sol_terra_luna.csv`), jugé non exploitable par le
`DIAGNOSTIC.md` du run `sol_terra_luna_20260726_1020` : c'est une mise au propre
(résumé, orthographe modernisée, abréviations résolues silencieusement), de sorte
que le CER mesure un écart éditorial et non la qualité HTR.

L'éditeur est distinct de `htr_viewer.html` (comparateur en lecture seule), qui
n'est pas modifié.

## Lancer

```bash
cd /mnt/d/Projets/533yes
python viewer/build_diplomatic_data.py   # (re)génère viewer/diplomatic_pages.json
python server.py                          # port 8000
```

→ http://localhost:8000/viewer/diplomatic_editor.html

Aucune dépendance réseau : pas de CDN, tout est inline. Les images sont servies
par `server.py` (`/images/...` pour 533yes, `/bench/...` pour le dépôt voisin
`Bench_HTR`, où vivent les images de la famille `etudiant_contemporain`).

## Règle de préchargement

`build_diplomatic_data.py` précharge, pour chaque page, **le premier modèle
exploitable dans l'ordre sol > terra > luna**. Un texte est « exploitable » s'il
est non vide, fait au moins 120 caractères, et n'est pas dégénéré (aucune ligne
identique n'occupe ≥ 55 % des lignes non vides). Sinon la page est préchargée
**vide**.

Justification :

- `luna` n'est jamais préféré : il part en boucle de `[illisible]` sur les pages
  difficiles (jusqu'à 195 046 caractères sur une page) — cf. `DIAGNOSTIC.md`.
- Le filtre anti-dégénérescence est nécessaire au-delà de luna : sur ce run,
  `terra` ne produit lui aussi que des boucles de `[illisible]` sur les pages
  Sieyès.
- Le **gold éditorial n'est jamais préchargé** : le précharger reviendrait à
  reconduire le biais qu'on cherche justement à éliminer. Il reste consultable et
  chargeable à la demande via le sélecteur de source.

État réel du corpus sur le run courant : **3 pages sur 14** de la famille
`sieyes_xviii` ont un préchargement (sol) ; les 11 autres sont vides faute de
sortie modèle exploitable. Les 3 pages `etudiant_contemporain` ont sol/terra.
La saisie manuelle reste donc l'essentiel du travail sur Sieyès.

Le sélecteur de l'en-tête permet de basculer à tout moment entre `auto`, `sol`,
`terra`, `luna`, `gold éditorial` et `vide`. Un chargement de source demande
confirmation si la page contient déjà du texte, et « Annuler chargement »
restaure la saisie précédente.

## Sauvegarde (deux mécanismes indépendants)

1. **Locale, automatique et continue** — chaque frappe est enregistrée dans
   `localStorage` (clé `diplomatic_editor_v1`, écriture débattue à 400 ms, plus
   à chaque changement de page, au masquage de l'onglet et avant fermeture). Au
   chargement, l'éditeur propose de reprendre la session trouvée.
2. **Explicite, sur disque ou en téléchargement** —
   « Sauver sur disque » (`Ctrl+S`) poste vers `POST /api/save-gold` et écrit
   `viewer/gold_diplomatique.csv` (UTF-8, colonnes `item_name,gold_text,family,image_path`,
   directement consommable par le harnais Bench_HTR) ; la version précédente est
   copiée en `.bak` horodaté. « Exporter CSV » télécharge le même contenu depuis
   le navigateur — filet de sécurité qui fonctionne serveur éteint.

« Importer CSV » permet de repartir d'un CSV existant (reprise sur une autre
machine, récupération après purge du navigateur).

## Conventions de saisie proposées

Facultatives, mais à conserver telles quelles pour rester comparable d'une page à
l'autre. Boutons et raccourcis :

| Convention | Sens | Raccourci |
|---|---|---|
| `M[onsieu]r` | résolution d'abréviation | `Alt+A` |
| `mot[?]` | lecture incertaine | `Alt+I` |
| `†` | mot illisible | `Alt+L` |
| `[illisible]` | passage illisible | bouton |
| `⟨…⟩` | ajout interlinéaire ou marginal | `Alt+J` |
| `⟦…⟧` | passage biffé | `Alt+S` |
| `[lacune]` | support détérioré | bouton |
| `⁅⁆` | changement de main ou de colonne | bouton |

Autres raccourcis : `Ctrl+Alt+←/→` (page précédente/suivante), `Ctrl+S`
(sauver sur disque). Image : molette = zoom, glisser = déplacement,
double-clic = zoom ×2, boutons `Ajuster` / `100 %`. Le séparateur central
redimensionne les deux panneaux.

## Ensuite

Une fois la saisie terminée, copier `viewer/gold_diplomatique.csv` vers
`Bench_HTR/` (par ex. `gold_sol_terra_luna_diplomatique.csv`) et relancer
`run_sol_terra_luna.sh`.
