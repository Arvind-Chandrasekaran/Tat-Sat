from fastapi import FastAPI
from network.router import router 
import uvicorn

app = FastAPI(
        title="Post Creation Service",
        docs_url="/api-reference")
app.include_router(router)


"""
if __name__ == "__main__":
        uvicorn.run(app, host="127.0.0.1", port=8000)

        # 127.0.0.1 is a local ip address. For production change it 0.0.0.0 which will make it access any address in the production environment.

Better to use uvicorn run -  uvicorn server:app --host 127.0.0.1 --port 8000      
"""

