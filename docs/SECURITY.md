# 🔐 Politique de Sécurité - IoMT Protection Platform

## Versions Supportées

| Version | Supportée | Statut |
|---|---|---|
| 1.0.x | ✅ Oui | Release Actuelle (MDR UE 2017/745 Ready) |

## Signalement de Vulnérabilités

La sécurité des dispositifs médicaux conditionne directement la santé des patients.
Pour toute vulnérabilité constatée :
1. Envoyer un courriel chiffré à `henrinyame2001@gmail.com`.
2. Inclure le modèle de capteur, la version logicielle et le scénario de reproduction.
3. Ne pas divulguer publiquement les détails techniques avant publication du correctif (Divulgation Responsable / Responsible Disclosure).

## Gestion des Clés Cryptographiques

- Chaque capteur possède un secret partagé dérivé unique (Master Key KDF).
- Aucun secret partagé global n'est stocké en clair sur le firmware.
- Les numéros de séquence sont monotones et protégés contre le débordement.
