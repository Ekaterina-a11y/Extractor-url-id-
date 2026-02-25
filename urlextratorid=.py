import sys
from urllib.parse import urlparse, unquote
import re

# Vérifie qu'un fichier est passé en argument
if len(sys.argv) < 2:
    print("Usage: python extractor-url.py <fichier_urls>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = "urls_avec_id.txt"

# Ensemble pour éliminer automatiquement les doublons
urls_uniques = set()

# Domaines à exclure
domaines_exclus = {"free.fr", "google"}

# Patterns SQL injection à supprimer
patterns_sql = [
    r"AND\d+=\d+",
    r"ANDMySQL_Error=MySQL_Error",
    r"OR\d+=\d+", 
    r"UNION SELECT",
    r"SELECT.*FROM",
    r"INSERT INTO",
    r"DROP TABLE",
    r"';--",
    r"' OR '1'='1"
]

# Lecture du fichier d'entrée
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        url = line.strip()
        if not url:
            continue
        
        # Vérifier si l'URL contient "id="
        if "id=" in url:
            parsed = urlparse(url)
            if parsed.netloc:
                # Vérifier si le domaine contient un des motifs à exclure
                exclure = any(dom_exclu in parsed.netloc for dom_exclu in domaines_exclus)
                
                if not exclure:
                    # Décoder les caractères URL-encoded comme %27
                    url_decodee = unquote(url)
                    
                    # Nettoyer les patterns SQL injection
                    url_propre = url_decodee
                    for pattern in patterns_sql:
                        url_propre = re.sub(pattern, '', url_propre, flags=re.IGNORECASE)
                    
                    # Nettoyer les doubles slash et autres artefacts
                    url_propre = re.sub(r'//+', '/', url_propre)
                    url_propre = re.sub(r'&+', '&', url_propre)
                    url_propre = re.sub(r'[?&]$', '', url_propre)
                    
                    urls_uniques.add(url_propre.strip())

# Trier d'abord par domaine, puis par URL complète
def cle_tri(url):
    parsed = urlparse(url)
    return (parsed.netloc, url)

# Écriture du fichier de sortie trié
with open(output_file, "w", encoding="utf-8") as f:
    for url in sorted(urls_uniques, key=cle_tri):
        f.write(url + "\n")

print(f"{len(urls_uniques)} URLs uniques avec 'id=' nettoyées et triées dans {output_file}")

# Afficher les domaines trouvés pour vérification
domaines_trouves = set(urlparse(url).netloc for url in urls_uniques)
print(f"Domaines trouvés ({len(domaines_trouves)}): {sorted(domaines_trouves)}")