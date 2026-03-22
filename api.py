from fastapi import FastAPI

from db import search_catalog, get_catalog_perfume, get_notes_for_perfume

app = FastAPI()


@app.get("/perfumes")
def get_perfumes(q: str = ""):
    return search_catalog(q) if q else search_catalog("", limit=100)


@app.get("/perfumes/{perfume_id}")
def get_perfume(perfume_id: int):
    perfume = get_catalog_perfume(perfume_id)
    if not perfume:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    perfume["notes"] = get_notes_for_perfume(perfume_id)
    return perfume

@app.get("/")
def root():
    return {"message": "Aromance API is running"}