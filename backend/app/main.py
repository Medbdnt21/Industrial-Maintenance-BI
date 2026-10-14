from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import alerts, machines, overview, timeseries

app = FastAPI(title="Industrial Maintenance BI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(overview.router)
app.include_router(machines.router)
app.include_router(alerts.router)
app.include_router(timeseries.router)
