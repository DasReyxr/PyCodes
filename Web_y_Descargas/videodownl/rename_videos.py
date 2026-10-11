import os
import re
import urllib.parse
import urllib.request
import json
from mutagen.mp4 import MP4

VIDEOS_DIR = "videos"

def clean_title(title):
    """Remove karaoke-related words and clean up the title."""
    # Patterns to remove (case insensitive)
    patterns_to_remove = [
        r'\bkaraoke\b',
        r'\bkaraokanta\b',
        r'\bKARAOKE\b',
        r'\bKaraoke\b',
        r'\(karaoke\)',
        r'\[karaoke\]',
        r'\(KARAOKE\)',
        r'\[KARAOKE\]',
        r'\blyrics?\b',
        r'\bofficial\s*(video|audio)?\b',
        r'\(official\s*(video|audio)?\)',
        r'\[official\s*(video|audio)?\]',
        r'\bhd\b',
        r'\b4k\b',
        r'\bremaster(ed)?\b',
    ]
    
    cleaned = title
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra spaces and dashes
    cleaned = re.sub(r'\s*-\s*-\s*', ' - ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\(\s*\)', '', cleaned)
    cleaned = re.sub(r'\[\s*\]', '', cleaned)
    cleaned = cleaned.strip(' -')
    
    return cleaned

def extract_author_song(title):
    """Try to extract author and song from title."""
    # Common patterns: "Author - Song" or "Song - Author"
    if ' - ' in title:
        parts = title.split(' - ', 1)
        return parts[0].strip(), parts[1].strip()
    return None, title

def get_metadata_artist(filepath):
    """Try to get artist from MP4 metadata."""
    try:
        audio = MP4(filepath)
        if '\xa9ART' in audio:  # Artist tag
            return audio['\xa9ART'][0]
        if 'aART' in audio:  # Album artist
            return audio['aART'][0]
    except Exception:
        pass
    return None

def search_artist_online(song_title):
    """Search for artist using YouTube/web search."""
    try:
        import yt_dlp
        # Search YouTube for the song
        search_query = f"{song_title} song artist"
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch1',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_query, download=False)
            if result and 'entries' in result and result['entries']:
                entry = result['entries'][0]
                title = entry.get('title', '')
                # Try to extract artist from the search result title
                if ' - ' in title:
                    artist = title.split(' - ')[0].strip()
                    # Clean the artist name
                    artist = re.sub(r'\b(karaoke|karaokanta|lyrics|official)\b', '', artist, flags=re.IGNORECASE).strip()
                    if artist and len(artist) > 1:
                        return artist
                # Check channel name as fallback
                channel = entry.get('channel', entry.get('uploader', ''))
                if channel and 'karaoke' not in channel.lower() and 'vevo' not in channel.lower():
                    return None  # Don't use channel name, too unreliable
    except Exception as e:
        print(f"    (Could not search online: {e})")
    return None

def sanitize_filename(name):
    """Remove invalid characters for Windows filenames."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    return name.strip()

def rename_videos():
    """Main function to rename all videos in the folder."""
    if not os.path.exists(VIDEOS_DIR):
        print(f"Directory '{VIDEOS_DIR}' not found!")
        return
    
    files = [f for f in os.listdir(VIDEOS_DIR) if f.endswith(('.mp4', '.mkv', '.webm', '.m4a'))]
    
    if not files:
        print("No video files found!")
        return
    
    print(f"Found {len(files)} video(s) to process...\n")
    
    for filename in files:
        filepath = os.path.join(VIDEOS_DIR, filename)
        name, ext = os.path.splitext(filename)
        
        # Clean the title
        cleaned = clean_title(name)
        
        # Try to extract author and song
        author, song = extract_author_song(cleaned)
        
        author_found_in_name = author is not None
        
        # If no author in filename, try metadata
        if not author:
            author = get_metadata_artist(filepath)
        
        # If still no author, search online
        if not author:
            print(f"    Searching online for artist of '{song}'...")
            author = search_artist_online(song)
        
        # Build new filename
        if author:
            new_name = f"{author} - {song}{ext}"
        else:
            # No author found, prefix with 0author
            new_name = f"0author - {song}{ext}"
        
        new_name = sanitize_filename(new_name)
        new_path = os.path.join(VIDEOS_DIR, new_name)
        
        # Skip if name is the same
        if filename == new_name:
            print(f"SKIP: {filename} (no changes needed)")
            continue
        
        # Handle duplicate names
        counter = 1
        base_new_name = new_name
        while os.path.exists(new_path) and new_path != filepath:
            name_part, ext_part = os.path.splitext(base_new_name)
            new_name = f"{name_part} ({counter}){ext_part}"
            new_path = os.path.join(VIDEOS_DIR, new_name)
            counter += 1
        
        # Rename the file
        try:
            os.rename(filepath, new_path)
            print(f"RENAMED: {filename}")
            print(f"     -> {new_name}\n")
        except Exception as e:
            print(f"ERROR: Could not rename {filename}: {e}\n")

if __name__ == "__main__":
    rename_videos()
