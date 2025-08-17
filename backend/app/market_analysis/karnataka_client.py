from __future__ import annotations

import asyncio
import re
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from .schemas import MandiPriceRow


class KarnatakaClient:
    """Client for Karnataka government agricultural market data website"""
    
    def __init__(self):
        self.base_url = "https://krama.karnataka.gov.in"
        self.reports_url = f"{self.base_url}/reports/Main_Rep"
        self.session = None
        self._viewstate = None
        self._viewstate_generator = None
        self._event_validation = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def _get_form_tokens(self) -> Tuple[str, str, str]:
        """Get ASP.NET form tokens from the main page"""
        try:
            response = await self.session.get(self.reports_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract ASP.NET form tokens
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
            event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})
            
            self._viewstate = viewstate['value'] if viewstate else ""
            self._viewstate_generator = viewstate_generator['value'] if viewstate_generator else ""
            self._event_validation = event_validation['value'] if event_validation else ""
            
            return self._viewstate, self._viewstate_generator, self._event_validation
            
        except Exception as e:
            print(f"❌ Error getting form tokens: {e}")
            return "", "", ""
    
    async def get_market_prices_by_location(
        self, 
        location: str, 
        report_date: Optional[date] = None,
        report_type: str = "M"  # M=MarketWise, C=Commoditywise, L=Latest
    ) -> List[MandiPriceRow]:
        """
        Get market prices for a specific location
        
        Args:
            location: District or market name
            report_date: Date for the report (defaults to today)
            report_type: Type of report (M, C, L, S)
            
        Returns:
            List of market price records
        """
        try:
            # First, get the main page to establish session
            print("🔑 Establishing session...")
            main_response = await self.session.get(self.reports_url)
            
            if main_response.status_code != 200:
                print(f"❌ Failed to load main page: {main_response.status_code}")
                return []
            
            print("✅ Session established")
            
            # Now try to access the data URLs with proper referrer
            url_mapping = {
                "S": f"{self.base_url}/reports/state",  # State Level Report
                "M": f"{self.base_url}/reports/DailyMar",  # Daily Market Report
                "C": f"{self.base_url}/reports/DailyMar",  # Commoditywise (use DailyMar)
                "L": f"{self.base_url}/reports/DailyMar"   # Latest (use DailyMar)
            }
            
            data_url = url_mapping.get(report_type, url_mapping["S"])
            
            print(f"🔗 Fetching data from: {data_url}")
            
            # Try to access with proper referrer and session
            headers = {
                "Referer": self.reports_url,
                "Origin": self.base_url,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.0; Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            response = await self.session.get(data_url, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ Successfully fetched data from {data_url}")
                return await self._parse_price_data(response.text, location)
            else:
                print(f"❌ Failed to fetch data: {response.status_code}")
                
                # If direct access fails, try the form submission approach as fallback
                print("🔄 Trying form submission as fallback...")
                return await self._try_form_submission(location, report_date, report_type)
            
        except Exception as e:
            print(f"❌ Error fetching market prices: {e}")
            return []
    
    async def get_commodity_prices(
        self, 
        commodity: str, 
        report_date: Optional[date] = None
    ) -> List[MandiPriceRow]:
        """
        Get prices for a specific commodity across markets
        
        Args:
            commodity: Name of the commodity
            report_date: Date for the report (defaults to today)
            
        Returns:
            List of market price records
        """
        try:
            # Use the DailyMar URL for commodity data
            data_url = f"{self.base_url}/reports/DailyMar"
            
            print(f"🔗 Fetching commodity data from: {data_url}")
            
            # Fetch data directly from the working URL
            response = await self.session.get(data_url)
            
            if response.status_code == 200:
                print(f"✅ Successfully fetched commodity data from {data_url}")
                # Parse the response for commodity data
                return await self._parse_commodity_data(response.text, commodity)
            else:
                print(f"❌ Failed to fetch commodity data: {response.status_code}")
                return []
            
        except Exception as e:
            print(f"❌ Error fetching commodity prices: {e}")
            return []
    
    async def _parse_price_data(self, html_content: str, location: str) -> List[MandiPriceRow]:
        """Parse HTML response for market price data"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            price_rows = []
            
            print(f"🔍 Parsing HTML content ({len(html_content)} characters)")
            
            # Look for the main data table - the website shows "State Level Daily Report"
            tables = soup.find_all('table')
            print(f"📊 Found {len(tables)} tables")
            
            for i, table in enumerate(tables):
                print(f"  Table {i+1}: {len(table.find_all('tr'))} rows")
                
                # Look for table with price data (should have columns like Commodity, Variety, Market, Min, Max, Modal)
                rows = table.find_all('tr')
                
                # Skip header rows, look for data rows
                for row in rows[1:]:  # Skip first row (header)
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 7:  # Expecting: Commodity, Variety, Grade, Market, Arrival, Unit, Min, Max, Modal
                        try:
                            # Extract data from cells based on the actual website structure
                            commodity = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                            variety = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                            grade = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                            market = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                            arrival = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                            unit = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                            min_price = self._extract_price(cells[6].get_text(strip=True)) if len(cells) > 6 else None
                            max_price = self._extract_price(cells[7].get_text(strip=True)) if len(cells) > 7 else None
                            modal_price = self._extract_price(cells[8].get_text(strip=True)) if len(cells) > 8 else None
                            
                            # Skip rows without essential data
                            if not commodity or not market or commodity.lower() in ['commodity', 'total']:
                                continue
                                
                            # Filter by location if specified
                            if location and location.lower() not in market.lower():
                                continue
                            
                            # Create price row
                            price_row = MandiPriceRow(
                                market=market,
                                state="Karnataka",
                                district=self._extract_district(market),
                                commodity=commodity,
                                variety=variety,
                                unit=unit or "Quintal",
                                modal=modal_price or 0.0,
                                min_price=min_price,
                                max_price=max_price,
                                arrivals=self._extract_number(arrival),
                                date=date.today()
                            )
                            
                            price_rows.append(price_row)
                            print(f"  ✅ Added: {commodity} at {market} - ₹{modal_price}/quintal")
                            
                        except Exception as e:
                            print(f"  ⚠️ Error parsing row: {e}")
                            continue
            
            print(f"📈 Successfully parsed {len(price_rows)} price records")
            return price_rows
            
        except Exception as e:
            print(f"❌ Error parsing price data: {e}")
            return []
    
    async def _parse_commodity_data(self, html_content: str, commodity: str) -> List[MandiPriceRow]:
        """Parse HTML response for commodity-specific price data"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            price_rows = []
            
            print(f"🔍 Parsing commodity data for {commodity}")
            
            # Look for tables with commodity data
            tables = soup.find_all('table')
            
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                
                # Skip header rows, look for data rows
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 7:  # Same structure as price data
                        try:
                            # Extract data from cells
                            row_commodity = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                            variety = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                            grade = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                            market = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                            arrival = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                            unit = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                            min_price = self._extract_price(cells[6].get_text(strip=True)) if len(cells) > 6 else None
                            max_price = self._extract_price(cells[7].get_text(strip=True)) if len(cells) > 7 else None
                            modal_price = self._extract_price(cells[8].get_text(strip=True)) if len(cells) > 8 else None
                            
                            # Filter by commodity if specified
                            if commodity and commodity.lower() not in row_commodity.lower():
                                continue
                                
                            # Skip rows without essential data
                            if not row_commodity or not market or row_commodity.lower() in ['commodity', 'total']:
                                continue
                            
                            # Create price row
                            price_row = MandiPriceRow(
                                market=market,
                                state="Karnataka",
                                district=self._extract_district(market),
                                commodity=row_commodity,
                                variety=variety,
                                unit=unit or "Quintal",
                                modal=modal_price or 0.0,
                                min_price=min_price,
                                max_price=max_price,
                                arrivals=self._extract_number(arrival),
                                date=date.today()
                            )
                            
                            price_rows.append(price_row)
                            print(f"  ✅ Added: {row_commodity} at {market} - ₹{modal_price}/quintal")
                            
                        except Exception as e:
                            print(f"  ⚠️ Error parsing commodity row: {e}")
                            continue
            
            print(f"📈 Successfully parsed {len(price_rows)} commodity records")
            return price_rows
            
        except Exception as e:
            print(f"❌ Error parsing commodity data: {e}")
            return []
    
    async def _try_form_submission(
        self, 
        location: str, 
        report_date: Optional[date] = None,
        report_type: str = "M"
    ) -> List[MandiPriceRow]:
        """Fallback method: try form submission if direct URL access fails"""
        try:
            print("📝 Attempting form submission...")
            
            # Get form tokens first
            await self._get_form_tokens()
            
            # Prepare form data
            if report_date is None:
                report_date = date.today()
                
            form_data = {
                "__VIEWSTATE": self._viewstate,
                "__VIEWSTATEGENERATOR": self._viewstate_generator,
                "__EVENTVALIDATION": self._event_validation,
                "_ctl0:MainContent:TxtDate": report_date.strftime("%d/%m/%Y"),
                "_ctl0:MainContent:RadBtnSel": report_type,
                "_ctl0:MainContent:BtnRep": "View Report"
            }
            
            # Submit the form
            response = await self.session.post(
                self.reports_url,
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                print("✅ Form submission successful")
                return await self._parse_price_data(response.text, location)
            else:
                print(f"❌ Form submission failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Form submission error: {e}")
            return []
    
    def _extract_price(self, price_text: str) -> float:
        """Extract numeric price from text"""
        try:
            # Remove currency symbols and non-numeric characters
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                return float(price_match.group().replace(',', ''))
            return 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    def _extract_number(self, text: str) -> int:
        """Extract numeric value from text (e.g., '100' from '100 quintals')"""
        try:
            match = re.search(r'\d+', text)
            if match:
                return int(match.group())
            return 0
        except (ValueError, AttributeError):
            return 0
    
    def _extract_district(self, market_name: str) -> str:
        """Extract district from market name (heuristic approach)"""
        # Common Karnataka districts
        districts = [
            "Bangalore", "Mysore", "Mangalore", "Belgaum", "Gulbarga", 
            "Dharwad", "Bellary", "Bijapur", "Raichur", "Kolar",
            "Tumkur", "Mandya", "Hassan", "Shimoga", "Chitradurga"
        ]
        
        for district in districts:
            if district.lower() in market_name.lower():
                return district
        
        return "Unknown"

    async def get_market_prices_from_main_page(self, location: str = None) -> List[MandiPriceRow]:
        """
        Get market prices from the main page (which actually contains data)
        This bypasses the broken reports system
        """
        try:
            print("🏠 Fetching data from main page...")
            
            # The main page actually contains the market data
            main_url = f"{self.base_url}/"
            response = await self.session.get(main_url)
            
            if response.status_code == 200:
                print("✅ Main page loaded successfully")
                print(f"📄 Content length: {len(response.text)} characters")
                
                # Parse the main page for market data
                return await self._parse_main_page_data(response.text, location)
            else:
                print(f"❌ Failed to load main page: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching from main page: {e}")
            return []

    async def _parse_main_page_data(self, html_content: str, location: str = None) -> List[MandiPriceRow]:
        """Parse market data from the main page HTML - contains state-level crop prices"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            price_rows = []
            
            print("🔍 Parsing main page for state-level crop prices...")
            
            # Look for table data on the main page
            tables = soup.find_all('table')
            print(f"📊 Found {len(tables)} tables on main page")
            
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"  Table {i+1}: {len(rows)} rows")
                
                current_category = ""
                current_product = ""
                
                # Skip header rows, look for data rows
                for row in rows[1:]:  # Skip first row (header)
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) == 3:  # 3 columns: Product/Variety, Min, Max
                        try:
                            # Extract data from cells based on actual structure
                            cell_texts = [cell.get_text(strip=True) for cell in cells]
                            
                            # Check if this is a category header (no prices, just text)
                            if not any(text.isdigit() for text in cell_texts[1:]):
                                if cell_texts[0] and not cell_texts[1] and not cell_texts[2]:
                                    # This is a category header like "Cereals"
                                    if not any(crop in cell_texts[0].lower() for crop in ['wheat', 'rice', 'jowar', 'bajra', 'onion', 'potato']):
                                        current_category = cell_texts[0]
                                        print(f"    📂 Category: {current_category}")
                                        current_product = ""  # Reset product when new category
                                    else:
                                        # This is actually a product name like "Wheat / ಗೋಧಿ"
                                        current_product = cell_texts[0]
                                        print(f"      🌾 Product: {current_product}")
                                continue
                            
                            # Check if this row has price data
                            has_price = any(text.isdigit() for text in cell_texts[1:])
                            has_variety = cell_texts[0] and not cell_texts[0].startswith('ಉತ್ಪನ್ನ')  # Not header text
                            
                            if has_price and has_variety and current_product:
                                # Extract structured data
                                market_data = self._extract_state_level_data_3col(cell_texts, current_product, current_category)
                                if market_data:
                                    price_rows.append(market_data)
                                    print(f"        ✅ Added: {market_data.commodity} - {market_data.variety} - ₹{market_data.modal}/quintal")
                                    
                        except Exception as e:
                            print(f"        ⚠️ Error parsing row: {e}")
                            continue
            
            print(f"📈 Successfully parsed {len(price_rows)} state-level price records")
            return price_rows
            
        except Exception as e:
            print(f"❌ Error parsing main page data: {e}")
            return []

    def _extract_market_data_from_cells(self, cell_texts: List[str]) -> Optional[MandiPriceRow]:
        """Extract structured market data from cell texts"""
        try:
            if len(cell_texts) < 5:
                return None
            
            # Try to identify which columns contain what data
            commodity = ""
            variety = ""
            market = ""
            modal_price = 0.0
            min_price = None
            max_price = None
            arrivals = None
            unit = "Quintal"
            
            # Look for commodity in first few columns
            for i, text in enumerate(cell_texts[:3]):
                if any(crop in text.lower() for crop in ['bajra', 'jowar', 'rice', 'wheat', 'maize', 'pulses']):
                    commodity = text
                    break
            
            # Look for market names
            for i, text in enumerate(cell_texts):
                if any(market_name in text.lower() for market_name in ['bangalore', 'bengaluru', 'mysore', 'mandi', 'apmc']):
                    market = text
                    break
            
            # Look for prices (numbers with ₹ or Rs)
            for text in cell_texts:
                if '₹' in text or 'Rs' in text:
                    price_text = text.replace('₹', '').replace('Rs', '').replace('.', '').strip()
                    try:
                        price = float(price_text)
                        if modal_price == 0.0:
                            modal_price = price
                        elif min_price is None:
                            min_price = price
                        else:
                            max_price = price
                    except ValueError:
                        pass
            
            # Look for arrival quantities
            for text in cell_texts:
                if text.isdigit() and len(text) < 5:  # Reasonable quantity
                    try:
                        arrivals = int(text)
                        break
                    except ValueError:
                        pass
            
            # Only return if we have essential data
            if commodity and market and modal_price > 0:
                return MandiPriceRow(
                    market=market,
                    state="Karnataka",
                    district=self._extract_district(market),
                    commodity=commodity,
                    variety=variety,
                    unit=unit,
                    modal=modal_price,
                    min_price=min_price,
                    max_price=max_price,
                    arrivals=arrivals,
                    date=date.today()
                )
            
            return None
            
        except Exception as e:
            print(f"    ⚠️ Error extracting market data: {e}")
            return None

    def _extract_state_level_data(self, cell_texts: List[str]) -> Optional[MandiPriceRow]:
        """Extract structured state-level crop price data from cell texts"""
        try:
            if len(cell_texts) < 4:
                return None
            
            # Extract Product, Variety, Min, Max
            product = cell_texts[0].strip()
            variety = cell_texts[1].strip()
            min_price_text = cell_texts[2].replace('₹', '').replace('Rs', '').replace('.', '').strip()
            max_price_text = cell_texts[3].replace('₹', '').replace('Rs', '').replace('.', '').strip()
            
            # Convert prices to float
            try:
                min_price = float(min_price_text)
                max_price = float(max_price_text)
            except ValueError:
                min_price = 0.0
                max_price = 0.0
            
            # Create MandiPriceRow
            return MandiPriceRow(
                market="State Level",
                state="Karnataka",
                district="State",
                commodity=product,
                variety=variety,
                unit="Quintal",
                modal=max_price, # Assuming modal is max price for state-level
                min_price=min_price,
                max_price=max_price,
                arrivals=None, # No arrival quantity for state-level
                date=date.today()
            )
        except Exception as e:
            print(f"    ⚠️ Error extracting state-level data: {e}")
            return None

    def _extract_state_level_data_3col(self, cell_texts: List[str], product: str, category: str) -> Optional[MandiPriceRow]:
        """Extract structured state-level crop price data from 3-column table row"""
        try:
            if len(cell_texts) < 3:
                return None
            
            # Extract Product, Variety, Min, Max
            variety = cell_texts[0].strip()
            min_price_text = cell_texts[1].replace('₹', '').replace('Rs', '').replace('.', '').strip()
            max_price_text = cell_texts[2].replace('₹', '').replace('Rs', '').replace('.', '').strip()
            
            # Convert prices to float
            try:
                min_price = float(min_price_text)
                max_price = float(max_price_text)
            except ValueError:
                min_price = 0.0
                max_price = 0.0
            
            # Create MandiPriceRow
            return MandiPriceRow(
                market="State Level",
                state="Karnataka",
                district="State",
                commodity=product,
                variety=variety,
                unit="Quintal",
                modal=max_price, # Assuming modal is max price for state-level
                min_price=min_price,
                max_price=max_price,
                arrivals=None, # No arrival quantity for state-level
                date=date.today()
            )
        except Exception as e:
            print(f"    ⚠️ Error extracting state-level data (3col): {e}")
            return None


async def fetch_karnataka_prices(
    location: str = None,
    commodity: str = None,
    report_date: Optional[date] = None,
    report_type: str = "M"
) -> List[MandiPriceRow]:
    """
    Fetch market prices from Karnataka government website
    
    Args:
        location: District or market name (optional)
        commodity: Commodity name (optional)
        report_date: Date for the report (defaults to today)
        report_type: Type of report (M=MarketWise, C=Commoditywise, L=Latest)
        
    Returns:
        List of price records
    """
    try:
        async with KarnatakaClient() as client:
            # Use the main page approach since the reports system is broken
            print("🏠 Using main page data source (reports system is currently down)")
            
            if commodity:
                # For commodity-specific data, still use main page but filter by commodity
                prices = await client.get_market_prices_from_main_page()
                if location:
                    # Filter by both commodity and location
                    return [p for p in prices if commodity.lower() in p.commodity.lower() and location.lower() in p.market.lower()]
                else:
                    # Filter by commodity only
                    return [p for p in prices if commodity.lower() in p.commodity.lower()]
            elif location:
                # For location-specific data, use main page
                return await client.get_market_prices_from_main_page(location)
            else:
                # Default to all data from main page
                return await client.get_market_prices_from_main_page()
                
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 500:
            print(f"⚠️  Karnataka website server error (500): {e}")
            print("   This is an external issue with the government website")
        else:
            print(f"❌ HTTP error in fetch_karnataka_prices: {e}")
        return []
    except httpx.ConnectError as e:
        print(f"⚠️  Connection error to Karnataka website: {e}")
        print("   Check if the website is accessible")
        return []
    except Exception as e:
        print(f"❌ Unexpected error in fetch_karnataka_prices: {e}")
        return []
