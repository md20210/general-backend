"""Update bar info with multilingual data

Revision ID: 20260110_update_bar
Revises: 20260110_add_bar_tables
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '20260110_update_bar'
down_revision = '20260110_add_bar_tables'
branch_labels = None
depends_on = None


def upgrade():
    """Update bar_info table with multilingual descriptions and corrected data."""

    # Update existing bar_info record with multilingual data
    op.execute("""
        UPDATE bar_info SET
            description = '{
                "ca": "Bar Ca l''Elena és un tradicional bar-restaurant espanyol amb plats casolans, tapes, peix i carn frescos. Conegut per les sardines a la brasa, la truita espanyola i els vins locals. Gran terrassa assolellada, servei amable.",
                "es": "Bar Ca l''Elena es un tradicional bar-restaurante español con platos caseros, tapas, pescado y carne frescos. Conocido por las sardinas a la parrilla, la tortilla española y los vinos locales. Gran terraza soleada, servicio amable.",
                "en": "Bar Ca l''Elena is a traditional Spanish bar-restaurant with homemade dishes, tapas, fresh fish and meat. Known for grilled sardines, Spanish omelette and local wines. Large sunny terrace, friendly service.",
                "de": "Bar Ca l''Elena ist ein traditionelles spanisches Bar-Restaurant mit hausgemachten Gerichten, Tapas, frischem Fisch und Fleisch. Bekannt für gegrillte Sardinen, Spanische Omelette und lokale Weine. Große sonnige Terrasse, freundlicher Service.",
                "fr": "Bar Ca l''Elena est un bar-restaurant espagnol traditionnel avec des plats faits maison, des tapas, du poisson et de la viande frais. Connu pour les sardines grillées, l''omelette espagnole et les vins locaux. Grande terrasse ensoleillée, service amical."
            }'::jsonb,
            location_lat = '41.35931',
            location_lng = '2.12432',
            rating = '4.0/5 auf Google',
            featured_items = '[
                {
                    "name": "Fideua",
                    "description": {
                        "ca": "Plat tradicional català de fideus amb marisc",
                        "es": "Plato tradicional catalán de fideos con mariscos",
                        "en": "Traditional Catalan seafood noodle dish",
                        "de": "Traditionelles katalanisches Nudelgericht mit Meeresfrüchten",
                        "fr": "Plat traditionnel catalan de nouilles aux fruits de mer"
                    }
                },
                {
                    "name": "Vermut",
                    "description": {
                        "ca": "Vermut espanyol tradicional",
                        "es": "Vermut español tradicional",
                        "en": "Traditional Spanish vermouth",
                        "de": "Traditioneller spanischer Wermut",
                        "fr": "Vermouth espagnol traditionnel"
                    }
                },
                {
                    "name": "Vino",
                    "description": {
                        "ca": "Vins locals",
                        "es": "Vinos locales",
                        "en": "Local wines",
                        "de": "Lokale Weine",
                        "fr": "Vins locaux"
                    }
                },
                {
                    "name": "Ensalada Con Queso de Cabra",
                    "description": {
                        "ca": "Amanida amb formatge de cabra",
                        "es": "Ensalada con queso de cabra",
                        "en": "Salad with goat cheese",
                        "de": "Salat mit Ziegenkäse",
                        "fr": "Salade au fromage de chèvre"
                    }
                },
                {
                    "name": "Huevos Con Bacon",
                    "description": {
                        "ca": "Ous amb cansalada",
                        "es": "Huevos con bacon",
                        "en": "Eggs with bacon",
                        "de": "Eier mit Speck",
                        "fr": "Œufs au bacon"
                    }
                },
                {
                    "name": "Puding",
                    "description": {
                        "ca": "Púding casolà",
                        "es": "Pudín casero",
                        "en": "Homemade pudding",
                        "de": "Hausgemachter Pudding",
                        "fr": "Pudding fait maison"
                    }
                },
                {
                    "name": "Cafe Con Leche",
                    "description": {
                        "ca": "Cafè amb llet",
                        "es": "Café con leche",
                        "en": "Coffee with milk",
                        "de": "Kaffee mit Milch",
                        "fr": "Café au lait"
                    }
                },
                {
                    "name": "Tarta de Queso",
                    "description": {
                        "ca": "Pastís de formatge",
                        "es": "Tarta de queso",
                        "en": "Cheesecake",
                        "de": "Käsekuchen",
                        "fr": "Gâteau au fromage"
                    }
                }
            ]'::jsonb,
            updated_at = NOW()
        WHERE id = 1;
    """)


def downgrade():
    """Revert to single-language descriptions."""
    op.execute("""
        UPDATE bar_info SET
            description = 'Bar Ca l''Elena ist ein traditionelles spanisches Bar-Restaurant mit hausgemachten Gerichten, Tapas, frischem Fisch und Fleisch. Bekannt für gegrillte Sardinen, Spanische Omelette und lokale Weine. Große sonnige Terrasse, freundlicher Service.',
            location_lat = '41.3613',
            location_lng = '2.1164',
            rating = '2.8/5 auf TripAdvisor (12 Bewertungen)',
            updated_at = NOW()
        WHERE id = 1;
    """)
