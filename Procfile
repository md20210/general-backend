web: (alembic upgrade head || echo "Alembic upgrade failed or skipped") && python create_mvp_tax_spain_tables.py && python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
