"""
Streamware Language Manager
Multi-language support for text, TTS, and STT with runtime switching
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger("streamware.language")


@dataclass
class LanguageConfig:
    """Language configuration"""
    code: str  # ISO 639-1 code (pl, en, de, etc.)
    name: str
    native_name: str
    tts_voice: str  # Voice ID for TTS
    stt_model: str  # Model for STT
    enabled: bool = True


class LanguageManager:
    """
    Manages multi-language support with runtime switching
    Supports: text translations, TTS voices, STT models
    """
    
    # Supported languages with TTS/STT config
    LANGUAGES = {
        "pl": LanguageConfig(
            code="pl",
            name="Polish",
            native_name="Polski",
            tts_voice="pl-PL-Standard-A",
            stt_model="pl-PL",
            enabled=True
        ),
        "en": LanguageConfig(
            code="en",
            name="English",
            native_name="English",
            tts_voice="en-US-Standard-A",
            stt_model="en-US",
            enabled=True
        ),
        "de": LanguageConfig(
            code="de",
            name="German",
            native_name="Deutsch",
            tts_voice="de-DE-Standard-A",
            stt_model="de-DE",
            enabled=True
        ),
        "fr": LanguageConfig(
            code="fr",
            name="French",
            native_name="Français",
            tts_voice="fr-FR-Standard-A",
            stt_model="fr-FR",
            enabled=True
        ),
        "es": LanguageConfig(
            code="es",
            name="Spanish",
            native_name="Español",
            tts_voice="es-ES-Standard-A",
            stt_model="es-ES",
            enabled=True
        ),
        "uk": LanguageConfig(
            code="uk",
            name="Ukrainian",
            native_name="Українська",
            tts_voice="uk-UA-Standard-A",
            stt_model="uk-UA",
            enabled=True
        ),
        "ru": LanguageConfig(
            code="ru",
            name="Russian",
            native_name="Русский",
            tts_voice="ru-RU-Standard-A",
            stt_model="ru-RU",
            enabled=True
        ),
    }
    
    # UI Translations
    TRANSLATIONS = {
        "pl": {
            "welcome": "Cześć! Jestem Twoim asystentem. Powiedz co chcesz zrobić.",
            "help": "Wyświetlam dostępne komendy.",
            "not_understood": "Nie rozumiem polecenia. Powiedz 'pomoc' aby zobaczyć komendy.",
            "error": "Wystąpił błąd.",
            "success": "Gotowe!",
            "loading": "Ładowanie...",
            "settings": "Ustawienia",
            "language": "Język",
            "voice": "Głos",
            "quick_actions": "Szybkie akcje",
            "send": "Wyślij",
            "listening": "Słucham...",
            "speaking": "Mówię...",
            "connected": "Połączono",
            "disconnected": "Rozłączono",
            "weather": "Pogoda",
            "documents": "Dokumenty",
            "cameras": "Kamery",
            "sales": "Sprzedaż",
            "home": "Dom",
            "analytics": "Analityka",
            "system": "System",
        },
        "en": {
            "welcome": "Hi! I'm your assistant. Tell me what you want to do.",
            "help": "Showing available commands.",
            "not_understood": "I don't understand. Say 'help' to see commands.",
            "error": "An error occurred.",
            "success": "Done!",
            "loading": "Loading...",
            "settings": "Settings",
            "language": "Language",
            "voice": "Voice",
            "quick_actions": "Quick actions",
            "send": "Send",
            "listening": "Listening...",
            "speaking": "Speaking...",
            "connected": "Connected",
            "disconnected": "Disconnected",
            "weather": "Weather",
            "documents": "Documents",
            "cameras": "Cameras",
            "sales": "Sales",
            "home": "Home",
            "analytics": "Analytics",
            "system": "System",
        },
        "de": {
            "welcome": "Hallo! Ich bin Ihr Assistent. Sagen Sie mir, was Sie tun möchten.",
            "help": "Verfügbare Befehle werden angezeigt.",
            "not_understood": "Ich verstehe nicht. Sagen Sie 'Hilfe' für Befehle.",
            "error": "Ein Fehler ist aufgetreten.",
            "success": "Fertig!",
            "loading": "Laden...",
            "settings": "Einstellungen",
            "language": "Sprache",
            "voice": "Stimme",
            "quick_actions": "Schnellaktionen",
            "send": "Senden",
            "listening": "Höre zu...",
            "speaking": "Spreche...",
            "connected": "Verbunden",
            "disconnected": "Getrennt",
            "weather": "Wetter",
            "documents": "Dokumente",
            "cameras": "Kameras",
            "sales": "Verkauf",
            "home": "Zuhause",
            "analytics": "Analytik",
            "system": "System",
        },
        "uk": {
            "welcome": "Привіт! Я ваш асистент. Скажіть, що ви хочете зробити.",
            "help": "Показую доступні команди.",
            "not_understood": "Не розумію. Скажіть 'допомога' для команд.",
            "error": "Сталася помилка.",
            "success": "Готово!",
            "loading": "Завантаження...",
            "settings": "Налаштування",
            "language": "Мова",
            "voice": "Голос",
            "quick_actions": "Швидкі дії",
            "send": "Надіслати",
            "listening": "Слухаю...",
            "speaking": "Говорю...",
            "connected": "Підключено",
            "disconnected": "Відключено",
            "weather": "Погода",
            "documents": "Документи",
            "cameras": "Камери",
            "sales": "Продажі",
            "home": "Дім",
            "analytics": "Аналітика",
            "system": "Система",
        },
    }
    
    # Command patterns per language
    COMMAND_PATTERNS = {
        "pl": {
            "weather": ["pogoda", "temperatura", "prognoza"],
            "documents": ["faktury", "dokumenty", "skanuj"],
            "cameras": ["kamery", "monitoring", "ruch"],
            "help": ["pomoc", "komendy"],
            "status": ["status", "stan"],
        },
        "en": {
            "weather": ["weather", "temperature", "forecast"],
            "documents": ["invoices", "documents", "scan"],
            "cameras": ["cameras", "monitoring", "motion"],
            "help": ["help", "commands"],
            "status": ["status", "state"],
        },
        "de": {
            "weather": ["wetter", "temperatur", "vorhersage"],
            "documents": ["rechnungen", "dokumente", "scannen"],
            "cameras": ["kameras", "überwachung", "bewegung"],
            "help": ["hilfe", "befehle"],
            "status": ["status", "zustand"],
        },
        "uk": {
            "weather": ["погода", "температура", "прогноз"],
            "documents": ["рахунки", "документи", "сканувати"],
            "cameras": ["камери", "моніторинг", "рух"],
            "help": ["допомога", "команди"],
            "status": ["статус", "стан"],
        },
    }
    
    def __init__(self):
        self.current_language = "pl"
        self.session_languages: Dict[str, str] = {}  # session_id -> language
        logger.info(f"🌐 LanguageManager initialized: {self.current_language}")
    
    def get_language(self, session_id: str = None) -> str:
        """Get current language for session"""
        if session_id and session_id in self.session_languages:
            return self.session_languages[session_id]
        return self.current_language
    
    def set_language(self, language: str, session_id: str = None) -> bool:
        """Set language for session or globally"""
        if language not in self.LANGUAGES:
            logger.warning(f"Unsupported language: {language}")
            return False
        
        if session_id:
            self.session_languages[session_id] = language
            logger.info(f"🌐 Language set for session {session_id[:8]}: {language}")
        else:
            self.current_language = language
            logger.info(f"🌐 Global language set: {language}")
        
        return True
    
    def get_available_languages(self) -> List[Dict]:
        """Get list of available languages"""
        return [
            {
                "code": lang.code,
                "name": lang.name,
                "native_name": lang.native_name,
                "enabled": lang.enabled
            }
            for lang in self.LANGUAGES.values()
            if lang.enabled
        ]
    
    def translate(self, key: str, session_id: str = None) -> str:
        """Get translation for key"""
        lang = self.get_language(session_id)
        translations = self.TRANSLATIONS.get(lang, self.TRANSLATIONS.get("en", {}))
        return translations.get(key, key)
    
    def get_tts_config(self, session_id: str = None) -> Dict:
        """Get TTS configuration for current language"""
        lang_code = self.get_language(session_id)
        lang = self.LANGUAGES.get(lang_code)
        
        if not lang:
            lang = self.LANGUAGES["en"]
        
        return {
            "language": lang.code,
            "voice": lang.tts_voice,
            "model": f"{lang.code}-{lang.code.upper()}"
        }
    
    def get_stt_config(self, session_id: str = None) -> Dict:
        """Get STT configuration for current language"""
        lang_code = self.get_language(session_id)
        lang = self.LANGUAGES.get(lang_code)
        
        if not lang:
            lang = self.LANGUAGES["en"]
        
        return {
            "language": lang.stt_model,
            "model": lang.stt_model
        }
    
    def detect_command_language(self, text: str) -> Optional[str]:
        """Detect language from command text"""
        text_lower = text.lower()
        
        for lang_code, patterns in self.COMMAND_PATTERNS.items():
            for category, keywords in patterns.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        return lang_code
        
        return None
    
    def normalize_command(self, text: str, target_lang: str = "pl") -> str:
        """Normalize command to target language (for internal processing)"""
        source_lang = self.detect_command_language(text)
        
        if not source_lang or source_lang == target_lang:
            return text
        
        # Find matching category and translate
        text_lower = text.lower()
        source_patterns = self.COMMAND_PATTERNS.get(source_lang, {})
        target_patterns = self.COMMAND_PATTERNS.get(target_lang, {})
        
        for category, keywords in source_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Get first keyword from target language
                    target_keywords = target_patterns.get(category, [])
                    if target_keywords:
                        return text_lower.replace(keyword, target_keywords[0])
        
        return text
    
    def get_all_translations(self, session_id: str = None) -> Dict:
        """Get all translations for current language"""
        lang = self.get_language(session_id)
        return self.TRANSLATIONS.get(lang, self.TRANSLATIONS.get("en", {}))


# Global language manager instance
language_manager = LanguageManager()
