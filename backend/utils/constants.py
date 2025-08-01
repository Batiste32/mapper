# Paths
ENV_PATH = "frontend/.env"
DATABASE_PATH = "backend/database/electoral_app.db"
CSV_PATH = "backend/database/profiles.csv"
CACHE_PATH = "backend/cache"
NGROK_CONFIG_PATH = "backend/ngrok_config.yml"
VITE_CONFIG_PATH = "frontend/vite.config.ts"
CONSTANTS_PATH = "backend/utils/constants.py"

# URLs
BASE_URL = "https://31738ea11dc4.ngrok-free.app"
DATABASE_URL = "sqlite:///backend/database/electoral_app.db"
NGROK_API_URL = "http://localhost:4040/api/tunnels"

# Strings
VALID_LEANS = ["extreme gauche", "gauche", "gauche centre", "centre", "centre droite", "droite", "extreme droite", "indeterminee"]
VALID_NATIONALITIES = ["Afghane", "Albanaise", "Algérienne", "Allemande", "Américaine", "Andorrane",
    "Anglaise", "Angolaise", "Argentine", "Arménienne", "Australienne", "Autrichienne",
    "Azerbaïdjanaise", "Bahreïnienne", "Bangladaise", "Barbadienne", "Belge", "Bélizienne",
    "Béninoise", "Bhoutanaise", "Biélorusse", "Birmane", "Bolivienne", "Bosnienne",
    "Botswanaise", "Brésilienne", "Britannique", "Brunéienne", "Bulgare", "Burkinabée",
    "Burundaise", "Cambodgienne", "Camerounaise", "Canadienne", "Cap-Verdienne",
    "Centrafricaine", "Chilienne", "Chinoise", "Chypriote", "Colombienne", "Comorienne",
    "Congolaise", "Costaricienne", "Croate", "Cubaine", "Danoise", "Djiboutienne",
    "Dominicaine", "Dominiquaise", "Écossaise", "Égyptienne", "Émiratie", "Équato-guinéenne",
    "Équatorienne", "Érythréenne", "Espagnole", "Estonienne", "Éthiopienne", "Fidjienne",
    "Finlandaise", "Française", "Gabonaise", "Gambienne", "Georgienne", "Ghanéenne",
    "Grecque", "Grenadienne", "Guatémaltèque", "Guinéenne", "Guinéenne-Bissau", "Guyanienne",
    "Haïtienne", "Hondurienne", "Hongroise", "Indienne", "Indonésienne", "Irakienne",
    "Iranienne", "Irlandaise", "Islandaise", "Israélienne", "Italienne", "Ivoirienne",
    "Jamaïcaine", "Japonaise", "Jordanienne", "Kazakhstanaise", "Kényane", "Kirghize",
    "Kiribatienne", "Koweïtienne", "Laotienne", "Lesothienne", "Lettonne", "Libanaise",
    "Libérienne", "Libyenne", "Liechtensteinoise", "Lituanienne", "Luxembourgeoise",
    "Macédonienne", "Malaisienne", "Malawienne", "Maldivienne", "Malienne", "Maltaise",
    "Marocaine", "Marshallaise", "Mauricienne", "Mauritanienne", "Mexicaine", "Micronésienne",
    "Moldave", "Monegasque", "Mongole", "Monténégrine", "Mozambicaine", "Namibienne",
    "Nauruane", "Népalaise", "Nicaraguayenne", "Nigérienne", "Nigériane", "Nord-Coréenne",
    "Norvégienne", "Néo-Zélandaise", "Omanaise", "Ougandaise", "Ouzbèke", "Pakistanaise",
    "Palaosienne", "Palestinienne", "Panaméenne", "Papouane", "Paraguayenne", "Péruvienne",
    "Philippine", "Polonaise", "Portugaise", "Qatarienne", "Roumaine", "Russe",
    "Rwandaise", "Saint-Lucienne", "Saint-Marinaise", "Saint-Vincentaise", "Salomonaise",
    "Salvadorienne", "Samoane", "Saoudienne", "Sénégalaise", "Serbe", "Seychelloise",
    "Sierra-Léonaise", "Singapourienne", "Slovaque", "Slovène", "Somalienne", "Soudanaise",
    "Sud-Africaine", "Sud-Coréenne", "Sud-Soudanaise", "Suédoise", "Suisse", "Surinamaise",
    "Syrienne", "Tadjike", "Tanzanienne", "Tchadienne", "Tchèque", "Thaïlandaise",
    "Timoraise", "Togolaise", "Tongienne", "Trinidadienne", "Tunisienne", "Turkmène",
    "Turque", "Tuvaluane", "Ukrainienne", "Uruguayenne", "Vanuataise", "Vénézuélienne",
    "Vietnamienne", "Yéménite", "Zambienne", "Zimbabwéenne"]

PARSING_PROMPT = """
Identify the following data to one of the provided values.
Return the data as it is if you can't.
- DO NOT EXPLAIN ANYTHING.
- NO BULLET POINTS, NO HEADERS, NO EXTRA TEXT.
- SEPARATE ENTRIES WITH ;"""

# Tokens
SECRET_KEY = "YOUR_SECRET_KEY"
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImM1MWU3MzZiNjkyYTRhZWJhOWU4NTc3YzNmYmVjMWVlIiwiaCI6Im11cm11cjY0In0="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7