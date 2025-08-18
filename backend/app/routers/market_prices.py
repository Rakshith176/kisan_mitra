from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime
from typing import Optional

from ..db import get_db
from ..models import User
from ..services.karnataka_market_tool import KarnatakaMarketTool
from ..services.market_tool import MarketTool
from ..market_analysis.agmarknet_client import AgmarknetClient
from ..feed.generators import KarnatakaMarketGenerator

router = APIRouter(prefix="/market", tags=["market-prices"])

@router.get("/prices")
async def get_market_prices(
    crop: str = Query(..., description="Crop name (e.g., wheat, rice, maize)"),
    location: Optional[str] = Query(None, description="Location for market data"),
    client_id: Optional[str] = Query(None, description="Client ID for user context"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get market prices for a specific crop
    """
    try:
        # Verify user exists if client_id provided
        if client_id:
            user = await db.get(User, client_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        
        # Use the same market generator as the feed
        market_generator = KarnatakaMarketGenerator()
        
        # Create a simple context for the generator
        from ..feed.context import FeedContext
        ctx = FeedContext(
            db=db,
            client_id=client_id or "default",
            language="en",
            lat=12.9716,  # Default to Bangalore
            lon=77.5946,
            pincode=None,
            crop_ids=None,
        )
        
        try:
            # Generate market data using the same logic as feed
            market_card = await market_generator.generate(ctx)
            
            if market_card and market_card.data.get('items'):
                # Filter items for the specific crop
                crop_items = []
                for item in market_card.data['items']:
                    if crop.lower() in item.get('commodity', '').lower():
                        crop_items.append({
                            'market_name': item.get('market_name', ''),
                            'commodity': item.get('commodity', ''),
                            'modal_price': item.get('price_modal'),
                            'min_price': item.get('price_min'),
                            'max_price': item.get('price_max'),
                            'unit': item.get('unit', '₹/quintal'),
                            'date': item.get('date'),
                        })
                
                if crop_items:
                    return {
                        'prices': crop_items,
                        'commodity': crop,
                        'location': location or 'Karnataka',
                        'total_markets': len(crop_items),
                        'last_updated': datetime.now().isoformat(),
                        'source': 'Karnataka APMC'
                    }
        
        except Exception as e:
            # Fallback to sample data
            pass
        
        # Initialize market tools for fallback
        karnataka_tool = KarnatakaMarketTool()
        agmarknet_client = AgmarknetClient()
        
        # Return sample data that matches the feed structure
        sample_prices = []
        
        if crop.lower() == 'wheat':
            sample_prices = [
                {
                    'market_name': 'Karnataka APMC',
                    'commodity': 'Wheat - Local',
                    'modal_price': 3750.0,
                    'min_price': 3500.0,
                    'max_price': 4000.0,
                    'unit': '₹/quintal',
                    'date': datetime.now().isoformat(),
                },
                {
                    'market_name': 'Bangalore APMC',
                    'commodity': 'Wheat - Local',
                    'modal_price': 3750.0,
                    'min_price': 3500.0,
                    'max_price': 4000.0,
                    'unit': '₹/quintal',
                    'date': datetime.now().isoformat(),
                },
                {
                    'market_name': 'Mysore APMC',
                    'commodity': 'Wheat - Local',
                    'modal_price': 3700.0,
                    'min_price': 3450.0,
                    'max_price': 3950.0,
                    'unit': '₹/quintal',
                    'date': datetime.now().isoformat(),
                }
            ]
        elif crop.lower() == 'rice':
            sample_prices = [
                {
                    'market_name': 'Karnataka Central Market',
                    'commodity': 'Rice - Sona Masuri',
                    'modal_price': 4250.0,
                    'min_price': 4000.0,
                    'max_price': 4500.0,
                    'unit': '₹/quintal',
                    'date': datetime.now().isoformat(),
                },
                {
                    'market_name': 'Bangalore Central Market',
                    'commodity': 'Rice - Sona Masuri',
                    'modal_price': 4250.0,
                    'min_price': 4000.0,
                    'max_price': 4500.0,
                    'unit': '₹/quintal',
                    'date': datetime.now().isoformat(),
                }
            ]
        elif crop.lower() == 'maize':
            sample_prices = [
                {
                    'market_name': 'Karnataka Wholesale Market',
                    'commodity': 'Maize - Yellow',
                    'modal_price': 2200.0,
                    'min_price': 2000.0,
                    'max_price': 2400.0,
                    'unit': '₹/quintal',
                    'date': datetime.now().isoformat(),
                }
            ]
        elif crop.lower() == 'cotton':
            sample_prices = [
                {
                    'market_name': 'Karnataka Cotton Market',
                    'commodity': 'Cotton - Medium Staple',
                    'modal_price': 6500.0,
                    'min_price': 6200.0,
                    'max_price': 6800.0,
                    'unit': '₹/quintal',
                    'date': datetime.now().isoformat(),
                }
            ]
        elif crop.lower() == 'sugarcane':
            sample_prices = [
                {
                    'market_name': 'Karnataka Sugar Factory',
                    'commodity': 'Sugarcane - Fresh',
                    'modal_price': 320.0,
                    'min_price': 300.0,
                    'max_price': 340.0,
                    'unit': '₹/quintal',
                    'date': datetime.now().isoformat(),
                }
            ]
        
        return {
            'prices': sample_prices,
            'commodity': crop,
            'location': location or 'Karnataka',
            'total_markets': len(sample_prices),
            'last_updated': datetime.now().isoformat(),
            'source': 'Karnataka APMC (Sample Data)'
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching market prices: {str(e)}"
        )

@router.get("/prices/{crop}")
async def get_market_prices_by_crop(
    crop: str,
    location: Optional[str] = Query(None, description="Location for market data"),
    client_id: Optional[str] = Query(None, description="Client ID for user context"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get market prices for a specific crop (alternative endpoint)
    """
    return await get_market_prices(crop=crop, location=location, client_id=client_id, db=db)
