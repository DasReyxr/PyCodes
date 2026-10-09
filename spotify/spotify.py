import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 1. Configura tus credenciales de Spotify Developer
CLIENT_ID = "2e5a20f16193421c8a3cff58bec9aefb"
CLIENT_SECRET = "b04509932cf24903a64e6d8fd1356558"
REDIRECT_URI = "http://127.0.0.1:8000/callback"

# 2. Autenticación con permisos para leer tus canciones guardadas ("likes")
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read"
))

print("🔍 Buscando artistas en tus canciones guardadas (Likes)...\n")

artistas_likes = set() # Usamos un conjunto para no duplicar nombres
resultados = sp.current_user_saved_tracks(limit=50)

# 3. Bucle para recorrer TODOS tus likes (paginación de Spotify)
while resultados:
    for item in resultados['items']:
        cancion = item['track']
        # Extraer los nombres de los artistas de cada canción guardada
        for artista in cancion['artists']:
            artistas_likes.add(artista['name'])
            
    # Pasar a la siguiente página de tus likes
    if resultados['next']:
        resultados = sp.next(resultados)
    else:
        break


# 3. Guardar la lista en un archivo de texto ordenado alfabéticamente
nombre_archivo = "mis_artistas_spotify.txt"
with open(nombre_archivo, "w", encoding="utf-8") as f:
    f.write(f"✨ ¡Encontrados {len(artistas_likes)} artistas únicos en tus likes!\n\n")
    for artista in sorted(artistas_likes):
        f.write(f"- {artista}\n")

print(f"✅ ¡Listo! La lista de artistas se ha guardado en '{nombre_archivo}'")