"""
Government Schemes Integration Service
Matches farmers to relevant government schemes and provides application guidance
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import aiohttp
from dataclasses import dataclass
from enum import Enum
from app.config import settings

logger = logging.getLogger(__name__)

class SchemeCategory(Enum):
    """Categories of government schemes"""
    FERTILIZER_SUBSIDY = "fertilizer_subsidy"
    SEED_SUBSIDY = "seed_subsidy"
    IRRIGATION_SUBSIDY = "irrigation_subsidy"
    CROP_INSURANCE = "crop_insurance"
    LOAN_SUBSIDY = "loan_subsidy"
    EQUIPMENT_SUBSIDY = "equipment_subsidy"
    TRAINING_SUBSIDY = "training_subsidy"
    MARKETING_SUPPORT = "marketing_support"

class SchemeStatus(Enum):
    """Status of government schemes"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SEASONAL = "seasonal"
    LIMITED_TIME = "limited_time"

@dataclass
class SchemeRequirement:
    """Requirements for scheme eligibility"""
    requirement_type: str  # "document", "criteria", "deadline"
    description: str
    is_mandatory: bool
    deadline: Optional[date] = None
    document_format: Optional[str] = None

@dataclass
class GovernmentScheme:
    """Government scheme information"""
    scheme_id: str
    scheme_name: str
    category: SchemeCategory
    status: SchemeStatus
    description: str
    eligibility_criteria: List[str]
    benefits: List[str]
    requirements: List[SchemeRequirement]
    applicable_crops: List[str]
    applicable_regions: List[str]
    source: str
    reliability_score: float
    last_updated: date
    scheme_name_hi: Optional[str] = None
    scheme_name_kn: Optional[str] = None
    description_hi: Optional[str] = None
    description_kn: Optional[str] = None
    application_deadline: Optional[date] = None
    application_start_date: Optional[date] = None
    subsidy_percentage: Optional[float] = None
    max_subsidy_amount: Optional[float] = None

@dataclass
class SchemeMatch:
    """Farmer's match with a government scheme"""
    scheme: GovernmentScheme
    match_score: float  # 0.0 to 1.0
    match_reasons: List[str]
    application_status: str  # "eligible", "not_eligible", "pending"
    next_steps: List[str]
    estimated_benefit: Optional[float] = None

class SchemeMatchingService:
    """Service for matching farmers to government schemes"""
    
    def __init__(self):
        self.pm_kisan_url = "https://pmkisan.gov.in"
        self.fert_subsidy_url = "https://www.fert.nic.in"
        self.crop_insurance_url = "https://pmfby.gov.in"
        self.karnataka_schemes_url = "https://raitamitra.karnataka.gov.in"
        self.cache_duration_hours = 24
        self.session = None
        
        # Pre-defined schemes for major programs (fallback data)
        self.fallback_schemes = self._initialize_fallback_schemes()
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _initialize_fallback_schemes(self) -> Dict[str, GovernmentScheme]:
        """Initialize fallback government schemes with reliable baseline data"""
        fallback_data = {}
        
        # PM-KISAN Scheme
        pm_kisan_requirements = [
            SchemeRequirement(
                requirement_type="document",
                description="Aadhaar Card",
                is_mandatory=True
            ),
            SchemeRequirement(
                requirement_type="document",
                description="Land Records",
                is_mandatory=True
            ),
            SchemeRequirement(
                requirement_type="criteria",
                description="Must be a farmer with cultivable land",
                is_mandatory=True
            )
        ]
        
        fallback_data["pm_kisan"] = GovernmentScheme(
            scheme_id="pm_kisan_2024",
            scheme_name="PM-KISAN",
            scheme_name_hi="पीएम-किसान",
            scheme_name_kn="ಪಿಎಂ-ಕಿಸಾನ್",
            category=SchemeCategory.LOAN_SUBSIDY,
            status=SchemeStatus.ACTIVE,
            description="Direct income support of ₹6,000 per year to eligible farmer families",
            description_hi="योग्य किसान परिवारों को प्रति वर्ष ₹6,000 की सीधी आय सहायता",
            description_kn="ಯೋಗ್ಯ ರೈತ ಕುಟುಂಬಗಳಿಗೆ ವರ್ಷಕ್ಕೆ ₹6,000 ನೇರ ಆದಾಯ ಬೆಂಬಲ",
            eligibility_criteria=[
                "Must be a farmer with cultivable land",
                "Family should not have members in government service",
                "Family should not have members with monthly income above ₹10,000"
            ],
            benefits=[
                "₹6,000 per year in three installments of ₹2,000 each",
                "Direct bank transfer",
                "No repayment required"
            ],
            requirements=pm_kisan_requirements,
            application_deadline=None,  # Ongoing scheme
            application_start_date=date(2019, 2, 1),
            subsidy_percentage=100.0,
            max_subsidy_amount=6000.0,
            applicable_crops=["all"],
            applicable_regions=["all_india"],
            source="PM-KISAN Portal",
            reliability_score=0.98,
            last_updated=date(2024, 1, 1)
        )
        
        # Fertilizer Subsidy Scheme
        fert_requirements = [
            SchemeRequirement(
                requirement_type="document",
                description="Aadhaar Card",
                is_mandatory=True
            ),
            SchemeRequirement(
                requirement_type="document",
                description="Land Records",
                is_mandatory=True
            ),
            SchemeRequirement(
                requirement_type="criteria",
                description="Must purchase from authorized dealers",
                is_mandatory=True
            )
        ]
        
        fallback_data["fertilizer_subsidy"] = GovernmentScheme(
            scheme_id="fert_subsidy_2024",
            scheme_name="Fertilizer Subsidy",
            scheme_name_hi="उर्वरक सब्सिडी",
            scheme_name_kn="ರಸಗೊಬ್ಬರ ಸಬ್ಸಿಡಿ",
            category=SchemeCategory.FERTILIZER_SUBSIDY,
            status=SchemeStatus.ACTIVE,
            description="Subsidized fertilizers for farmers through authorized dealers",
            description_hi="अधिकृत डीलरों के माध्यम से किसानों के लिए सब्सिडी वाले उर्वरक",
            description_kn="ಅಧಿಕೃತ ವ್ಯಾಪಾರಿಗಳ ಮೂಲಕ ರೈತರಿಗೆ ಸಬ್ಸಿಡಿ ರಸಗೊಬ್ಬರಗಳು",
            eligibility_criteria=[
                "Must be a farmer with cultivable land",
                "Must purchase from authorized dealers",
                "No income limit"
            ],
            benefits=[
                "Urea: ₹266 per bag (50kg)",
                "DAP: ₹1,350 per bag (50kg)",
                "NPK: ₹1,200 per bag (50kg)"
            ],
            requirements=fert_requirements,
            application_deadline=None,  # Ongoing scheme
            application_start_date=None,
            subsidy_percentage=60.0,
            max_subsidy_amount=None,
            applicable_crops=["all"],
            applicable_regions=["all_india"],
            source="Department of Fertilizers",
            reliability_score=0.95,
            last_updated=date(2024, 1, 1)
        )
        
        # Crop Insurance Scheme (PMFBY)
        insurance_requirements = [
            SchemeRequirement(
                requirement_type="document",
                description="Aadhaar Card",
                is_mandatory=True
            ),
            SchemeRequirement(
                requirement_type="document",
                description="Land Records",
                is_mandatory=True
            ),
            SchemeRequirement(
                requirement_type="deadline",
                description="Apply before crop sowing",
                is_mandatory=True
            )
        ]
        
        fallback_data["crop_insurance"] = GovernmentScheme(
            scheme_id="pmfby_2024",
            scheme_name="PM Fasal Bima Yojana",
            scheme_name_hi="पीएम फसल बीमा योजना",
            scheme_name_kn="ಪಿಎಂ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ",
            category=SchemeCategory.CROP_INSURANCE,
            status=SchemeStatus.ACTIVE,
            description="Comprehensive crop insurance for farmers against natural calamities",
            description_hi="प्राकृतिक आपदाओं के खिलाफ किसानों के लिए व्यापक फसल बीमा",
            description_kn="ನೈಸರ್ಗಿಕ ವಿಪತ್ತುಗಳ ವಿರುದ್ಧ ರೈತರಿಗೆ ಸಮಗ್ರ ಬೆಳೆ ವಿಮೆ",
            eligibility_criteria=[
                "Must be a farmer with cultivable land",
                "Must apply before crop sowing",
                "All food crops, oilseeds, and commercial crops eligible"
            ],
            benefits=[
                "Premium: 2% for Kharif, 1.5% for Rabi, 5% for commercial crops",
                "Coverage against natural calamities, pests, and diseases",
                "Quick claim settlement"
            ],
            requirements=insurance_requirements,
            application_deadline=None,  # Seasonal
            application_start_date=None,
            subsidy_percentage=90.0,  # Government pays 90% of premium
            max_subsidy_amount=None,
            applicable_crops=["rice", "wheat", "maize", "cotton", "sugarcane", "pulses", "oilseeds"],
            applicable_regions=["all_india"],
            source="PMFBY Portal",
            reliability_score=0.95,
            last_updated=date(2024, 1, 1)
        )
        
        return fallback_data
    
    async def find_eligible_schemes(
        self, 
        farmer_profile: Dict[str, Any], 
        crop_cycle: Optional[Dict[str, Any]] = None
    ) -> List[SchemeMatch]:
        """
        Find eligible government schemes for a farmer
        
        Args:
            farmer_profile: Farmer's profile information
            crop_cycle: Current crop cycle information (optional)
            
        Returns:
            List of SchemeMatch objects with eligibility and match scores
        """
        try:
            logger.info(f"Finding eligible schemes for farmer in {farmer_profile.get('state', 'Unknown')}")
            
            # Get all available schemes
            all_schemes = await self._get_all_schemes()
            
            # Match schemes with farmer profile
            scheme_matches = []
            for scheme in all_schemes:
                match = await self._evaluate_scheme_eligibility(scheme, farmer_profile, crop_cycle)
                if match and match.match_score > 0.3:  # Only include relevant matches
                    scheme_matches.append(match)
            
            # Sort by match score (highest first)
            scheme_matches.sort(key=lambda x: x.match_score, reverse=True)
            
            logger.info(f"Found {len(scheme_matches)} eligible schemes")
            return scheme_matches
            
        except Exception as e:
            logger.error(f"Error finding eligible schemes: {e}")
            return []
    
    async def _get_all_schemes(self) -> List[GovernmentScheme]:
        """Get all available government schemes"""
        try:
            schemes = []
            
            # Add fallback schemes
            schemes.extend(self.fallback_schemes.values())
            
            # Try to fetch additional schemes from online sources
            online_schemes = await self._fetch_online_schemes()
            schemes.extend(online_schemes)
            
            return schemes
            
        except Exception as e:
            logger.error(f"Error getting all schemes: {e}")
            return list(self.fallback_schemes.values())
    
    async def _fetch_online_schemes(self) -> List[GovernmentScheme]:
        """Fetch additional schemes from online sources"""
        try:
            schemes = []
            
            # Fetch from PM-KISAN portal
            pm_kisan_schemes = await self._fetch_pm_kisan_schemes()
            schemes.extend(pm_kisan_schemes)
            
            # Fetch from fertilizer subsidy portal
            fert_schemes = await self._fetch_fertilizer_schemes()
            schemes.extend(fert_schemes)
            
            # Fetch from crop insurance portal
            insurance_schemes = await self._fetch_crop_insurance_schemes()
            schemes.extend(insurance_schemes)
            
            # Fetch from state-specific portals
            state_schemes = await self._fetch_state_schemes()
            schemes.extend(state_schemes)
            
            return schemes
            
        except Exception as e:
            logger.error(f"Error fetching online schemes: {e}")
            return []
    
    async def _fetch_pm_kisan_schemes(self) -> List[GovernmentScheme]:
        """Fetch schemes from PM-KISAN portal"""
        try:
            # This would fetch from PM-KISAN portal
            # For now, return empty list as we have fallback data
            return []
            
        except Exception as e:
            logger.error(f"Error fetching PM-KISAN schemes: {e}")
            return []
    
    async def _fetch_fertilizer_schemes(self) -> List[GovernmentScheme]:
        """Fetch schemes from fertilizer subsidy portal"""
        try:
            # This would fetch from fertilizer portal
            # For now, return empty list as we have fallback data
            return []
            
        except Exception as e:
            logger.error(f"Error fetching fertilizer schemes: {e}")
            return []
    
    async def _fetch_crop_insurance_schemes(self) -> List[GovernmentScheme]:
        """Fetch schemes from crop insurance portal"""
        try:
            # This would fetch from crop insurance portal
            # For now, return empty list as we have fallback data
            return []
            
        except Exception as e:
            logger.error(f"Error fetching crop insurance schemes: {e}")
            return []
    
    async def _fetch_state_schemes(self) -> List[GovernmentScheme]:
        """Fetch schemes from state-specific portals"""
        try:
            # This would fetch from state agriculture portals
            # For now, return empty list as we have fallback data
            return []
            
        except Exception as e:
            logger.error(f"Error fetching state schemes: {e}")
            return []
    
    async def _evaluate_scheme_eligibility(
        self, 
        scheme: GovernmentScheme, 
        farmer_profile: Dict[str, Any], 
        crop_cycle: Optional[Dict[str, Any]] = None
    ) -> Optional[SchemeMatch]:
        """Evaluate if a farmer is eligible for a specific scheme"""
        try:
            match_score = 0.0
            match_reasons = []
            application_status = "not_eligible"
            next_steps = []
            estimated_benefit = None
            
            # Check basic eligibility
            if await self._check_basic_eligibility(scheme, farmer_profile):
                match_score += 0.3
                match_reasons.append("Meets basic eligibility criteria")
                
                # Check regional eligibility
                if await self._check_regional_eligibility(scheme, farmer_profile):
                    match_score += 0.2
                    match_reasons.append("Available in your region")
                    
                    # Check crop-specific eligibility
                    if crop_cycle and await self._check_crop_eligibility(scheme, crop_cycle):
                        match_score += 0.3
                        match_reasons.append("Applicable to your current crop")
                        
                        # Check timing eligibility
                        if await self._check_timing_eligibility(scheme):
                            match_score += 0.2
                            match_reasons.append("Currently accepting applications")
                            application_status = "eligible"
                        else:
                            match_reasons.append("Application period not currently open")
                            next_steps.append("Wait for application period to open")
                    else:
                        match_reasons.append("Not applicable to your current crop")
                        next_steps.append("Consider this scheme for future crop cycles")
                else:
                    match_reasons.append("Not available in your region")
                    next_steps.append("Check for similar schemes in your state")
            else:
                match_reasons.append("Does not meet basic eligibility criteria")
                next_steps.append("Review eligibility requirements")
            
            # Calculate estimated benefit
            if application_status == "eligible":
                estimated_benefit = await self._calculate_estimated_benefit(scheme, farmer_profile, crop_cycle)
            
            # Generate next steps
            if application_status == "eligible":
                next_steps.extend(await self._generate_application_steps(scheme))
            
            return SchemeMatch(
                scheme=scheme,
                match_score=match_score,
                match_reasons=match_reasons,
                application_status=application_status,
                next_steps=next_steps,
                estimated_benefit=estimated_benefit
            )
            
        except Exception as e:
            logger.error(f"Error evaluating scheme eligibility: {e}")
            return None
    
    async def _check_basic_eligibility(self, scheme: GovernmentScheme, farmer_profile: Dict[str, Any]) -> bool:
        """Check basic eligibility criteria"""
        try:
            # Check if farmer has cultivable land
            if "farm_size" in farmer_profile and farmer_profile["farm_size"] > 0:
                return True
            
            # Check other basic criteria based on scheme type
            if scheme.category == SchemeCategory.FERTILIZER_SUBSIDY:
                return True  # Most farmers are eligible for fertilizer subsidy
            
            if scheme.category == SchemeCategory.CROP_INSURANCE:
                return True  # Most farmers are eligible for crop insurance
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking basic eligibility: {e}")
            return False
    
    async def _check_regional_eligibility(self, scheme: GovernmentScheme, farmer_profile: Dict[str, Any]) -> bool:
        """Check regional eligibility"""
        try:
            farmer_state = farmer_profile.get("state", "").lower()
            farmer_district = farmer_profile.get("district", "").lower()
            
            # Check if scheme is available in farmer's region
            for region in scheme.applicable_regions:
                if region == "all_india":
                    return True
                elif region.lower() in farmer_state or region.lower() in farmer_district:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking regional eligibility: {e}")
            return False
    
    async def _check_crop_eligibility(self, scheme: GovernmentScheme, crop_cycle: Dict[str, Any]) -> bool:
        """Check crop-specific eligibility"""
        try:
            crop_name = crop_cycle.get("crop_name", "").lower()
            
            # Check if scheme applies to farmer's crop
            for applicable_crop in scheme.applicable_crops:
                if applicable_crop == "all":
                    return True
                elif applicable_crop.lower() in crop_name:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking crop eligibility: {e}")
            return False
    
    async def _check_timing_eligibility(self, scheme: GovernmentScheme) -> bool:
        """Check if scheme is currently accepting applications"""
        try:
            current_date = datetime.now().date()
            
            # Check if scheme is active
            if scheme.status != SchemeStatus.ACTIVE:
                return False
            
            # Check application deadlines
            if scheme.application_deadline and current_date > scheme.application_deadline:
                return False
            
            # Check application start dates
            if scheme.application_start_date and current_date < scheme.application_start_date:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking timing eligibility: {e}")
            return False
    
    async def _calculate_estimated_benefit(
        self, 
        scheme: GovernmentScheme, 
        farmer_profile: Dict[str, Any], 
        crop_cycle: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """Calculate estimated benefit from scheme"""
        try:
            if scheme.max_subsidy_amount:
                return scheme.max_subsidy_amount
            
            if scheme.subsidy_percentage and crop_cycle:
                # Calculate based on crop area and typical costs
                area_acres = crop_cycle.get("area_acres", 1.0)
                
                if scheme.category == SchemeCategory.FERTILIZER_SUBSIDY:
                    # Estimate fertilizer cost per acre
                    typical_cost_per_acre = 2000.0  # ₹2000 per acre
                    total_cost = area_acres * typical_cost_per_acre
                    subsidy_amount = total_cost * (scheme.subsidy_percentage / 100.0)
                    return subsidy_amount
                
                elif scheme.category == SchemeCategory.CROP_INSURANCE:
                    # Estimate insurance premium per acre
                    typical_premium_per_acre = 500.0  # ₹500 per acre
                    total_premium = area_acres * typical_premium_per_acre
                    subsidy_amount = total_premium * (scheme.subsidy_percentage / 100.0)
                    return subsidy_amount
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating estimated benefit: {e}")
            return None
    
    async def _generate_application_steps(self, scheme: GovernmentScheme) -> List[str]:
        """Generate step-by-step application guidance"""
        try:
            steps = []
            
            # Add general steps
            steps.append("Collect required documents")
            steps.append("Visit nearest agriculture office or apply online")
            steps.append("Submit application with supporting documents")
            steps.append("Wait for approval and verification")
            
            # Add scheme-specific steps
            if scheme.category == SchemeCategory.FERTILIZER_SUBSIDY:
                steps.append("Purchase fertilizers from authorized dealers")
                steps.append("Keep purchase receipts for verification")
            
            elif scheme.category == SchemeCategory.CROP_INSURANCE:
                steps.append("Apply before crop sowing begins")
                steps.append("Pay remaining premium after government subsidy")
            
            elif scheme.category == SchemeCategory.LOAN_SUBSIDY:
                steps.append("Apply through authorized banks")
                steps.append("Complete loan application process")
            
            return steps
            
        except Exception as e:
            logger.error(f"Error generating application steps: {e}")
            return ["Contact local agriculture office for guidance"]
    
    async def get_scheme_details(self, scheme_id: str) -> Optional[GovernmentScheme]:
        """Get detailed information about a specific scheme"""
        try:
            # Check fallback schemes first
            if scheme_id in self.fallback_schemes:
                return self.fallback_schemes[scheme_id]
            
            # Try to fetch from online sources
            # Implementation depends on available APIs
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting scheme details: {e}")
            return None
    
    async def get_application_timeline(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        """Get application timeline for a scheme"""
        try:
            scheme = await self.get_scheme_details(scheme_id)
            if not scheme:
                return None
            
            timeline = {
                "scheme_name": scheme.scheme_name,
                "application_start": scheme.application_start_date,
                "application_deadline": scheme.application_deadline,
                "status": scheme.status.value,
                "current_status": "open" if await self._check_timing_eligibility(scheme) else "closed"
            }
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error getting application timeline: {e}")
            return None
    
    def export_schemes_to_csv(self, schemes: List[GovernmentScheme], filename: str):
        """Export schemes data to CSV for analysis"""
        try:
            import pandas as pd
            
            # Convert schemes to DataFrame
            data_rows = []
            for scheme in schemes:
                data_rows.append({
                    'scheme_id': scheme.scheme_id,
                    'scheme_name': scheme.scheme_name,
                    'category': scheme.category.value,
                    'status': scheme.status.value,
                    'description': scheme.description,
                    'eligibility_criteria': '; '.join(scheme.eligibility_criteria),
                    'benefits': '; '.join(scheme.benefits),
                    'subsidy_percentage': scheme.subsidy_percentage,
                    'max_subsidy_amount': scheme.max_subsidy_amount,
                    'applicable_crops': '; '.join(scheme.applicable_crops),
                    'applicable_regions': '; '.join(scheme.applicable_regions),
                    'source': scheme.source,
                    'reliability_score': scheme.reliability_score,
                    'last_updated': scheme.last_updated
                })
            
            df = pd.DataFrame(data_rows)
            df.to_csv(filename, index=False)
            logger.info(f"Exported {len(schemes)} schemes to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting schemes to CSV: {e}")

# Example usage and testing
async def test_scheme_matching_service():
    """Test the scheme matching service"""
    async with SchemeMatchingService() as service:
        # Test farmer profile
        farmer_profile = {
            "state": "Karnataka",
            "district": "Bangalore Rural",
            "farm_size": 2.5,
            "experience_years": 5
        }
        
        # Test crop cycle
        crop_cycle = {
            "crop_name": "rice",
            "area_acres": 2.5,
            "season": "kharif"
        }
        
        # Find eligible schemes
        eligible_schemes = await service.find_eligible_schemes(farmer_profile, crop_cycle)
        
        print(f"Found {len(eligible_schemes)} eligible schemes:")
        for match in eligible_schemes:
            print(f"\n{match.scheme.scheme_name}")
            print(f"Match Score: {match.match_score:.2f}")
            print(f"Status: {match.application_status}")
            print(f"Estimated Benefit: ₹{match.estimated_benefit or 'N/A'}")
            print(f"Reasons: {', '.join(match.match_reasons)}")
            print(f"Next Steps: {', '.join(match.next_steps)}")
        
        # Export schemes to CSV
        if eligible_schemes:
            schemes = [match.scheme for match in eligible_schemes]
            service.export_schemes_to_csv(schemes, "eligible_schemes.csv")

if __name__ == "__main__":
    asyncio.run(test_scheme_matching_service())
