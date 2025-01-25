import os
from datetime import datetime

def get_file_paths(content: str, base_filename: str, extension: str = ".txt") -> tuple[str, str]:
    """
    Zwraca ścieżkę (full_path) i samą nazwę pliku (filename) dla zapisu kontentu.
    W tym przykładzie plik zapisywany jest do katalogu 'outputs'.
    Możesz rozbudować to wedle potrzeb (np. uwzględniając user_id lub inny podkatalog).
    """
    # Upewnij się, że istnieje folder 'outputs'
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}{extension}"
    full_path = os.path.join(output_dir, filename)

    return full_path, filename
