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
- Docker installed
- Docker Compose (included with Docker Desktop)

### Installation & Setup

**Build and Run with Docker Compose**
   
    docker-compose --verbose up --build 

**Access API documentation** (Swagger UI)

    http://127.0.0.1:8000/docs

**Unit test Coverage Report**

| Name                           |  Stmts    |  Miss    |  Cover | Missing |
|--------------------------------|-----------|----------|--------|---------|
| app/__init__.py                |  0        |    0     |  100%  |         |
| app/authentication/__init__.py |  0        |    0     |  100%  |         |
| app/authentication/oauth.py    |  19       |    0     |  100%  |         |
| app/authentication/token.py    |  11       |    0     |  100%  |         |
| app/config.py                  |  8        |    0     |  100%  |         |
| app/database.py                |  12       |    0     |  100%  |         |
| app/exceptions.py              |  14       |    0     |  100%  |         |
| app/main.py                    |  13       |    0     |  100%  |         |
| app/models/__init__.py         |  0        |    0     |  100%  |         |
| app/models/accounts.py         |  38       |    0     |  100%  |         |
| app/models/login.py            |  9        |    0     |  100%  |         |
| app/models/transfers.py        |  29       |    0     |  100%  |         |
| app/routers/__init__.py        |  0        |    0     |  100%  |         |
| app/routers/accounts.py        |  26       |    0     |  100%  |         |
| app/routers/login.py           |  17       |    0     |  100%  |         |
| app/routers/transfers.py       |  32       |    0     |  100%  |         |
| app/services/__init__.py       |  0        |    0     |  100%  |         |
| app/services/accounts.py       |  29       |    0     |  100%  |         |
| app/services/login.py          |  11       |    0     |  100%  |         |
| app/services/transfers.py      |  24       |    0     |  100%  |         |

