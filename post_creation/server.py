from fastapi import FastAPI
from network.router import router 
import uvicorn

app = FastAPI(
        title="Post Creation Service",
        docs_url="/api-reference")
app.include_router(router)

uvicorn.run(app, host="127.0.0.1", port=8000)

