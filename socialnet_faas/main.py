import logging
from fastapi import FastAPI, Request, HTTPException
from importlib import import_module
import traceback
import time
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logging.error(f"Unhandled Exception: {e}")
        raise
    process_time = time.time() - start_time
    logging.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response


@app.post("/function/{func_name}")
async def call_function(func_name: str, request: Request):
    try:
        body = await request.body()
        logging.info(f"Calling function: {func_name} with body: {body}")

        module = import_module(f"functions.{func_name}.handler")
        if not hasattr(module, "handler"):
            raise HTTPException(status_code=400, detail="Missing `handler()`")

        handler = getattr(module, "handler")
        data = await request.json()
        result = await handler(data)  # if callable(getattr(handler, "__await__", None)) else handler(data)

        logging.info(f"Function {func_name} returned: {result}")
        return {"result": result}

    except ModuleNotFoundError:
        raise HTTPException(status_code=404, detail=f"Function {func_name} not found.")

    except Exception as e:
        logging.error(f"Error in function {func_name}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", port=8800, reload=True)  # reload=True enables hot reload
