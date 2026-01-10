"""
Bar Ca l'Elena Translations
Multi-language support for Bar website (Catalan, Spanish, English, German, French)
"""
from typing import Dict

# 5 languages: ca (Catalan), es (Spanish), en (English), de (German), fr (French)
BAR_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Navigation & General
    "bar_name": {
        "ca": "Bar Ca l'Elena",
        "es": "Bar Ca l'Elena",
        "en": "Bar Ca l'Elena",
        "de": "Bar Ca l'Elena",
        "fr": "Bar Ca l'Elena"
    },
    "nav_home": {
        "ca": "Inici",
        "es": "Inicio",
        "en": "Home",
        "de": "Startseite",
        "fr": "Accueil"
    },
    "nav_menu": {
        "ca": "Menú",
        "es": "Menú",
        "en": "Menu",
        "de": "Speisekarte",
        "fr": "Menu"
    },
    "nav_news": {
        "ca": "Notícies",
        "es": "Noticias",
        "en": "News",
        "de": "Aktuelles",
        "fr": "Actualités"
    },
    "nav_chat": {
        "ca": "Xat",
        "es": "Chat",
        "en": "Chat",
        "de": "Chat",
        "fr": "Chat"
    },
    "nav_contact": {
        "ca": "Contacte",
        "es": "Contacto",
        "en": "Contact",
        "de": "Kontakt",
        "fr": "Contact"
    },
    "nav_admin": {
        "ca": "Admin",
        "es": "Admin",
        "en": "Admin",
        "de": "Admin",
        "fr": "Admin"
    },

    # Home Page
    "welcome_title": {
        "ca": "Benvinguts a Bar Ca l'Elena",
        "es": "Bienvenidos a Bar Ca l'Elena",
        "en": "Welcome to Bar Ca l'Elena",
        "de": "Willkommen bei Bar Ca l'Elena",
        "fr": "Bienvenue à Bar Ca l'Elena"
    },
    "about_title": {
        "ca": "Sobre Nosaltres",
        "es": "Sobre Nosotros",
        "en": "About Us",
        "de": "Über Uns",
        "fr": "À Propos"
    },
    "opening_hours": {
        "ca": "Horari d'obertura",
        "es": "Horario de apertura",
        "en": "Opening Hours",
        "de": "Öffnungszeiten",
        "fr": "Heures d'ouverture"
    },
    "address": {
        "ca": "Adreça",
        "es": "Dirección",
        "en": "Address",
        "de": "Adresse",
        "fr": "Adresse"
    },
    "phone": {
        "ca": "Telèfon",
        "es": "Teléfono",
        "en": "Phone",
        "de": "Telefon",
        "fr": "Téléphone"
    },
    "cuisine": {
        "ca": "Cuina",
        "es": "Cocina",
        "en": "Cuisine",
        "de": "Küche",
        "fr": "Cuisine"
    },
    "price_range": {
        "ca": "Rang de preus",
        "es": "Rango de precios",
        "en": "Price Range",
        "de": "Preisspanne",
        "fr": "Gamme de prix"
    },
    "rating": {
        "ca": "Valoració",
        "es": "Valoración",
        "en": "Rating",
        "de": "Bewertung",
        "fr": "Note"
    },
    "where_we_are": {
        "ca": "On som?",
        "es": "¿Dónde estamos?",
        "en": "Where are we?",
        "de": "Wo sind wir?",
        "fr": "Où sommes-nous?"
    },
    "view_map": {
        "ca": "Veure mapa",
        "es": "Ver mapa",
        "en": "View map",
        "de": "Karte ansehen",
        "fr": "Voir la carte"
    },

    # Featured Items
    "featured_items": {
        "ca": "Plats destacats",
        "es": "Platos destacados",
        "en": "Featured Items",
        "de": "Empfohlene Gerichte",
        "fr": "Plats vedettes"
    },
    "our_dishes": {
        "ca": "Els Nostres Plats",
        "es": "Nuestros Platos",
        "en": "Our Dishes",
        "de": "Unsere Gerichte",
        "fr": "Nos Plats"
    },

    # Chat
    "chat_welcome": {
        "ca": "Benvingut al xat de Bar Ca l'Elena!",
        "es": "¡Bienvenido al chat del Bar Ca l'Elena!",
        "en": "Welcome to Bar Ca l'Elena Chat!",
        "de": "Willkommen beim Bar Ca l'Elena Chat!",
        "fr": "Bienvenue au chat du Bar Ca l'Elena!"
    },
    "chat_help": {
        "ca": "Pregunta'm sobre el menú, horaris, ubicació o qualsevol altra cosa!",
        "es": "¡Pregúntame sobre el menú, horarios, ubicación o cualquier otra cosa!",
        "en": "Ask me about our menu, opening hours, location, or anything else!",
        "de": "Frag mich nach unserer Speisekarte, Öffnungszeiten, Standort oder allem anderen!",
        "fr": "Demandez-moi des informations sur notre menu, les horaires, l'emplacement ou autre chose!"
    },
    "chat_placeholder": {
        "ca": "Escriu el teu missatge...",
        "es": "Escribe tu mensaje...",
        "en": "Type your message...",
        "de": "Gib deine Nachricht ein...",
        "fr": "Tapez votre message..."
    },
    "chat_error": {
        "ca": "Ho sento, hi ha hagut un error processant el missatge.",
        "es": "Lo siento, hubo un error procesando el mensaje.",
        "en": "Sorry, there was an error processing your message.",
        "de": "Entschuldigung, es gab einen Fehler beim Verarbeiten Ihrer Nachricht.",
        "fr": "Désolé, il y a eu une erreur lors du traitement de votre message."
    },
    "auto_speak": {
        "ca": "Lectura automàtica de respostes",
        "es": "Lectura automática de respuestas",
        "en": "Auto-speak responses",
        "de": "Automatische Sprachausgabe",
        "fr": "Lecture automatique des réponses"
    },
    "translate_only": {
        "ca": "Només mode de traducció",
        "es": "Solo modo de traducción",
        "en": "Translation mode only",
        "de": "Nur Übersetzungsmodus",
        "fr": "Mode traduction uniquement"
    },
    "chat_language": {
        "ca": "Idioma del xat",
        "es": "Idioma del chat",
        "en": "Chat language",
        "de": "Chat-Sprache",
        "fr": "Langue du chat"
    },
    "speak": {
        "ca": "Parlar",
        "es": "Hablar",
        "en": "Speak",
        "de": "Sprechen",
        "fr": "Parler"
    },
    "send": {
        "ca": "Enviar",
        "es": "Enviar",
        "en": "Send",
        "de": "Senden",
        "fr": "Envoyer"
    },
    "sending": {
        "ca": "Enviant...",
        "es": "Enviando...",
        "en": "Sending...",
        "de": "Senden...",
        "fr": "Envoi en cours..."
    },
    "voice_input": {
        "ca": "Entrada de veu disponible",
        "es": "Entrada de voz disponible",
        "en": "Voice input available",
        "de": "Spracheingabe verfügbar",
        "fr": "Entrée vocale disponible"
    },
    "voice_output": {
        "ca": "Sortida de veu disponible",
        "es": "Salida de voz disponible",
        "en": "Voice output available",
        "de": "Sprachausgabe verfügbar",
        "fr": "Sortie vocale disponible"
    },

    # Menu Page
    "menu_title": {
        "ca": "El Nostre Menú",
        "es": "Nuestro Menú",
        "en": "Our Menu",
        "de": "Unsere Speisekarte",
        "fr": "Notre Menu"
    },
    "lunch_menu": {
        "ca": "Menú del dia",
        "es": "Menú del día",
        "en": "Lunch Menu",
        "de": "Mittagskarte",
        "fr": "Menu du jour"
    },
    "food_menu": {
        "ca": "Carta de menjar",
        "es": "Carta de comida",
        "en": "Food Menu",
        "de": "Speisekarte",
        "fr": "Carte alimentaire"
    },
    "drinks_menu": {
        "ca": "Carta de begudes",
        "es": "Carta de bebidas",
        "en": "Drinks Menu",
        "de": "Getränkekarte",
        "fr": "Carte des boissons"
    },
    "download_menu": {
        "ca": "Descarregar menú",
        "es": "Descargar menú",
        "en": "Download menu",
        "de": "Speisekarte herunterladen",
        "fr": "Télécharger le menu"
    },

    # News & Events
    "latest_news": {
        "ca": "Últimes notícies",
        "es": "Últimas noticias",
        "en": "Latest News",
        "de": "Neueste Nachrichten",
        "fr": "Dernières nouvelles"
    },
    "upcoming_events": {
        "ca": "Pròxims esdeveniments",
        "es": "Próximos eventos",
        "en": "Upcoming Events",
        "de": "Kommende Veranstaltungen",
        "fr": "Événements à venir"
    },
    "read_more": {
        "ca": "Llegir més",
        "es": "Leer más",
        "en": "Read more",
        "de": "Mehr lesen",
        "fr": "Lire la suite"
    },
    "published_on": {
        "ca": "Publicat el",
        "es": "Publicado el",
        "en": "Published on",
        "de": "Veröffentlicht am",
        "fr": "Publié le"
    },

    # Chat
    "chat_title": {
        "ca": "Pregunta'ns qualsevol cosa",
        "es": "Pregúntanos cualquier cosa",
        "en": "Ask us anything",
        "de": "Frag uns etwas",
        "fr": "Demandez-nous n'importe quoi"
    },
    "chat_placeholder": {
        "ca": "Escriu el teu missatge aquí...",
        "es": "Escribe tu mensaje aquí...",
        "en": "Type your message here...",
        "de": "Schreibe deine Nachricht hier...",
        "fr": "Tapez votre message ici..."
    },
    "chat_send": {
        "ca": "Enviar",
        "es": "Enviar",
        "en": "Send",
        "de": "Senden",
        "fr": "Envoyer"
    },
    "chat_thinking": {
        "ca": "Pensant...",
        "es": "Pensando...",
        "en": "Thinking...",
        "de": "Denke nach...",
        "fr": "Réflexion..."
    },

    # Reservations
    "reservation_title": {
        "ca": "Fes una reserva",
        "es": "Hacer una reserva",
        "en": "Make a Reservation",
        "de": "Reservierung vornehmen",
        "fr": "Faire une réservation"
    },
    "reservation_name": {
        "ca": "Nom",
        "es": "Nombre",
        "en": "Name",
        "de": "Name",
        "fr": "Nom"
    },
    "reservation_email": {
        "ca": "Correu electrònic",
        "es": "Correo electrónico",
        "en": "Email",
        "de": "E-Mail",
        "fr": "E-mail"
    },
    "reservation_phone": {
        "ca": "Telèfon",
        "es": "Teléfono",
        "en": "Phone",
        "de": "Telefon",
        "fr": "Téléphone"
    },
    "reservation_date": {
        "ca": "Data i hora",
        "es": "Fecha y hora",
        "en": "Date and time",
        "de": "Datum und Uhrzeit",
        "fr": "Date et heure"
    },
    "reservation_guests": {
        "ca": "Nombre de persones",
        "es": "Número de personas",
        "en": "Number of guests",
        "de": "Anzahl Gäste",
        "fr": "Nombre de personnes"
    },
    "reservation_message": {
        "ca": "Missatge (opcional)",
        "es": "Mensaje (opcional)",
        "en": "Message (optional)",
        "de": "Nachricht (optional)",
        "fr": "Message (optionnel)"
    },
    "reservation_submit": {
        "ca": "Reservar",
        "es": "Reservar",
        "en": "Reserve",
        "de": "Reservieren",
        "fr": "Réserver"
    },
    "reservation_success": {
        "ca": "Reserva rebuda! Ens posarem en contacte aviat.",
        "es": "¡Reserva recibida! Nos pondremos en contacto pronto.",
        "en": "Reservation received! We'll contact you soon.",
        "de": "Reservierung erhalten! Wir melden uns bald.",
        "fr": "Réservation reçue! Nous vous contacterons bientôt."
    },
    "reservation_error": {
        "ca": "Error en enviar la reserva. Torna-ho a provar.",
        "es": "Error al enviar la reserva. Inténtalo de nuevo.",
        "en": "Error submitting reservation. Please try again.",
        "de": "Fehler beim Senden der Reservierung. Bitte versuche es erneut.",
        "fr": "Erreur lors de l'envoi de la réservation. Veuillez réessayer."
    },

    # Newsletter
    "newsletter_title": {
        "ca": "Subscriu-te al nostre butlletí i menú diari",
        "es": "Suscríbete a nuestro boletín y menú diario",
        "en": "Subscribe to our newsletter and daily menu",
        "de": "Abonniere unseren Newsletter und Tagesmenü",
        "fr": "Abonnez-vous à notre newsletter et menu du jour"
    },
    "newsletter_email": {
        "ca": "Correu electrònic",
        "es": "Correo electrónico",
        "en": "Email",
        "de": "E-Mail",
        "fr": "E-mail"
    },
    "newsletter_name": {
        "ca": "Nom (opcional)",
        "es": "Nombre (opcional)",
        "en": "Name (optional)",
        "de": "Name (optional)",
        "fr": "Nom (optionnel)"
    },
    "newsletter_submit": {
        "ca": "Subscriure's",
        "es": "Suscribirse",
        "en": "Subscribe",
        "de": "Abonnieren",
        "fr": "S'abonner"
    },
    "newsletter_success": {
        "ca": "Gràcies per subscriure't!",
        "es": "¡Gracias por suscribirte!",
        "en": "Thanks for subscribing!",
        "de": "Danke fürs Abonnieren!",
        "fr": "Merci de vous être abonné!"
    },
    "newsletter_error": {
        "ca": "Error en subscriure's. Torna-ho a provar.",
        "es": "Error al suscribirse. Inténtalo de nuevo.",
        "en": "Error subscribing. Please try again.",
        "de": "Fehler beim Abonnieren. Bitte versuche es erneut.",
        "fr": "Erreur lors de l'abonnement. Veuillez réessayer."
    },

    # Reviews
    "reviews_title": {
        "ca": "Opinions dels clients",
        "es": "Opiniones de los clientes",
        "en": "Customer Reviews",
        "de": "Kundenbewertungen",
        "fr": "Avis des clients"
    },

    # Social Media
    "follow_us": {
        "ca": "Segueix-nos",
        "es": "Síguenos",
        "en": "Follow us",
        "de": "Folge uns",
        "fr": "Suivez-nous"
    },
    "facebook": {
        "ca": "Facebook",
        "es": "Facebook",
        "en": "Facebook",
        "de": "Facebook",
        "fr": "Facebook"
    },

    # Admin
    "admin_login": {
        "ca": "Inici de sessió d'administrador",
        "es": "Inicio de sesión de administrador",
        "en": "Admin Login",
        "de": "Admin-Anmeldung",
        "fr": "Connexion administrateur"
    },
    "admin_panel": {
        "ca": "Tauler d'administració",
        "es": "Panel de administración",
        "en": "Admin Panel",
        "de": "Admin-Panel",
        "fr": "Panneau d'administration"
    },
    "admin_username": {
        "ca": "Nom d'usuari",
        "es": "Nombre de usuario",
        "en": "Username",
        "de": "Benutzername",
        "fr": "Nom d'utilisateur"
    },
    "admin_password": {
        "ca": "Contrasenya",
        "es": "Contraseña",
        "en": "Password",
        "de": "Passwort",
        "fr": "Mot de passe"
    },
    "admin_login_btn": {
        "ca": "Iniciar sessió",
        "es": "Iniciar sesión",
        "en": "Login",
        "de": "Anmelden",
        "fr": "Se connecter"
    },
    "admin_logout": {
        "ca": "Tancar sessió",
        "es": "Cerrar sesión",
        "en": "Logout",
        "de": "Abmelden",
        "fr": "Se déconnecter"
    },
    "admin_settings": {
        "ca": "Configuració",
        "es": "Configuración",
        "en": "Settings",
        "de": "Einstellungen",
        "fr": "Paramètres"
    },
    "admin_menu_management": {
        "ca": "Gestió de menús",
        "es": "Gestión de menús",
        "en": "Menu Management",
        "de": "Menü-Verwaltung",
        "fr": "Gestion des menus"
    },
    "admin_featured_items": {
        "ca": "Plats destacats",
        "es": "Platos destacados",
        "en": "Featured Items",
        "de": "Empfohlene Gerichte",
        "fr": "Plats vedettes"
    },
    "admin_news_management": {
        "ca": "Gestió de notícies",
        "es": "Gestión de noticias",
        "en": "News Management",
        "de": "Nachrichten-Verwaltung",
        "fr": "Gestion des actualités"
    },
    "admin_llm_select": {
        "ca": "Selecciona el proveïdor LLM",
        "es": "Seleccionar proveedor LLM",
        "en": "Select LLM Provider",
        "de": "LLM-Anbieter auswählen",
        "fr": "Sélectionner le fournisseur LLM"
    },
    "admin_llm_ollama": {
        "ca": "Ollama (local, compatible amb RGPD)",
        "es": "Ollama (local, compatible con RGPD)",
        "en": "Ollama (local, GDPR compliant)",
        "de": "Ollama (lokal, DSGVO-konform)",
        "fr": "Ollama (local, conforme RGPD)"
    },
    "admin_llm_grok": {
        "ca": "Grok (núvol, ràpid)",
        "es": "Grok (nube, rápido)",
        "en": "Grok (cloud, fast)",
        "de": "Grok (Cloud, schnell)",
        "fr": "Grok (nuage, rapide)"
    },
    "admin_upload_menu": {
        "ca": "Carregar menú",
        "es": "Cargar menú",
        "en": "Upload Menu",
        "de": "Speisekarte hochladen",
        "fr": "Télécharger le menu"
    },
    "admin_add_news": {
        "ca": "Afegir notícia",
        "es": "Agregar noticia",
        "en": "Add News",
        "de": "Nachricht hinzufügen",
        "fr": "Ajouter une actualité"
    },
    "admin_news_title": {
        "ca": "Títol",
        "es": "Título",
        "en": "Title",
        "de": "Titel",
        "fr": "Titre"
    },
    "admin_news_content": {
        "ca": "Contingut",
        "es": "Contenido",
        "en": "Content",
        "de": "Inhalt",
        "fr": "Contenu"
    },
    "admin_news_image": {
        "ca": "URL de la imatge",
        "es": "URL de la imagen",
        "en": "Image URL",
        "de": "Bild-URL",
        "fr": "URL de l'image"
    },
    "admin_save": {
        "ca": "Desar",
        "es": "Guardar",
        "en": "Save",
        "de": "Speichern",
        "fr": "Enregistrer"
    },
    "admin_save_settings": {
        "ca": "Desar configuració",
        "es": "Guardar configuración",
        "en": "Save Settings",
        "de": "Einstellungen speichern",
        "fr": "Enregistrer les paramètres"
    },
    "admin_settings_saved": {
        "ca": "Configuració desada!",
        "es": "¡Configuración guardada!",
        "en": "Settings saved!",
        "de": "Einstellungen gespeichert!",
        "fr": "Paramètres enregistrés!"
    },
    "admin_menu_upload": {
        "ca": "Carregar arxiu de menú",
        "es": "Cargar archivo de menú",
        "en": "Upload Menu File",
        "de": "Menü-Datei hochladen",
        "fr": "Télécharger le fichier de menu"
    },
    "admin_menu_title": {
        "ca": "Títol del menú",
        "es": "Título del menú",
        "en": "Menu Title",
        "de": "Menütitel",
        "fr": "Titre du menu"
    },
    "admin_menu_type": {
        "ca": "Tipus de menú",
        "es": "Tipo de menú",
        "en": "Menu Type",
        "de": "Menütyp",
        "fr": "Type de menu"
    },
    "admin_menu_description": {
        "ca": "Descripció",
        "es": "Descripción",
        "en": "Description",
        "de": "Beschreibung",
        "fr": "Description"
    },
    "admin_choose_file": {
        "ca": "Triar arxiu",
        "es": "Elegir archivo",
        "en": "Choose File",
        "de": "Datei auswählen",
        "fr": "Choisir un fichier"
    },
    "admin_change_image": {
        "ca": "Canviar imatge",
        "es": "Cambiar imagen",
        "en": "Change Image",
        "de": "Bild ändern",
        "fr": "Changer l'image"
    },
    "admin_upload": {
        "ca": "Carregar",
        "es": "Cargar",
        "en": "Upload",
        "de": "Hochladen",
        "fr": "Télécharger"
    },
    "admin_upload_success": {
        "ca": "Menú carregat amb èxit!",
        "es": "¡Menú cargado con éxito!",
        "en": "Menu uploaded successfully!",
        "de": "Menü erfolgreich hochgeladen!",
        "fr": "Menu téléchargé avec succès!"
    },
    "admin_invalid_credentials": {
        "ca": "Credencials no vàlides",
        "es": "Credenciales no válidas",
        "en": "Invalid credentials",
        "de": "Ungültige Anmeldedaten",
        "fr": "Identifiants invalides"
    },
    "admin_chatbot_settings": {
        "ca": "Configuració del xatbot",
        "es": "Configuración del chatbot",
        "en": "Chatbot Settings",
        "de": "Chatbot-Einstellungen",
        "fr": "Paramètres du chatbot"
    },
    "admin_auto_speak_default": {
        "ca": "Activar lectura automàtica per defecte",
        "es": "Activar lectura automática por defecto",
        "en": "Enable auto-speak by default",
        "de": "Automatische Sprachausgabe standardmäßig aktivieren",
        "fr": "Activer la lecture automatique par défaut"
    },
    "admin_contact_email": {
        "ca": "Correu electrònic de contacte (per a enviaments de formularis)",
        "es": "Correo electrónico de contacto (para envíos de formularios)",
        "en": "Contact Email (for form submissions)",
        "de": "Kontakt-E-Mail (für Formulareinreichungen)",
        "fr": "E-mail de contact (pour les soumissions de formulaires)"
    },
    "admin_menu_description_optional": {
        "ca": "Descripció (Opcional)",
        "es": "Descripción (Opcional)",
        "en": "Description (Optional)",
        "de": "Beschreibung (Optional)",
        "fr": "Description (Optionnel)"
    },
    "admin_menu_description_placeholder": {
        "ca": "Descripció d'aquest menú...",
        "es": "Descripción de este menú...",
        "en": "Description of this menu...",
        "de": "Beschreibung dieses Menüs...",
        "fr": "Description de ce menu..."
    },
    "admin_featured_items_title": {
        "ca": "Gestió d'elements destacats",
        "es": "Gestión de elementos destacados",
        "en": "Featured Items Management",
        "de": "Verwaltung der vorgestellten Artikel",
        "fr": "Gestion des éléments en vedette"
    },
    "admin_featured_items_description": {
        "ca": "Afegeix fins a 8 plats destacats. Introdueix el nom en el teu idioma preferit, puja una imatge (JPG/PNG), després fes clic a \"Traduir\" per a traduccions multilingües automàtiques. Finalment, fes clic a \"Publicar tot\" per actualitzar el lloc web.",
        "es": "Añade hasta 8 platos destacados. Introduce el nombre en tu idioma preferido, sube una imagen (JPG/PNG), después haz clic en \"Traducir\" para traducciones multilingües automáticas. Finalmente, haz clic en \"Publicar todo\" para actualizar el sitio web.",
        "en": "Add up to 8 featured dishes. Enter the name in your preferred language, upload an image (JPG/PNG), then click \"Translate\" for automatic multilingual translations. Finally, click \"Publish All\" to update the website.",
        "de": "Fügen Sie bis zu 8 vorgestellte Gerichte hinzu. Geben Sie den Namen in Ihrer bevorzugten Sprache ein, laden Sie ein Bild hoch (JPG/PNG) und klicken Sie dann auf \"Übersetzen\" für automatische mehrsprachige Übersetzungen. Klicken Sie abschließend auf \"Alle veröffentlichen\", um die Website zu aktualisieren.",
        "fr": "Ajoutez jusqu'à 8 plats en vedette. Entrez le nom dans votre langue préférée, téléchargez une image (JPG/PNG), puis cliquez sur \"Traduire\" pour les traductions multilingues automatiques. Enfin, cliquez sur \"Tout publier\" pour mettre à jour le site web."
    },
    "admin_item_number": {
        "ca": "Element {number}",
        "es": "Elemento {number}",
        "en": "Item {number}",
        "de": "Artikel {number}",
        "fr": "Élément {number}"
    },
    "admin_dish_name": {
        "ca": "Nom del plat",
        "es": "Nombre del plato",
        "en": "Dish Name",
        "de": "Gericht Name",
        "fr": "Nom du plat"
    },
    "admin_dish_name_placeholder": {
        "ca": "p. ex., Paella, Fideuà, Truita",
        "es": "p. ej., Paella, Fideuà, Tortilla",
        "en": "e.g., Paella, Fideua, Tortilla",
        "de": "z.B. Paella, Fideuà, Tortilla",
        "fr": "p. ex., Paella, Fideuà, Tortilla"
    },
    "admin_source_language": {
        "ca": "Idioma d'origen",
        "es": "Idioma de origen",
        "en": "Source Language",
        "de": "Ausgangssprache",
        "fr": "Langue source"
    },
    "admin_image_upload": {
        "ca": "Imatge (JPG/PNG)",
        "es": "Imagen (JPG/PNG)",
        "en": "Image (JPG/PNG)",
        "de": "Bild (JPG/PNG)",
        "fr": "Image (JPG/PNG)"
    },
    "admin_translate_button": {
        "ca": "🌐 Traduir",
        "es": "🌐 Traducir",
        "en": "🌐 Translate",
        "de": "🌐 Übersetzen",
        "fr": "🌐 Traduire"
    },
    "admin_translations_label": {
        "ca": "Traduccions:",
        "es": "Traducciones:",
        "en": "Translations:",
        "de": "Übersetzungen:",
        "fr": "Traductions:"
    },
    "admin_translate_all": {
        "ca": "🌐 Traduir tot",
        "es": "🌐 Traducir todo",
        "en": "🌐 Translate All",
        "de": "🌐 Alle übersetzen",
        "fr": "🌐 Tout traduire"
    },
    "admin_publish_all": {
        "ca": "🚀 Publicar tot",
        "es": "🚀 Publicar todo",
        "en": "🚀 Publish All",
        "de": "🚀 Alle veröffentlichen",
        "fr": "🚀 Tout publier"
    },
    "admin_image_uploaded": {
        "ca": "Imatge pujada per a l'element {number}",
        "es": "Imagen subida para el elemento {number}",
        "en": "Image uploaded for item {number}",
        "de": "Bild für Artikel {number} hochgeladen",
        "fr": "Image téléchargée pour l'élément {number}"
    },
    "admin_image_upload_failed": {
        "ca": "Error en pujar la imatge",
        "es": "Error al subir la imagen",
        "en": "Image upload failed",
        "de": "Bild-Upload fehlgeschlagen",
        "fr": "Échec du téléchargement de l'image"
    },
    "admin_enter_dish_name": {
        "ca": "Si us plau, introdueix primer el nom del plat",
        "es": "Por favor, introduce primero el nombre del plato",
        "en": "Please enter a dish name first",
        "de": "Bitte geben Sie zuerst einen Gerichtnamen ein",
        "fr": "Veuillez d'abord entrer un nom de plat"
    },
    "admin_translated": {
        "ca": "Traduït: {name}",
        "es": "Traducido: {name}",
        "en": "Translated: {name}",
        "de": "Übersetzt: {name}",
        "fr": "Traduit: {name}"
    },
    "admin_translation_failed": {
        "ca": "Error en la traducció",
        "es": "Error en la traducción",
        "en": "Translation failed",
        "de": "Übersetzung fehlgeschlagen",
        "fr": "Échec de la traduction"
    },
    "admin_translating_all": {
        "ca": "Traduint tots els elements...",
        "es": "Traduciendo todos los elementos...",
        "en": "Translating all items...",
        "de": "Alle Artikel werden übersetzt...",
        "fr": "Traduction de tous les éléments..."
    },
    "admin_all_translations_complete": {
        "ca": "Totes les traduccions completades!",
        "es": "¡Todas las traducciones completadas!",
        "en": "All translations complete!",
        "de": "Alle Übersetzungen abgeschlossen!",
        "fr": "Toutes les traductions terminées!"
    },
    "admin_publishing": {
        "ca": "Publicant...",
        "es": "Publicando...",
        "en": "Publishing...",
        "de": "Veröffentlichen...",
        "fr": "Publication en cours..."
    },
    "admin_add_complete_item": {
        "ca": "Si us plau, afegeix almenys un element complet (nom, traduccions, imatge)",
        "es": "Por favor, añade al menos un elemento completo (nombre, traducciones, imagen)",
        "en": "Please add at least one complete item (name, translations, image)",
        "de": "Bitte fügen Sie mindestens einen vollständigen Artikel hinzu (Name, Übersetzungen, Bild)",
        "fr": "Veuillez ajouter au moins un élément complet (nom, traductions, image)"
    },
    "admin_published_items": {
        "ca": "✅ {count} elements destacats publicats!",
        "es": "✅ ¡{count} elementos destacados publicados!",
        "en": "✅ Published {count} featured items!",
        "de": "✅ {count} vorgestellte Artikel veröffentlicht!",
        "fr": "✅ {count} éléments en vedette publiés!"
    },
    "admin_publishing_failed": {
        "ca": "❌ Error en la publicació",
        "es": "❌ Error en la publicación",
        "en": "❌ Publishing failed",
        "de": "❌ Veröffentlichung fehlgeschlagen",
        "fr": "❌ Échec de la publication"
    },
    "admin_news_title": {
        "ca": "Gestió de notícies",
        "es": "Gestión de noticias",
        "en": "News Management",
        "de": "Nachrichtenverwaltung",
        "fr": "Gestion des actualités"
    },
    "admin_news_description": {
        "ca": "Gestiona notícies i anuncis. Introdueix el títol i el contingut en el teu idioma preferit, puja una imatge (JPG/PNG), després fes clic a \"Traduir\" per a traduccions multilingües automàtiques. Finalment, fes clic a \"Guardar\" per publicar cada notícia individualment.",
        "es": "Gestiona noticias y anuncios. Introduce el título y el contenido en tu idioma preferido, sube una imagen (JPG/PNG), después haz clic en \"Traducir\" para traducciones multilingües automáticas. Finalmente, haz clic en \"Guardar\" para publicar cada noticia individualmente.",
        "en": "Manage news and announcements. Enter the title and content in your preferred language, upload an image (JPG/PNG), then click \"Translate\" for automatic multilingual translations. Finally, click \"Save\" to publish each news item individually.",
        "de": "Verwalten Sie Nachrichten und Ankündigungen. Geben Sie Titel und Inhalt in Ihrer bevorzugten Sprache ein, laden Sie ein Bild hoch (JPG/PNG) und klicken Sie dann auf \"Übersetzen\" für automatische mehrsprachige Übersetzungen. Klicken Sie abschließend auf \"Speichern\", um jeden Nachrichteneintrag einzeln zu veröffentlichen.",
        "fr": "Gérez les actualités et les annonces. Entrez le titre et le contenu dans votre langue préférée, téléchargez une image (JPG/PNG), puis cliquez sur \"Traduire\" pour les traductions multilingues automatiques. Enfin, cliquez sur \"Enregistrer\" pour publier chaque actualité individuellement."
    },
    "admin_news_item": {
        "ca": "Notícia {number}",
        "es": "Noticia {number}",
        "en": "News Item {number}",
        "de": "Nachricht {number}",
        "fr": "Actualité {number}"
    },
    "admin_delete": {
        "ca": "Eliminar",
        "es": "Eliminar",
        "en": "Delete",
        "de": "Löschen",
        "fr": "Supprimer"
    },
    "admin_title": {
        "ca": "Títol",
        "es": "Título",
        "en": "Title",
        "de": "Titel",
        "fr": "Titre"
    },
    "admin_title_placeholder": {
        "ca": "p. ex., Celebració d'Any Nou 2026",
        "es": "p. ej., Celebración de Año Nuevo 2026",
        "en": "e.g., New Year 2026 Celebration",
        "de": "z.B. Neujahrsfeier 2026",
        "fr": "p. ex., Célébration du Nouvel An 2026"
    },
    "admin_content": {
        "ca": "Contingut",
        "es": "Contenido",
        "en": "Content",
        "de": "Inhalt",
        "fr": "Contenu"
    },
    "admin_content_placeholder": {
        "ca": "Contingut complet de la notícia...",
        "es": "Contenido completo de la noticia...",
        "en": "Full news content...",
        "de": "Vollständiger Nachrichteninhalt...",
        "fr": "Contenu complet de l'actualité..."
    },
    "admin_is_event": {
        "ca": "És un esdeveniment",
        "es": "Es un evento",
        "en": "Is Event",
        "de": "Ist ein Event",
        "fr": "Est un événement"
    },
    "admin_save": {
        "ca": "💾 Guardar",
        "es": "💾 Guardar",
        "en": "💾 Save",
        "de": "💾 Speichern",
        "fr": "💾 Enregistrer"
    },
    "admin_add_news": {
        "ca": "➕ Afegir nova notícia",
        "es": "➕ Añadir nueva noticia",
        "en": "➕ Add New News Item",
        "de": "➕ Neue Nachricht hinzufügen",
        "fr": "➕ Ajouter une nouvelle actualité"
    },
    "admin_enter_title_content": {
        "ca": "Si us plau, introdueix tant el títol com el contingut primer",
        "es": "Por favor, introduce tanto el título como el contenido primero",
        "en": "Please enter both title and content first",
        "de": "Bitte geben Sie zuerst sowohl Titel als auch Inhalt ein",
        "fr": "Veuillez d'abord entrer le titre et le contenu"
    },
    "admin_news_translated": {
        "ca": "Notícia {number} traduïda",
        "es": "Noticia {number} traducida",
        "en": "Translated news item {number}",
        "de": "Nachricht {number} übersetzt",
        "fr": "Actualité {number} traduite"
    },
    "admin_complete_translations": {
        "ca": "Si us plau, completa les traduccions abans de guardar",
        "es": "Por favor, completa las traducciones antes de guardar",
        "en": "Please complete translations before saving",
        "de": "Bitte vervollständigen Sie die Übersetzungen vor dem Speichern",
        "fr": "Veuillez compléter les traductions avant d'enregistrer"
    },
    "admin_news_updated": {
        "ca": "Notícia {number} actualitzada amb èxit",
        "es": "Noticia {number} actualizada con éxito",
        "en": "News item {number} updated successfully",
        "de": "Nachricht {number} erfolgreich aktualisiert",
        "fr": "Actualité {number} mise à jour avec succès"
    },
    "admin_news_created": {
        "ca": "Notícia {number} creada amb èxit",
        "es": "Noticia {number} creada con éxito",
        "en": "News item {number} created successfully",
        "de": "Nachricht {number} erfolgreich erstellt",
        "fr": "Actualité {number} créée avec succès"
    },
    "admin_failed_save": {
        "ca": "Error en guardar la notícia",
        "es": "Error al guardar la noticia",
        "en": "Failed to save news item",
        "de": "Fehler beim Speichern der Nachricht",
        "fr": "Échec de l'enregistrement de l'actualité"
    },
    "admin_delete_confirm": {
        "ca": "Estàs segur que vols eliminar aquesta notícia?",
        "es": "¿Estás seguro de que quieres eliminar esta noticia?",
        "en": "Are you sure you want to delete this news item?",
        "de": "Sind Sie sicher, dass Sie diese Nachricht löschen möchten?",
        "fr": "Êtes-vous sûr de vouloir supprimer cette actualité?"
    },
    "admin_news_deleted": {
        "ca": "Notícia eliminada amb èxit",
        "es": "Noticia eliminada con éxito",
        "en": "News item deleted successfully",
        "de": "Nachricht erfolgreich gelöscht",
        "fr": "Actualité supprimée avec succès"
    },
    "admin_failed_delete": {
        "ca": "Error en eliminar la notícia",
        "es": "Error al eliminar la noticia",
        "en": "Failed to delete news item",
        "de": "Fehler beim Löschen der Nachricht",
        "fr": "Échec de la suppression de l'actualité"
    },
    "admin_failed_load_news": {
        "ca": "Error en carregar les notícies existents",
        "es": "Error al cargar las noticias existentes",
        "en": "Failed to load existing news",
        "de": "Fehler beim Laden vorhandener Nachrichten",
        "fr": "Échec du chargement des actualités existantes"
    },
    "admin_content_preview": {
        "ca": "Vista prèvia del contingut ({lang}):",
        "es": "Vista previa del contenido ({lang}):",
        "en": "Content Preview ({lang}):",
        "de": "Inhaltsvorschau ({lang}):",
        "fr": "Aperçu du contenu ({lang}):"
    },

    # Days of week
    "monday": {
        "ca": "Dilluns",
        "es": "Lunes",
        "en": "Monday",
        "de": "Montag",
        "fr": "Lundi"
    },
    "tuesday": {
        "ca": "Dimarts",
        "es": "Martes",
        "en": "Tuesday",
        "de": "Dienstag",
        "fr": "Mardi"
    },
    "wednesday": {
        "ca": "Dimecres",
        "es": "Miércoles",
        "en": "Wednesday",
        "de": "Mittwoch",
        "fr": "Mercredi"
    },
    "thursday": {
        "ca": "Dijous",
        "es": "Jueves",
        "en": "Thursday",
        "de": "Donnerstag",
        "fr": "Jeudi"
    },
    "friday": {
        "ca": "Divendres",
        "es": "Viernes",
        "en": "Friday",
        "de": "Freitag",
        "fr": "Vendredi"
    },
    "saturday": {
        "ca": "Dissabte",
        "es": "Sábado",
        "en": "Saturday",
        "de": "Samstag",
        "fr": "Samedi"
    },
    "sunday": {
        "ca": "Diumenge",
        "es": "Domingo",
        "en": "Sunday",
        "de": "Sonntag",
        "fr": "Dimanche"
    },
    "closed": {
        "ca": "Tancat",
        "es": "Cerrado",
        "en": "Closed",
        "de": "Geschlossen",
        "fr": "Fermé"
    },
    "monday_friday": {
        "ca": "Dilluns-Divendres",
        "es": "Lunes-Viernes",
        "en": "Monday-Friday",
        "de": "Montag-Freitag",
        "fr": "Lundi-Vendredi"
    },
    "saturday": {
        "ca": "Dissabte",
        "es": "Sábado",
        "en": "Saturday",
        "de": "Samstag",
        "fr": "Samedi"
    },
    "sunday": {
        "ca": "Diumenge",
        "es": "Domingo",
        "en": "Sunday",
        "de": "Sonntag",
        "fr": "Dimanche"
    },

    # Slogan
    "bar_slogan": {
        "ca": "També parlem anglès!",
        "es": "¡También hablamos inglés!",
        "en": "We also speak English!",
        "de": "Wir sprechen auch Englisch!",
        "fr": "Nous parlons aussi anglais!"
    },
    "all_rights_reserved": {
        "ca": "Tots els drets reservats",
        "es": "Todos los derechos reservados",
        "en": "All rights reserved",
        "de": "Alle Rechte vorbehalten",
        "fr": "Tous droits réservés"
    },

    # Common
    "loading": {
        "ca": "Carregant...",
        "es": "Cargando...",
        "en": "Loading...",
        "de": "Laden...",
        "fr": "Chargement..."
    },
    "error": {
        "ca": "Error",
        "es": "Error",
        "en": "Error",
        "de": "Fehler",
        "fr": "Erreur"
    },
    "success": {
        "ca": "Èxit",
        "es": "Éxito",
        "en": "Success",
        "de": "Erfolg",
        "fr": "Succès"
    },
    "cancel": {
        "ca": "Cancel·lar",
        "es": "Cancelar",
        "en": "Cancel",
        "de": "Abbrechen",
        "fr": "Annuler"
    },
    "confirm": {
        "ca": "Confirmar",
        "es": "Confirmar",
        "en": "Confirm",
        "de": "Bestätigen",
        "fr": "Confirmer"
    },

    # Newsletter Management
    "admin_newsletter_management": {
        "ca": "Gestió del butlletí",
        "es": "Gestión del boletín",
        "en": "Newsletter Management",
        "de": "Newsletter-Verwaltung",
        "fr": "Gestion de la newsletter"
    },
    "admin_subscribers": {
        "ca": "Subscriptors",
        "es": "Suscriptores",
        "en": "Subscribers",
        "de": "Abonnenten",
        "fr": "Abonnés"
    },
    "admin_name": {
        "ca": "Nom",
        "es": "Nombre",
        "en": "Name",
        "de": "Name",
        "fr": "Nom"
    },
    "admin_language": {
        "ca": "Idioma",
        "es": "Idioma",
        "en": "Language",
        "de": "Sprache",
        "fr": "Langue"
    },
    "admin_status": {
        "ca": "Estat",
        "es": "Estado",
        "en": "Status",
        "de": "Status",
        "fr": "Statut"
    },
    "admin_subscribed": {
        "ca": "Subscrit",
        "es": "Suscrito",
        "en": "Subscribed",
        "de": "Abonniert",
        "fr": "Abonné"
    },
    "admin_active": {
        "ca": "Actiu",
        "es": "Activo",
        "en": "Active",
        "de": "Aktiv",
        "fr": "Actif"
    },
    "admin_inactive": {
        "ca": "Inactiu",
        "es": "Inactivo",
        "en": "Inactive",
        "de": "Inaktiv",
        "fr": "Inactif"
    },
    "admin_create_newsletter": {
        "ca": "Crear butlletí",
        "es": "Crear boletín",
        "en": "Create Newsletter",
        "de": "Newsletter erstellen",
        "fr": "Créer une newsletter"
    },
    "admin_newsletter_draft": {
        "ca": "Esborrany del butlletí",
        "es": "Borrador del boletín",
        "en": "Newsletter Draft",
        "de": "Newsletter-Entwurf",
        "fr": "Brouillon de newsletter"
    },
    "admin_subject": {
        "ca": "Assumpte",
        "es": "Asunto",
        "en": "Subject",
        "de": "Betreff",
        "fr": "Objet"
    },
    "admin_subject_placeholder": {
        "ca": "Introdueix l'assumpte del butlletí...",
        "es": "Introduce el asunto del boletín...",
        "en": "Enter newsletter subject...",
        "de": "Newsletter-Betreff eingeben...",
        "fr": "Entrez l'objet de la newsletter..."
    },
    "admin_content": {
        "ca": "Contingut",
        "es": "Contenido",
        "en": "Content",
        "de": "Inhalt",
        "fr": "Contenu"
    },
    "admin_content_placeholder": {
        "ca": "Introdueix el contingut del butlletí...",
        "es": "Introduce el contenido del boletín...",
        "en": "Enter newsletter content...",
        "de": "Newsletter-Inhalt eingeben...",
        "fr": "Entrez le contenu de la newsletter..."
    },
    "admin_send_newsletter": {
        "ca": "Enviar butlletí",
        "es": "Enviar boletín",
        "en": "Send Newsletter",
        "de": "Newsletter senden",
        "fr": "Envoyer la newsletter"
    },
    "admin_send_newsletter_confirm": {
        "ca": "Estàs segur que vols enviar aquest butlletí a tots els subscriptors?",
        "es": "¿Estás seguro de que quieres enviar este boletín a todos los suscriptores?",
        "en": "Are you sure you want to send this newsletter to all subscribers?",
        "de": "Sind Sie sicher, dass Sie diesen Newsletter an alle Abonnenten senden möchten?",
        "fr": "Êtes-vous sûr de vouloir envoyer cette newsletter à tous les abonnés?"
    },
    "admin_newsletter_sent": {
        "ca": "✅ Butlletí enviat a {count} subscriptors!",
        "es": "✅ ¡Boletín enviado a {count} suscriptores!",
        "en": "✅ Newsletter sent to {count} subscribers!",
        "de": "✅ Newsletter an {count} Abonnenten gesendet!",
        "fr": "✅ Newsletter envoyée à {count} abonnés!"
    },
    "admin_newsletter_send_failed": {
        "ca": "❌ Error en enviar el butlletí",
        "es": "❌ Error al enviar el boletín",
        "en": "❌ Failed to send newsletter",
        "de": "❌ Fehler beim Senden des Newsletters",
        "fr": "❌ Échec de l'envoi de la newsletter"
    },
    "admin_enter_title_content": {
        "ca": "Si us plau, introdueix l'assumpte i el contingut",
        "es": "Por favor, introduce el asunto y el contenido",
        "en": "Please enter subject and content",
        "de": "Bitte geben Sie Betreff und Inhalt ein",
        "fr": "Veuillez entrer l'objet et le contenu"
    },
    "admin_complete_translations": {
        "ca": "Si us plau, completa primer les traduccions",
        "es": "Por favor, completa primero las traducciones",
        "en": "Please complete translations first",
        "de": "Bitte schließen Sie zuerst die Übersetzungen ab",
        "fr": "Veuillez d'abord compléter les traductions"
    },
    "admin_translations_complete": {
        "ca": "✅ Traduccions completades!",
        "es": "✅ ¡Traducciones completadas!",
        "en": "✅ Translations complete!",
        "de": "✅ Übersetzungen abgeschlossen!",
        "fr": "✅ Traductions terminées!"
    },
    "admin_translation_failed": {
        "ca": "❌ Error en la traducció",
        "es": "❌ Error en la traducción",
        "en": "❌ Translation failed",
        "de": "❌ Übersetzung fehlgeschlagen",
        "fr": "❌ Échec de la traduction"
    },
    "admin_failed_load": {
        "ca": "Error en carregar les dades",
        "es": "Error al cargar los datos",
        "en": "Failed to load data",
        "de": "Fehler beim Laden der Daten",
        "fr": "Échec du chargement des données"
    },
    "admin_content_preview": {
        "ca": "Previsualització del contingut",
        "es": "Vista previa del contenido",
        "en": "Content Preview",
        "de": "Inhaltsvorschau",
        "fr": "Aperçu du contenu"
    }
}
