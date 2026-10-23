# 🏗️ Architecture Technique - Protection des Objets Connectés Médicaux

```mermaid
flowchart TD
    subgraph Capteurs["🩺 Capteurs Médicaux IoMT (Ressources Contraintes)"]
        OX["Oxymètre de pouls (SpO2)"]
        ECG["Moniteur Cardiaque ECG"]
        PUMP["Pompe à Insuline Connectée"]
        TEMP["Thermomètre Médical"]
    end

    subgraph EdgeGateway["🛡️ IoMT Edge Security Gateway"]
        direction TB
        AUTH["Vérification mTLS & Certificats X.509"]
        REGISTRY["Contrôle d'accès & Registre d'Équipements (MDR)"]
        CRYPTO["Validation HMAC-SHA256 & Protection Anti-Rejeu"]
        PHYSIO["Filtre de Plausibilité Physiologique"]
    end

    subgraph AIEngine["🤖 Variante IA - Moteur d'Anomalies"]
        FREEZE["Détecteur de Gel de Signal (Freeze Attack)"]
        GRADIENT["Détecteur de Sauts Anormaux (Gradient Jump)"]
        ISOFOREST["Analyse Multi-variée / Profilage Sain"]
    end

    subgraph Hospital["🏥 Système Hospitalier & Dossier Patient"]
        STORAGE["Stockage Chiffré & Audit Trail"]
        CLINICAL["Poste de Surveillance Médicale"]
        QUARANTINE["Zone d'Isolation / Kill Switch Capteur"]
    end

    Capteurs -->|Trame Chiffrée ChaCha20/HMAC| AUTH
    AUTH --> REGISTRY
    REGISTRY --> CRYPTO
    CRYPTO --> PHYSIO
    PHYSIO --> AIEngine

    AIEngine -->|Trame Saine| STORAGE
    STORAGE --> CLINICAL
    AIEngine -->|Anomalie Détectée| QUARANTINE
```

---

## 🔒 Principes d'Ingénierie Sécurité

1. **Zero Trust Architecture (ZTA) :** Aucun dispositif n'est considéré de confiance par défaut, même situé au sein du réseau local de l'établissement de santé.
2. **Cryptographie adaptée aux contraintes matérielles :** Utilisation de ChaCha20-Poly1305 pour éviter la surcharge processeur et l'épuisement de batterie.
3. **Quarantaine automatisée :** Tout capteur présentant un comportement de signal aberrant est automatiquement isolé pour protéger le patient.
