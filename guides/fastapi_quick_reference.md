# 🚀 FastAPI Quick Reference Card

## 📋 Essential FastAPI Concepts for This Project

### 🏗️ Application Setup
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    app.state.database = make_database()
    yield  # App runs here
    # Cleanup
    app.state.database.teardown()

app = FastAPI(
    title="arXiv Paper Curator API",
    version="0.1.0",
    lifespan=lifespan
)
```

### 🛣️ Router Setup
```python
from fastapi import APIRouter

router = APIRouter(prefix="/papers", tags=["papers"])

@router.get("/{arxiv_id}")
def get_paper(arxiv_id: str):
    return {"arxiv_id": arxiv_id}

# Register in main.py
app.include_router(router)
```

### 📊 Pydantic Models
```python
from pydantic import BaseModel, Field
from typing import List

class PaperBase(BaseModel):
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="Authors")

class PaperResponse(PaperBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy models
```

### 🔌 Dependency Injection
```python
from typing import Annotated
from fastapi import Depends

def get_db_session() -> Session:
    with database.get_session() as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db_session)]

@router.get("/{arxiv_id}")
def get_paper(db: SessionDep, arxiv_id: str):
    return db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
```

### ⚠️ Error Handling
```python
from fastapi import HTTPException

@router.get("/{arxiv_id}")
def get_paper(arxiv_id: str):
    paper = find_paper(arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper
```

### 🧪 Testing
```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_paper():
    response = client.get("/papers/2401.00001")
    assert response.status_code == 200
```

### 📖 API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 🚀 Running the App
```bash
# Development
uvicorn src.main:app --reload

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Docker
docker compose up api
```

### 🎯 Key Decorators
- `@app.get()` - GET endpoint
- `@app.post()` - POST endpoint
- `@app.put()` - PUT endpoint
- `@app.delete()` - DELETE endpoint
- `@router.get()` - Router endpoint

### 📝 Common Parameters
- `response_model=Model` - Response validation
- `status_code=200` - HTTP status code
- `tags=["group"]` - API documentation grouping
- `summary="Description"` - Endpoint description

### 🔧 Type Hints
```python
# Path parameters
arxiv_id: str = Path(..., regex=r"^\d{4}\.\d{4,5}$")

# Query parameters
limit: int = Query(default=100, le=1000)

# Request body
paper: PaperCreate

# Response
def get_paper() -> PaperResponse:
    return paper
```

### 🎨 Best Practices
1. ✅ Use type hints everywhere
2. ✅ Use Pydantic models for validation
3. ✅ Use dependency injection
4. ✅ Handle errors gracefully
5. ✅ Use meaningful status codes
6. ✅ Document your endpoints

### 🔄 Data Flow
```
HTTP Request → Router → Dependency Injection → Business Logic → Response
     ↓              ↓              ↓              ↓              ↓
Validation    Dependencies    Repository    Domain Model    JSON Response
```

This quick reference covers the essential FastAPI concepts used in the arXiv Paper Curator project! 