"""
FastAPI Application
REST API interface for Stock Knowledge & Fundamentals Engine
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
from engine import StockEngine
import config

# Initialize FastAPI app
app = FastAPI(
    title="Stock Knowledge & Fundamentals Engine",
    description="Deterministic, auditable stock data API - NO predictions, NO recommendations",
    version="1.0.0"
)

# Initialize engine
engine = StockEngine()


class StockRequest(BaseModel):
    """Request model for stock analysis"""
    symbol: str = Field(..., description="Stock symbol (e.g., RELIANCE, AAPL)")
    exchange: str = Field(default="NSE", description="Exchange (NSE, BSE, NASDAQ, etc.)")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    engine: str


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Stock Knowledge & Fundamentals Engine",
        "version": "1.0.0",
        "description": "Deterministic stock data processing - NO predictions, NO recommendations",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze/{symbol}",
            "snapshot": "/snapshot/{symbol}"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engine": "operational"
    }


@app.get("/analyze/{symbol}", tags=["Stock Analysis"])
async def analyze_stock(
    symbol: str,
    exchange: str = Query(default="NSE", description="Exchange (NSE, BSE, NASDAQ, etc.)")
):
    """
    Complete stock analysis with full historical data
    
    Returns:
        - Price data (current, change%, historical)
        - Fundamentals (revenue, profit, debt, PE, market cap, sector)
        - Technical indicators (RSI, MACD, MAs, volatility)
        - Derived signals (trend, valuation, risk, momentum)
    
    Note: This endpoint returns FACTUAL DATA ONLY. 
    No predictions, recommendations, or speculative analysis.
    """
    try:
        result = engine.analyze_stock(symbol.upper(), exchange.upper())
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing stock: {str(e)}"
        )


@app.get("/snapshot/{symbol}", tags=["Stock Analysis"])
async def get_snapshot(
    symbol: str,
    exchange: str = Query(default="NSE", description="Exchange (NSE, BSE, NASDAQ, etc.)")
):
    """
    Quick stock snapshot
    
    Same as /analyze but optimized for faster response
    Currently identical to analyze endpoint
    """
    try:
        result = engine.get_stock_snapshot(symbol.upper(), exchange.upper())
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching snapshot: {str(e)}"
        )


@app.post("/analyze", tags=["Stock Analysis"])
async def analyze_stock_post(request: StockRequest):
    """
    POST endpoint for stock analysis
    
    Alternative to GET /analyze/{symbol} for programmatic access
    """
    try:
        result = engine.analyze_stock(request.symbol.upper(), request.exchange.upper())
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing stock: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
