#!/usr/bin/env python3
"""
Test script for the Agricultural Data Fetcher

This script tests the basic functionality without making actual HTTP requests.
"""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from fetch_agricultural_data import AgriculturalDataCollector, CropVariety, GrowthStage, RegionalPractice, CropKnowledge

async def test_data_models():
    """Test the Pydantic data models"""
    print("🧪 Testing data models...")
    
    try:
        # Test CropVariety
        variety = CropVariety(
            name="Basmati Rice",
            dtm_min=120,
            dtm_max=150,
            season=["kharif", "rabi"],
            yield_per_hectare=4.5,
            water_requirement="high",
            soil_preferences=["clay loam", "silty loam"]
        )
        print("✅ CropVariety model works")
        
        # Test GrowthStage
        stage = GrowthStage(
            stage="vegetative",
            duration_days=45,
            description="Rapid growth phase",
            care_requirements={"irrigation": "daily", "fertilizer": "NPK"},
            critical_factors=["water", "temperature", "nutrients"]
        )
        print("✅ GrowthStage model works")
        
        # Test RegionalPractice
        practice = RegionalPractice(
            state="Punjab",
            district="Amritsar",
            crop="rice",
            variety="Basmati",
            planting_window=["June", "July"],
            irrigation_frequency="daily",
            common_pests=["rice stem borer", "leaf folder"],
            soil_preferences=["clay loam"],
            fertilizer_recommendations={"N": "120 kg/ha", "P": "60 kg/ha", "K": "40 kg/ha"}
        )
        print("✅ RegionalPractice model works")
        
        # Test CropKnowledge
        knowledge = CropKnowledge(
            crop_name="Rice",
            scientific_name="Oryza sativa",
            family="Poaceae",
            varieties=[variety],
            growth_stages=[stage],
            regional_practices=[practice],
            source="ICAR",
            last_updated="2024-12-01T10:00:00Z"
        )
        print("✅ CropKnowledge model works")
        
        # Test JSON serialization
        json_data = knowledge.model_dump_json()
        print("✅ JSON serialization works")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model test failed: {e}")
        return False

async def test_collector_initialization():
    """Test the AgriculturalDataCollector initialization"""
    print("\n🧪 Testing collector initialization...")
    
    try:
        collector = AgriculturalDataCollector("./test_output")
        
        # Check if output directory was created
        if collector.output_dir.exists():
            print("✅ Output directory created")
        else:
            print("❌ Output directory not created")
            return False
        
        # Check if endpoints are configured
        if collector.endpoints:
            print(f"✅ {len(collector.endpoints)} data sources configured")
        else:
            print("❌ No data sources configured")
            return False
        
        # Check if headers are set
        if collector.headers:
            print("✅ Headers configured")
        else:
            print("❌ Headers not configured")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Collector initialization test failed: {e}")
        return False

async def test_mock_data_collection():
    """Test data collection with mocked HTTP responses"""
    print("\n🧪 Testing mock data collection...")
    
    # Mock successful responses
    mock_responses = {
        "https://icar.gov.in/api/crop-calendar": {
            "status": 200,
            "json": {"data": "mock_crop_calendar"}
        },
        "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070": {
            "status": 200,
            "json": {"data": "mock_agmarknet"}
        }
    }
    
    try:
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Configure mock responses
            for url, response_data in mock_responses.items():
                mock_response = AsyncMock()
                mock_response.status = response_data["status"]
                mock_response.json = AsyncMock(return_value=response_data["json"])
                mock_response.headers = {"content-type": "application/json"}
                mock_get.return_value.__aenter__.return_value = mock_response
            
            async with AgriculturalDataCollector("./test_output") as collector:
                # Test ICAR data fetching
                icar_data = await collector.fetch_icar_data()
                if icar_data and "crop_calendar" in icar_data:
                    print("✅ Mock ICAR data collection works")
                else:
                    print("❌ Mock ICAR data collection failed")
                    return False
                
                # Test data.gov.in data fetching
                gov_data = await collector.fetch_data_gov_in_data()
                if gov_data:
                    print("✅ Mock data.gov.in data collection works")
                else:
                    print("❌ Mock data.gov.in data collection failed")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock data collection test failed: {e}")
        return False

async def test_data_saving():
    """Test data saving functionality"""
    print("\n🧪 Testing data saving...")
    
    try:
        test_data = {
            "metadata": {
                "collection_timestamp": "2024-12-01T10:00:00Z",
                "script_version": "1.0.0",
                "data_sources": ["test"],
                "total_sources": 1,
                "success_rate": "1/1"
            },
            "test_source": {
                "data": "test_value"
            }
        }
        
        async with AgriculturalDataCollector("./test_output") as collector:
            # Test data saving
            filepath = await collector.save_data(test_data, "test_data.json")
            
            if Path(filepath).exists():
                print("✅ Data saving works")
                
                # Test data loading
                with open(filepath, 'r') as f:
                    loaded_data = json.load(f)
                
                if loaded_data == test_data:
                    print("✅ Data loading works")
                else:
                    print("❌ Data loading failed - data mismatch")
                    return False
            else:
                print("❌ Data saving failed - file not created")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data saving test failed: {e}")
        return False

async def test_report_generation():
    """Test report generation functionality"""
    print("\n🧪 Testing report generation...")
    
    try:
        test_data = {
            "metadata": {
                "collection_timestamp": "2024-12-01T10:00:00Z",
                "script_version": "1.0.0",
                "data_sources": ["test1", "test2"],
                "total_sources": 2,
                "success_rate": "2/2"
            },
            "test1": {"data": "value1"},
            "test2": {"data": "value2"}
        }
        
        async with AgriculturalDataCollector("./test_output") as collector:
            # Test report generation
            report = await collector.generate_summary_report(test_data)
            
            if report and "AGRICULTURAL DATA COLLECTION SUMMARY REPORT" in report:
                print("✅ Report generation works")
                
                # Check if report contains expected content
                if "test1" in report and "test2" in report:
                    print("✅ Report contains expected data")
                else:
                    print("❌ Report missing expected data")
                    return False
            else:
                print("❌ Report generation failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return False

async def cleanup_test_files():
    """Clean up test files and directories"""
    print("\n🧹 Cleaning up test files...")
    
    try:
        test_dir = Path("./test_output")
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
            print("✅ Test files cleaned up")
        else:
            print("ℹ️  No test files to clean up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Agricultural Data Fetcher Tests\n")
    
    tests = [
        ("Data Models", test_data_models),
        ("Collector Initialization", test_collector_initialization),
        ("Mock Data Collection", test_mock_data_collection),
        ("Data Saving", test_data_saving),
        ("Report Generation", test_report_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print("-"*50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        
        # Clean up
        asyncio.run(cleanup_test_files())
        
        if success:
            print("\n✅ All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        asyncio.run(cleanup_test_files())
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        asyncio.run(cleanup_test_files())
        sys.exit(1)
