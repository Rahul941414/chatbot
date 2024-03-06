from fastapi import Depends, FastAPI, HTTPException,Request,Form
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.responses import HTMLResponse, RedirectResponse
import asyncio
from typing import AsyncIterable
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.schema import HumanMessage
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
app = FastAPI()
class Message(BaseModel):
    content: str


async def send_message(content: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    model = ChatOpenAI(
        streaming=True,
        verbose=True,
        callbacks=[callback],
        api_key="your_api_key",
    )

    task = asyncio.create_task(
        model.agenerate(messages=[[HumanMessage(content=content)]])
    )

    try:
        async for token in callback.aiter():
            yield token
    except Exception as e:
        print(f"Caught exception: {e}")
    finally:
        callback.done.set()

    await task


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_users(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return templates.TemplateResponse("welcome.html", {"request": request, "users": users})

@app.post("/users/", response_class=HTMLResponse)
async def create_user(request: Request, username: str = Form(...), email: str = Form(...),db: Session = Depends(get_db)):
    print("Username:", username)
    print("Email:", email)
    # Add your logic to create the user here
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        return RedirectResponse(url="/")
        # raise HTTPException(status_code=400, detail="Email already registered")
    else :
     db_user = models.User(email=email, username=username)
     db.add(db_user)
     db.commit()
     db.refresh(db_user)
     print("Succesfully pushed into db")
     return RedirectResponse(url="/")

@app.post("/", response_class=HTMLResponse)
async def read_users(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return templates.TemplateResponse("welcome.html", {"request": request, "users": users})


@app.get("/users/", response_class=HTMLResponse)
async def read_users(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    print(users)
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": users}
    )

@app.get('/stream_chat',response_class=HTMLResponse)
async def openchatbot(request: Request):
    return templates.TemplateResponse("chatbot.html",{"request": request})
    

@app.post("/stream", response_class=HTMLResponse)
async def stream_chat(request: Request, text: str = Form(...),db: Session = Depends(get_db)):
    # Assuming send_message returns an asynchronous generator
    generator = send_message(text)
    
    # Accumulate the data from the asynchronous generator into a string
    data = ""
    async for item in generator:
        data += item
    print(data)
    db_user = models.Item(title=text, description=data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print("Succesfully pushed into db")
    return templates.TemplateResponse("chatbot.html", {"request": request, "text": data})


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items