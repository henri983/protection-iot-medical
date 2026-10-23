# Changelog

Toutes les modifications notables apportées à ce projet sont consignées dans ce document.
Format conforme à [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/) et [SemVer 2.0.0](https://semver.org/).

## [1.0.0] - 2026-10-23
### Ajouté
- Moteur cryptographique basse consommation (ChaCha20-Poly1305 et HMAC-SHA256).
- Protection anti-rejeu et validation d'horodatage des trames télémétriques.
- Registre d'inventaire d'équipements médicaux avec fonctions de mise en quarantaine et révocation immédiate (Kill Switch).
- Filtre de validation physiologique multi-paramétrique (SpO2, FC, glycémie, température).
- **Variante IA :** Moteur d'inférence temps réel pour la détection des attaques par gel de signal (Freeze Attack) et de variations impossibles (Gradient Jumps).
- API REST FastAPI pour l'Edge Gateway et le monitoring des équipements.
- 24 tests automatisés (Unitaires, Sécurité, IA, Intégration).
- Documentation complète d'analyse des vulnérabilités IoMT (MDR UE 2017/745).
