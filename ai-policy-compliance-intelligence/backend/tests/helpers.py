from app.database.mongodb import store


def reset_local_store() -> None:
    if hasattr(store, "_write"):
        store._write({"documents": [], "chunks": []})
