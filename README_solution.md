# Banking API (FastAPI)  

This is an internal banking system for the employees to handle customer requests such as account creation, retrieving account balance and history, transfer funds between accounts. This is created using FastAPI and PostgreSQL.
The backend API system is adequately tested with unit tests with 100% test coverage.

## Features  
 
- **Account Creation**: Create new accounts
- **Account View**: View the balance of the accounts
- **Transfers**: Transfer funds  
- **Transfer view**: View transfer history
- **Security**: JWT-based authentication.  
- **Comprehensive Tests**: Includes unit tests with `pytest`.

### Prerequisites
- Python 3.10+
- PostgreSQL
- Virtual Environment (venv or conda)
- Docker installed
- Docker Compose (included with Docker Desktop)

### Installation & Setup

**Docker**

1. **Build and Run with Docker Compose**
    docker-compose up --build


1. **Create the virtual environment**  
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

2. **Install dependencies** 
    pip3 install -r requirements.txt

3. **Setup environment variables** 
    In your local postgres database create a database with the following credentials
    DATABASE_URL=postgresql://postgres:password@localhost:5432/bank
    SECRET_KEY=your_secret_key

4. **Start the API server** 
    uvicorn main:app --reload

**Access API documentation** (Swagger UI)
    http://127.0.0.1:8000/docs

**Running the test**
    pytest --cov=app --cov-report=term-missing

**Unit test Coverage Report**

Name                         Stmts   Miss  Cover   Missing
----------------------------------------------------------
authentication\__init__.py       0      0   100%
authentication\oauth.py         19      0   100%
authentication\token.py         11      0   100%
db\__init__.py                   0      0   100%
db\database.py                  13      0   100%
db\models.py                    29      0   100%
db\schemas.py                   39      0   100%
routers\__init__.py              0      0   100%
routers\accounts.py             30      0   100%
routers\login.py                17      0   100%
routers\transfers.py            35      0   100%
utils\__init__.py                0      0   100%
utils\util.py                   45      0   100%
----------------------------------------------------------
TOTAL                          238      0   100%