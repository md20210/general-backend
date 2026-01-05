"""Add klassentreffen_participants table

Revision ID: 20260105_klassentreffen
Revises: fix_cv_showcase_002
Create Date: 2026-01-05

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '20260105_klassentreffen'
down_revision = 'fix_cv_showcase_002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create klassentreffen_participants table and populate with names."""
    # Create table
    op.create_table(
        'klassentreffen_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('consent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('registered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_klassentreffen_participants_id'), 'klassentreffen_participants', ['id'], unique=False)
    op.create_index(op.f('ix_klassentreffen_participants_name'), 'klassentreffen_participants', ['name'], unique=True)

    # Insert all 133 names
    names = [
        "Carsten Dobschall", "Michael Dütting", "Ansgar Ellermann", "Irene Etmann (jetzt: Bils)",
        "Klaus Gunnemann", "Stefan Hille", "Peter Hoppe", "Martina Höptner (jetzt: Hecker)",
        "Stephan Horstmann", "Ralf Huihsen", "Stephan Kappen", "Klaus Klöker",
        "Bernd Kottmann", "Klaus Loskant", "Sabine Lünnemann (jetzt: Vortkamp)", "Andreas Menke",
        "Stephan Quiel", "Roland Rietkoetter", "Olaf Saphörster", "Annette Schwarte",
        "Andre Sickmann", "Thomas Siebert", "Eike Silvester Wiemann", "Magnus Wolke",
        "Heinz Wöstmann", "Gernot Becker", "Christiane Buck (jetzt: Schmidt)", "Michael Dabrock",
        "Jochen Dahm", "Melanie Dörholt", "Birgit Dohmen (jetzt: Decker)", "Patric Droste zu Senden",
        "Roman Feil", "Georg Fels", "Andreas Golf", "Klaus Günther",
        "Volker Hahn", "Karin Harnisch", "Frank Kloppenburg", "Dirk Köwener",
        "Harald Kröger", "Peter Lahrkamp", "Bernd Lehmann", "Katrin Lumma",
        "Mechthild Lütke Kleimann", "Silke Mersmann (jetzt: Born)", "Dirk Neufelder", "Ursula Neumann",
        "Josef Niehoff", "Stefan Niggemeyer", "Gerhard Nowak", "Madueke Okegwo",
        "Renate Ostermeyer", "Bettina Otto", "Mechthild Rickert", "Axel Ritter",
        "Eva Sandhage (jetzt: Wehmeyer-Sandhage)", "Ralf Schupp", "Bettina Seidensticker", "Martin Sommermeyer",
        "Peter Sperling", "Wolfgang Spille", "Benedikt Sudbrock", "Thomas Terrahe",
        "Volker Welp", "Susanne Wettwer", "Uwe Wilme", "Reinhold Albrecht",
        "Peter Alt-Epping", "Konstanze Bader", "Michael Beneke", "Marc Böddecker",
        "Georg Bratke", "Carsten Brüning", "Andreas Döpp", "Jürgen Dorgeist",
        "Oliver Dütschke", "Dirk Eberhardt", "Reinhild Erling", "Marie-Luise Ernst (jetzt: Terrahe)",
        "Mathias Eßing", "Karsten Evers", "Christian Fischer", "Sabine Gädeke",
        "Veronica Gohl", "Anne Grewe (jetzt: Vetter)", "Monika Haye (jetzt: Gaedeke)", "Jörg Hecker",
        "Andrea Heller", "Ingo Hentschel", "Jörg Hesselink", "Annegret Hobbeling",
        "Markus Hock", "Thomas Hörnemann", "Bettina Horstmann", "Volker Hund",
        "Marcus Janotta", "Stephan Kehr", "Renate Kellers (jetzt:? Herzog)", "Martin Kintrup",
        "Annette Knirim", "Bernd Korves", "Michael Laermann", "Petra Lindner (jetzt: Hubeny-Lindner)",
        "Dominik Löer", "Friedrich Lührmann", "Arno Lutz", "David Lützenkirchen",
        "Henning Meißner", "Frank Mense", "Thomas Mertens", "Matthias Michalczyk",
        "Oliver Müllmann", "Anja Neumann-Wedekindt", "Jürgen Proch", "David Rehmann",
        "Katrin Richter", "Barbara Sauer", "Fabian Sauerwald", "Tobias Sauerwald",
        "Klaus Schaphorn", "Thomas Schleicher", "Anne Schlummer", "Frank Schulte",
        "Ludger Schwarte", "Harald Siegmund", "Andreas Südbeck", "Helmut Südmersen",
        "Wolfgang Thomas", "Clarus von der Horst", "Kai Wengler", "Melanie Wessels",
        "Roland Wilmes"
    ]

    # Bulk insert
    participants_table = sa.table(
        'klassentreffen_participants',
        sa.column('name', sa.String)
    )

    op.bulk_insert(
        participants_table,
        [{'name': name} for name in names]
    )


def downgrade() -> None:
    """Drop klassentreffen_participants table."""
    op.drop_index(op.f('ix_klassentreffen_participants_name'), table_name='klassentreffen_participants')
    op.drop_index(op.f('ix_klassentreffen_participants_id'), table_name='klassentreffen_participants')
    op.drop_table('klassentreffen_participants')
