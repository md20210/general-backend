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
        "ca": "Subscriu-te al nostre butlletí",
        "es": "Suscríbete a nuestro boletín",
        "en": "Subscribe to our newsletter",
        "de": "Abonniere unseren Newsletter",
        "fr": "Abonnez-vous à notre newsletter"
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
    }
}
