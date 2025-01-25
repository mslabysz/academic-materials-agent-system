from youtube_transcript_api import YouTubeTranscriptApi
import openai
from datetime import datetime
import os
from openai import OpenAI

from utils import get_file_paths

def get_youtube_transcript(url: str) -> tuple[str, str]:
    """
    Zwraca krotkę (transkrypcja, ścieżka_do_pliku).
    """
    print(f"\n[YouTube Transcription] Rozpoczynam pobieranie transkrypcji z URL: {url}")
    try:
        # Wydobywamy ID wideo
        video_id = None
        if "youtu.be" in url:
            video_id = url.split("/")[-1].split("?")[0]
        elif "youtube.com" in url:
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "embed/" in url:
                video_id = url.split("embed/")[1].split("?")[0]

        if not video_id:
            raise ValueError("Nie udało się wyodrębnić ID wideo z adresu URL.")
        
        print(f"[YouTube Transcription] Znaleziono ID wideo: {video_id}")

        # Pobieramy transkrypcję
        try:
            print("[YouTube Transcription] Próba bezpośredniego pobrania transkrypcji...")
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([entry['text'] for entry in transcript_list])
        except Exception as e:
            print(f"[YouTube Transcription] Bezpośrednie pobranie transkrypcji nie powiodło się, próba z listą języków...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                print("[YouTube Transcription] Szukam transkrypcji w języku angielskim...")
                transcript = transcript_list.find_transcript(['en'])
            except:
                print("[YouTube Transcription] Nie znaleziono transkrypcji angielskiej, próba innych języków...")
                try:
                    print("[YouTube Transcription] Szukam ręcznie utworzonych transkrypcji...")
                    transcript = transcript_list.find_manually_created_transcript(['en', 'pl', 'de', 'fr', 'ja'])
                except:
                    print("[YouTube Transcription] Brak ręcznie utworzonych transkrypcji, próba wygenerowanych...")
                    try:
                        transcript = transcript_list.find_generated_transcript(['en', 'pl', 'de', 'fr', 'ja'])
                    except:
                        raise Exception("Brak dostępnych transkrypcji dla tego wideo")
            
            transcript_data = transcript.fetch()
            if transcript.language_code != 'en':
                print(f"[YouTube Transcription] Tłumaczenie transkrypcji z {transcript.language_code} na en...")
                transcript_data = transcript.translate('en').fetch()
            full_text = " ".join([entry['text'] for entry in transcript_data])
        
        print("[YouTube Transcription] Pomyślnie pobrano transkrypcję")
        print(f"[YouTube Transcription] Długość transkrypcji: {len(full_text)} znaków")
        
        # Zapis transkrypcji do pliku
        full_path, filename = get_file_paths(full_text, f"transcript_yt_{video_id}", ".txt")
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        print(f"[YouTube Transcription] Zapisano transkrypcję do pliku: {filename}")
        return full_text, full_path

    except Exception as e:
        print(f"[YouTube Transcription] BŁĄD: {str(e)}")
        raise Exception(f"Error getting YouTube transcript: {str(e)}")


def get_audio_transcript(file_path: str) -> tuple[str, str]:
    """
    Zwraca krotkę (transkrypcja, ścieżka_do_pliku).
    W tym przykładzie zakładamy użycie OpenAI Whisper API.
    """
    print(f"\n[Audio Transcription] Rozpoczynam transkrypcję pliku: {file_path}")
    try:
        client = OpenAI()
        
        print("[Audio Transcription] Wysyłam plik do API Whisper...")
        with open(file_path, "rb") as af:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=af
            )

        full_text = transcript.text
        print("[Audio Transcription] Pomyślnie otrzymano transkrypcję")
        print(f"[Audio Transcription] Długość transkrypcji: {len(full_text)} znaków")

        # Zapis transkrypcji do pliku
        full_path, filename = get_file_paths(full_text, "transcript_audio", ".txt")
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(full_text)
            
        print(f"[Audio Transcription] Zapisano transkrypcję do pliku: {filename}")
        return full_text, full_path

    except Exception as e:
        print(f"[Audio Transcription] BŁĄD: {str(e)}")
        raise Exception(f"Error transcribing audio file: {str(e)}")
