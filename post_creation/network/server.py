import uvicorn
from fastapi import FastAPI
from router import router 

app = FastAPI()
app.include_router(router)
uvicorn.run(app, host="127.0.0.1", port=8000)

