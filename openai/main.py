from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/v1/models")
async def list():
    return {
        "data": [
            {
                "id": "deepseek-r1",
                "object": "model",
                "owned_by": "yuanbao",
            },
            {
                "id": "deepseek-v3",
                "object": "model",
                "owned_by": "yuanbao",
            },
            {
                "id": "hunyuan",
                "object": "model",
                "owned_by": "yuanbao",

            },
            {
                "id": "hunyuan-t1",
                "object": "model",
                "owned_by": "yuanbao",
            }
        ],
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)