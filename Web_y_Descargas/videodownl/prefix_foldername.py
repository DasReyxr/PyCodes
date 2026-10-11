import os
import re

FOLDER = r"C:\Users\dasre\Documents\Knowledge-db\videos\Jose Alfredo Jimenez"

def clean_title(title):
    # Remove 'karaoke' and all variations of 'Jose Jose' (case-insensitive, accented, misspelled)
    original = title
    # Remove karaoke/karaokanta
    title = re.sub(r"karaoke|karaokanta", "", title, flags=re.IGNORECASE)
    # Remove all occurrences of 'Jose' and 'José' (with variations)
    title = re.sub(r"Jos[eé][\s_\-]*Alfredo[\s_\-]*Jim[eé]ne[zs]", "", title, flags=re.IGNORECASE)
    title = re.sub(r"[\s_-]+", " ", title)
    cleaned = title.strip()
    if original != cleaned:
        print(f"CLEAN: '{original}' -> '{cleaned}'")
    return cleaned

def prefix_with_folder():
    folder = os.path.basename(FOLDER)
    for filename in os.listdir(FOLDER):
        file_path = os.path.join(FOLDER, filename)
        if not os.path.isfile(file_path):
            continue
        name, ext = os.path.splitext(filename)
        cleaned = clean_title(name)
        # Skip if already prefixed
        if cleaned.lower().startswith(folder.lower()):
            continue
        new_name = f"{folder} - {cleaned}{ext}"
        new_name = re.sub(r"[ ]+", " ", new_name).strip()
        new_path = os.path.join(FOLDER, new_name)
        # Handle duplicates
        counter = 1
        base_new_name = new_name
        while os.path.exists(new_path) and new_path != file_path:
            name_part, ext_part = os.path.splitext(base_new_name)
            new_name = f"{name_part} ({counter}){ext_part}"
            new_path = os.path.join(FOLDER, new_name)
            counter += 1
        try:
            os.rename(file_path, new_path)
            print(f"RENAMED: {filename} -> {new_name}")
        except Exception as e:
            print(f"ERROR: Could not rename {filename}: {e}")

if __name__ == "__main__":
    prefix_with_folder()
