# app/routes/item_routes.py

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Body
from sqlalchemy.orm import Session
from app.models import Item, SessionLocal
from app.schemas import ItemCreate, ItemRead

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Route zum Erstellen eines neuen Items mit einem hochgeladenen GLTF-Modell
@router.post("/items/", response_model=ItemRead)
def create_item(
        item: ItemCreate = Body(...),  # Korrekt aus dem Request Body
        uploaded_file: UploadFile = File(...),  # Datei-Upload
        db: Session = Depends(get_db)
):
    """
    Speichert ein neues Item und eine hochgeladene GLTF-Datei als Blob in der Datenbank.
    """
    # Überprüfen, ob die hochgeladene Datei eine GLTF-Datei ist
    if not uploaded_file.filename.endswith((".gltf", ".glb")):
        raise HTTPException(status_code=400, detail="Invalid file format. Only .gltf or .glb files are allowed.")

    # Liest den Inhalt der hochgeladenen GLTF-Datei
    model_data = uploaded_file.file.read()

    # Erstellt ein neues Item mit den Metadaten und den Modell-Binärdaten
    db_item = Item(name=item.name, description=item.description, model_data=model_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item  # Gibt das neu erstellte Item zurück


# Endpunkt zum Abrufen einer Liste von Elementen
@router.get("/items/", response_model=list[ItemRead])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Ruft eine Liste von Elementen aus der Datenbank ab, optional mit Pagination.

    Args:
    - skip: Die Anzahl der Elemente, die übersprungen werden sollen (für Pagination).
    - limit: Die maximale Anzahl der Elemente, die zurückgegeben werden sollen (für Pagination).
    - db: Die Datenbankverbindung (Session).

    Returns:
    - Eine Liste von Elementen.
    """
    items = db.query(Item).offset(skip).limit(limit).all()
    return items


# Endpunkt zum Abrufen eines spezifischen 3D-Modells basierend auf der Item-ID
@router.get("/items/{item_id}/model")
def read_item_model(item_id: int, db: Session = Depends(get_db)):
    """
    Ruft das 3D-Modell eines spezifischen Elements aus der Datenbank ab.

    Args:
    - item_id: Die ID des Elements, dessen 3D-Modell abgerufen werden soll.
    - db: Die Datenbankverbindung (Session).

    Returns:
    - Ein Dictionary mit dem Dateinamen und den binären Daten des Modells.
    """
    item = db.query(Item).filter(item_id == Item.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"filename": f"model_{item_id}.bin", "model_data": item.model_data}
