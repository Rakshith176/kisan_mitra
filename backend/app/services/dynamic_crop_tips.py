from __future__ import annotations

import json
import logging
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional

from llama_index.core import PromptTemplate
from llama_index.llms.gemini import Gemini

from ..config import settings
from ..schemas import LocalizedText
from .open_meteo import OpenMeteoClient


class DynamicCropTipsService:
    """Service for generating dynamic, context-aware crop tips using Gemini LLM"""
    
    def __init__(self):
        self.llm = Gemini(api_key=settings.google_api_key or "", model=settings.gemini_model)
        self.weather_client = OpenMeteoClient()
        self.logger = logging.getLogger(__name__)
    
    async def generate_crop_tips(
        self,
        crop_name: str,
        crop_name_localized: Dict[str, str],
        lat: float,
        lon: float,
        language: str,
        farm_size: Optional[float] = None,
        experience_years: Optional[int] = None,
        irrigation_type: Optional[str] = None,
        soil_type: Optional[str] = None,
    ) -> Tuple[str, List[str]]:
        """
        Generate dynamic crop tips based on current context
        
        Args:
            crop_name: English crop name
            crop_name_localized: Localized crop names (en, hi, kn)
            lat: Latitude
            lon: Longitude
            language: User's preferred language
            farm_size: Farm size in acres
            experience_years: Years of farming experience
            irrigation_type: Type of irrigation
            soil_type: Soil type
            
        Returns:
            Tuple of (title, list of tips)
        """
        try:
            # Get current weather context
            current_weather = await self.weather_client.get_current_weather(lat, lon)
            
            # Get seasonal context
            season = self._get_current_season()
            
            # Get crop stage context
            crop_stage = self._estimate_crop_stage(crop_name, season)
            
            # Prepare context for LLM
            context = {
                "crop": crop_name,
                "crop_localized": crop_name_localized,
                "weather": current_weather,
                "season": season,
                "crop_stage": crop_stage,
                "location": {"lat": lat, "lon": lon},
                "farm_profile": {
                    "size_acres": farm_size,
                    "experience_years": experience_years,
                    "irrigation_type": irrigation_type,
                    "soil_type": soil_type
                }
            }
            
            # Generate tips using LLM
            tips = await self._generate_tips_with_llm(context, language)
            
            return tips
            
        except Exception as e:
            self.logger.error(f"Failed to generate dynamic tips for {crop_name}: {e}")
            # Fallback to static tips
            return self._get_fallback_tips(crop_name, language)
    
    async def _generate_tips_with_llm(self, context: Dict, language: str) -> Tuple[str, List[str]]:
        """Generate tips using Gemini LLM"""
        
        # Create language-specific prompt
        if language == "hi":
            system_prompt = "आप एक अनुभवी कृषि सलाहकार हैं। किसानों को उनकी फसल के लिए व्यावहारिक सुझाव दें।"
            instruction = "दिए गए संदर्भ के आधार पर 3-4 व्यावहारिक कृषि सुझाव बनाएं।"
        elif language == "kn":
            system_prompt = "ನೀವು ಅನುಭವಿ ಕೃಷಿ ಸಲಹೆಗಾರರಾಗಿದ್ದೀರಿ. ರೈತರಿಗೆ ಅವರ ಬೆಳೆಗಳಿಗಾಗಿ ಪ್ರಾಯೋಗಿಕ ಸಲಹೆಗಳನ್ನು ನೀಡಿ."
            instruction = "ನೀಡಲಾದ ಸನ್ನಿವೇಶದ ಆಧಾರದಲ್ಲಿ 3-4 ಪ್ರಾಯೋಗಿಕ ಕೃಷಿ ಸಲಹೆಗಳನ್ನು ರಚಿಸಿ."
        else:
            system_prompt = "You are an experienced agricultural advisor. Provide practical suggestions to farmers for their crops."
            instruction = "Based on the given context, create 3-4 practical farming suggestions."
        
        prompt = PromptTemplate(
            f"{system_prompt}\n\n{instruction}\n\n"
            "Context: {context_json}\n\n"
            "Return JSON with keys: title, tips (array of strings).\n"
            "Keep tips actionable, specific, and relevant to current conditions.\n"
            "Focus on immediate actions farmers can take."
        )
        
        try:
            # Format context for LLM
            context_json = json.dumps(context, ensure_ascii=False, indent=2)
            
            # Generate response
            response = await self.llm.acomplete(
                prompt.format(context_json=context_json)
            )
            
            if response.text:
                # Parse JSON response
                try:
                    data = json.loads(response.text)
                    title = data.get("title", f"Tips for {context['crop']}")
                    tips = data.get("tips", [])
                    
                    # Ensure we have valid tips
                    if tips and isinstance(tips, list):
                        return title, tips[:4]  # Limit to 4 tips
                    
                except json.JSONDecodeError:
                    self.logger.warning("Failed to parse LLM response as JSON")
            
            # Fallback if LLM fails
            return self._get_fallback_tips(context["crop"], language)
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return self._get_fallback_tips(context["crop"], language)
    
    def _get_current_season(self) -> str:
        """Determine current agricultural season"""
        month = datetime.now().month
        
        if month in [6, 7, 8, 9]:
            return "monsoon"
        elif month in [10, 11]:
            return "post_monsoon"
        elif month in [12, 1, 2]:
            return "winter"
        else:
            return "summer"
    
    def _estimate_crop_stage(self, crop_name: str, season: str) -> str:
        """Estimate current crop stage based on season and crop type"""
        crop_lower = crop_name.lower()
        
        # Rice
        if "rice" in crop_lower:
            if season == "monsoon":
                return "vegetative_growth"
            elif season == "post_monsoon":
                return "flowering_heading"
            else:
                return "planning_season"
        
        # Wheat
        elif "wheat" in crop_lower:
            if season == "winter":
                return "vegetative_growth"
            elif season == "summer":
                return "harvest_ready"
            else:
                return "planning_season"
        
        # Sugarcane
        elif "sugarcane" in crop_lower:
            if season == "monsoon":
                return "active_growth"
            elif season == "winter":
                return "maturity"
            else:
                return "maintenance"
        
        # Cotton
        elif "cotton" in crop_lower:
            if season == "monsoon":
                return "flowering"
            elif season == "post_monsoon":
                return "boll_development"
            else:
                return "planning_season"
        
        # Pulses
        elif any(pulse in crop_lower for pulse in ["dal", "pulse", "lentil", "chickpea"]):
            if season == "monsoon":
                return "vegetative_growth"
            elif season == "post_monsoon":
                return "pod_development"
            else:
                return "planning_season"
        
        # Vegetables
        elif any(veg in crop_lower for veg in ["tomato", "onion", "potato", "vegetable"]):
            if season == "winter":
                return "vegetative_growth"
            elif season == "summer":
                return "harvest_ready"
            else:
                return "maintenance"
        
        # Default fallback
        return "general_maintenance"
    
    def _get_fallback_tips(self, crop_name: str, language: str) -> Tuple[str, List[str]]:
        """Provide fallback tips when LLM generation fails"""
        
        if language == "hi":
            title = f"{crop_name} के लिए सुझाव"
            tips = [
                "नियमित रूप से पौधों की जांच करें और कीटों को नियंत्रित करें",
                "मिट्टी की नमी बनाए रखें और उचित सिंचाई करें",
                "खरपतवार को समय पर हटाएं और मिट्टी को ढीला रखें"
            ]
        elif language == "kn":
            title = f"{crop_name} ಗಾಗಿ ಸಲಹೆಗಳು"
            tips = [
                "ಸಸ್ಯಗಳನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಕೀಟಗಳನ್ನು ನಿಯಂತ್ರಿಸಿ",
                "ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಕಾಯ್ದುಕೊಳ್ಳಿ ಮತ್ತು ಸರಿಯಾದ ನೀರಾವರಿ ಮಾಡಿ",
                "ಕಳೆಗಳನ್ನು ಸಮಯಕ್ಕೆ ತಕ್ಕಂತೆ ತೆಗೆದುಹಾಕಿ ಮತ್ತು ಮಣ್ಣನ್ನು ಸಡಿಲವಾಗಿ ಇರಿಸಿ"
            ]
        else:
            title = f"Tips for {crop_name}"
            tips = [
                "Regularly inspect plants and control pests",
                "Maintain soil moisture and provide proper irrigation",
                "Remove weeds timely and keep soil loose"
            ]
        
        return title, tips


# Global instance
dynamic_crop_tips_service = DynamicCropTipsService()
