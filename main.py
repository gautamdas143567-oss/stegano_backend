import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
#from fastapi.staticfiles import StaticFiles

from steganography import encode, decode

app = FastAPI(title="Steganography API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/encode")
async def encode_file(
    file: UploadFile = File(...), 
    message: str = Form(...)
):
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG/JPG are supported.")
        
    try:
        image_bytes = await file.read()
        # 10MB size limit for encoding
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
            
        encoded_img_bytes = encode(image_bytes, message)
        
        # We always output PNG to preserve exactly our embedded LSB format
        base_name, _ = os.path.splitext(file.filename)
        return Response(
            content=encoded_img_bytes, 
            media_type="image/png", 
            headers={"Content-Disposition": f'attachment; filename="encoded_{base_name}.png"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decode")
async def decode_file(file: UploadFile = File(...)):
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG/JPG are supported.")
        
    try:
        image_bytes = await file.read()
        # 20MB size limit for decoding
        if len(image_bytes) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 20MB.")
            
        decoded_message = decode(image_bytes)
        return {"success": True, "message": decoded_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend directory for static serving
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
#app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
