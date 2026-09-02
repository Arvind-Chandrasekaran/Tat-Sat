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

        Better to use uvicorn run -  uvicorn server:app --host 127.0.0.1 --port 8000      

        # 127.0.0.1 is a local ip address. 
        # For production use 0.0.0.0 which will make it access any address in the production environment.
        # Or assign a private ip address if a reverse proxy will connect to in a private network rather than a client directly. 


"""

