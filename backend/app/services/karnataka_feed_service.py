from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from ..feed.types import CardGenerator
from ..feed.context import FeedContext
from ..feed.generators import KarnatakaMarketGenerator, KarnatakaLocationInsightsGenerator
from .karnataka_market_tool import karnataka_tool


class KarnatakaFeedService:
    """Intelligent feed service for Karnataka farmers with market insights"""
    
    def __init__(self):
        self.market_generator = KarnatakaMarketGenerator()
        self.insights_generator = KarnatakaLocationInsightsGenerator()
    
    async def generate_smart_feed(self, ctx: FeedContext, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Generate intelligent feed with market insights, price alerts, and recommendations
        
        Args:
            ctx: Feed context with user preferences and location
            limit: Maximum number of feed items to generate
            
        Returns:
            List of feed items with market insights
        """
        try:
            feed_items = []
            
            # Check if user is in Karnataka
            if not self._is_in_karnataka(ctx.lat, ctx.lon):
                logging.getLogger(__name__).info("User not in Karnataka, skipping Karnataka feed")
                return feed_items
            
            # Get user's nearest location
            nearest_location = self._get_nearest_karnataka_location(ctx.lat, ctx.lon)
            
            # 1. Generate crop-specific market cards
            crop_cards = await self.market_generator.generate(ctx)
            feed_items.extend(self._convert_cards_to_feed_items(crop_cards, "crop_market"))
            
            # 2. Generate location insights
            insight_cards = await self.insights_generator.generate(ctx)
            feed_items.extend(self._convert_cards_to_feed_items(insight_cards, "location_insights"))
            
            # 3. Generate price trend alerts
            trend_alerts = await self._generate_price_trend_alerts(ctx, nearest_location)
            feed_items.extend(trend_alerts)
            
            # 4. Generate market recommendations
            recommendations = await self._generate_market_recommendations(ctx, nearest_location)
            feed_items.extend(recommendations)
            
            # 5. Generate commodity highlights
            highlights = await self._generate_commodity_highlights(ctx, nearest_location)
            feed_items.extend(highlights)
            
            # Sort by relevance and recency
            feed_items.sort(key=lambda x: x.get('priority', 0), reverse=True)
            
            return feed_items[:limit]
            
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to generate Karnataka smart feed")
            return []
    
    async def _generate_price_trend_alerts(self, ctx: FeedContext, location: str) -> List[Dict[str, Any]]:
        """Generate price trend alerts for user's crops"""
        try:
            alerts = []
            
            # Get user's top crops
            if not ctx.crop_ids:
                return alerts
            
            # Get latest prices for each crop
            for crop_id in ctx.crop_ids[:3]:  # Top 3 crops
                try:
                    # This would need to be implemented based on your crop model
                    # For now, using a placeholder approach
                    crop_name = f"Crop_{crop_id}"  # You'd get actual crop name from DB
                    
                    # Get current prices using correct method name
                    current_prices = await karnataka_tool.get_commodity_prices(crop_name)
                    
                    if 'error' in current_prices or 'status' in current_prices and current_prices['status'] != 'success':
                        continue
                    
                    # Analyze price trends (simplified)
                    if current_prices.get('markets'):
                        avg_price = current_prices['summary']['avg_modal_price']
                        
                        # Create alert based on price level
                        if avg_price > 5000:  # High price alert
                            alert = {
                                'type': 'price_alert',
                                'priority': 8,
                                'title': f"High {crop_name} Prices in {location}",
                                'message': f"Current {crop_name} prices are ₹{avg_price:.0f}/quintal - good time to sell!",
                                'data': {
                                    'crop': crop_name,
                                    'location': location,
                                    'current_price': avg_price,
                                    'recommendation': 'Consider selling now',
                                    'markets': list(current_prices['markets'].keys())[:3]
                                },
                                'created_at': datetime.utcnow().isoformat(),
                                'language': ctx.language
                            }
                            alerts.append(alert)
                        
                        elif avg_price < 2000:  # Low price alert
                            alert = {
                                'type': 'price_alert',
                                'priority': 6,
                                'title': f"Low {crop_name} Prices in {location}",
                                'message': f"Current {crop_name} prices are ₹{avg_price:.0f}/quintal - consider waiting",
                                'data': {
                                    'crop': crop_name,
                                    'location': location,
                                    'current_price': avg_price,
                                    'recommendation': 'Consider waiting for better prices',
                                    'markets': list(current_prices['markets'].keys())[:3]
                                },
                                'created_at': datetime.utcnow().isoformat(),
                                'language': ctx.language
                            }
                            alerts.append(alert)
                
                except Exception as e:
                    logging.getLogger(__name__).warning(f"Failed to generate price alert for crop {crop_id}: {e}")
                    continue
            
            return alerts
            
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to generate price trend alerts")
            return []
    
    async def _generate_market_recommendations(self, ctx: FeedContext, location: str) -> List[Dict[str, Any]]:
        """Generate market recommendations based on current conditions"""
        try:
            recommendations = []
            
            # Get latest market overview using real method
            latest_prices = await karnataka_tool.get_prices_by_location(location)
            
            if 'error' in latest_prices or 'status' in latest_prices and latest_prices['status'] != 'success':
                return recommendations
            
            # Analyze market conditions
            total_commodities = latest_prices.get('total_commodities', 0)
            total_markets = latest_prices.get('total_markets', 0)
            
            if total_commodities > 20:  # Active market
                # Get sample prices from commodities data
                sample_prices = []
                for commodity, price_list in latest_prices.get('commodities', {}).items():
                    if price_list and len(price_list) > 0:
                        # Take first price entry for each commodity
                        sample_prices.append(price_list[0])
                
                recommendation = {
                    'type': 'market_recommendation',
                    'priority': 7,
                    'title': f"Active Market in {location}",
                    'message': f"High market activity with {total_commodities} commodities across {total_markets} markets",
                    'data': {
                        'location': location,
                        'total_commodities': total_commodities,
                        'total_markets': total_markets,
                        'recommendation': 'Good time for market visits and price comparison',
                        'best_time': 'Morning hours (9 AM - 12 PM)',
                        'markets_to_visit': sample_prices[:3]
                    },
                    'created_at': datetime.utcnow().isoformat(),
                    'language': ctx.language
                }
                recommendations.append(recommendation)
            
            # Check for specific commodity opportunities
            sample_prices = []
            for commodity, price_list in latest_prices.get('commodities', {}).items():
                if price_list and len(price_list) > 0:
                    # Take first price entry for each commodity
                    sample_prices.append(price_list[0])
            
            if sample_prices:
                # Find commodities with good price ranges
                for price_data in sample_prices[:5]:
                    commodity = price_data.get('commodity', '')
                    modal_price = price_data.get('modal_price', 0)
                    
                    if modal_price > 3000:  # Good price commodity
                        recommendation = {
                            'type': 'commodity_recommendation',
                            'priority': 6,
                            'title': f"Good {commodity} Prices in {location}",
                            'message': f"{commodity} prices are ₹{modal_price:.0f}/quintal - favorable for farmers",
                            'data': {
                                'commodity': commodity,
                                'location': location,
                                'price': modal_price,
                                'recommendation': 'Consider selling if you have stock',
                                'market': price_data.get('market', ''),
                                'district': price_data.get('district', '')
                            },
                            'created_at': datetime.utcnow().isoformat(),
                            'language': ctx.language
                        }
                        recommendations.append(recommendation)
                        break  # Only show one commodity recommendation
            
            return recommendations
            
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to generate market recommendations")
            return []
    
    async def _generate_commodity_highlights(self, ctx: FeedContext, location: str) -> List[Dict[str, Any]]:
        """Generate commodity highlights and insights"""
        try:
            highlights = []
            
            # Get latest prices for the location using real method
            latest_prices = await karnataka_tool.get_prices_by_location(location)
            
            if 'error' in latest_prices or 'status' in latest_prices and latest_prices['status'] != 'success':
                return highlights
            
            # Create commodity summary from real data
            commodities = latest_prices.get('commodities', {})
            if commodities:
                # Group by commodity type using real price data
                commodity_summary = {}
                for commodity, price_list in commodities.items():
                    if price_list and len(price_list) > 0:
                        # Extract modal prices from real data
                        modal_prices = [price.get('modal_price', 0) for price in price_list if price.get('modal_price')]
                        if modal_prices:
                            commodity_summary[commodity] = modal_prices
                
                # Create highlights for top commodities
                for commodity, prices in list(commodity_summary.items())[:3]:
                    if prices:
                        avg_price = sum(prices) / len(prices)
                        min_price = min(prices)
                        max_price = max(prices)
                        
                        highlight = {
                            'type': 'commodity_highlight',
                            'priority': 5,
                            'title': f"{commodity} Market Summary - {location}",
                            'message': f"Average price: ₹{avg_price:.0f}/quintal (Range: ₹{min_price:.0f} - ₹{max_price:.0f})",
                            'data': {
                                'commodity': commodity,
                                'location': location,
                                'avg_price': avg_price,
                                'min_price': min_price,
                                'max_price': max_price,
                                'price_variation': f"{((max_price - min_price) / avg_price * 100):.1f}%",
                                'insight': 'Price variation indicates market volatility',
                                'recommendation': 'Monitor prices daily for best selling opportunities'
                            },
                            'created_at': datetime.utcnow().isoformat(),
                            'language': ctx.language
                        }
                        highlights.append(highlight)
            
            return highlights
            
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to generate commodity highlights")
            return []
    
    def _convert_cards_to_feed_items(self, cards: List, source: str) -> List[Dict[str, Any]]:
        """Convert feed cards to feed items"""
        feed_items = []
        
        for card in cards:
            try:
                feed_item = {
                    'type': source,
                    'priority': 7,  # High priority for market data
                    'title': card.data.title.get('en', 'Market Information'),
                    'message': card.data.body_variants[0].get('en', 'Market price update'),
                    'data': {
                        'card_id': card.card_id,
                        'created_at': card.created_at.isoformat(),
                        'language': card.language,
                        'source': source
                    },
                    'created_at': card.created_at.isoformat(),
                    'language': card.language
                }
                
                # Add specific data based on card type
                if hasattr(card.data, 'items') and card.data.items:
                    feed_item['data']['market_items'] = [
                        {
                            'market': item.market_name,
                            'commodity': item.commodity,
                            'price': item.price_modal,
                            'unit': item.unit,
                            'distance': item.distance_km
                        }
                        for item in card.data.items[:5]  # Top 5 items
                    ]
                
                if hasattr(card.data, 'recommendations') and card.data.recommendations:
                    feed_item['data']['recommendations'] = [
                        rec.get('en', '') for rec in card.data.recommendations
                    ]
                
                feed_items.append(feed_item)
                
            except Exception as e:
                logging.getLogger(__name__).warning(f"Failed to convert card to feed item: {e}")
                continue
        
        return feed_items
    
    def _is_in_karnataka(self, lat: float, lon: float) -> bool:
        """Check if coordinates are in Karnataka region"""
        return 11.5 <= lat <= 18.5 and 74.0 <= lon <= 78.5
    
    def _get_nearest_karnataka_location(self, lat: float, lon: float) -> str:
        """Get nearest major Karnataka location"""
        karnataka_locations = {
            "Bangalore": (12.9716, 77.5946),
            "Mysore": (12.2958, 76.6394),
            "Mangalore": (12.9141, 74.8560),
            "Belgaum": (15.8497, 74.4977),
            "Gulbarga": (17.3297, 76.8343),
            "Dharwad": (15.4589, 75.0078),
            "Bellary": (15.1394, 76.9214),
            "Bijapur": (16.8244, 75.7154),
            "Raichur": (16.2076, 77.3563),
            "Kolar": (13.1370, 78.1298),
            "Tumkur": (13.3409, 77.1011),
            "Mandya": (12.5221, 76.9009),
            "Hassan": (13.0033, 76.1004),
            "Shimoga": (13.9299, 75.5681),
            "Chitradurga": (14.2264, 76.4008)
        }
        
        nearest = "Bangalore"
        min_distance = float('inf')
        
        for location, (loc_lat, loc_lon) in karnataka_locations.items():
            distance = ((lat - loc_lat) ** 2 + (lon - loc_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest = location
        
        return nearest


# Create global instance
karnataka_feed_service = KarnatakaFeedService()
