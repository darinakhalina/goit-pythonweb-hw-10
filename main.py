from fastapi import FastAPI

from src.api import contacts, utils

from src.conf.config import settings

app = FastAPI()

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
