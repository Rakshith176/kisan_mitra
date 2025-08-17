# Agricultural Data Fetcher Script

This script fetches comprehensive agricultural data from various government sources and stores it in JSON format for use in the Crop Cycle Planner (Phase 4).

## 🎯 **What This Script Does**

The script collects agricultural knowledge from multiple authoritative sources:

- **ICAR** - Indian Council of Agricultural Research (crop calendars, varieties, best practices)
- **data.gov.in** - Government APIs (Agmarknet market prices, agricultural census, soil health)
- **State Agricultural Universities** - Regional crop recommendations and research
- **KVKs** - Krishi Vigyan Kendras (location-specific agricultural advice)
- **Ministry of Agriculture** - Government schemes and advisories

## 🚀 **Quick Start**

### 1. Install Dependencies

```bash
cd backend/scripts
pip install -r requirements.txt
```

### 2. Basic Usage

```bash
# Fetch all agricultural data
python fetch_agricultural_data.py

# Fetch data for specific crop
python fetch_agricultural_data.py --crop rice

# Fetch data for specific state
python fetch_agricultural_data.py --state punjab

# Generate detailed report
python fetch_agricultural_data.py --generate-report

# Verbose logging
python fetch_agricultural_data.py --verbose

# Handle SSL issues with government sites
python fetch_agricultural_data.py --skip-ssl-verify

# Test connectivity and skip problematic sources
python fetch_agricultural_data.py --test-connectivity --skip-problematic
```

### 3. Advanced Usage

```bash
# Custom output directory
python fetch_agricultural_data.py --output-dir ./custom_data

# Filter by both crop and state
python fetch_agricultural_data.py --crop wheat --state haryana

# Generate report with custom output
python fetch_agricultural_data.py --generate-report --output-dir ./reports
```

## 📊 **Data Sources & Endpoints**

### **ICAR (Indian Council of Agricultural Research)**
- **Base URL**: https://icar.gov.in
- **Endpoints**:
  - `/crop-calendar` - Official crop calendar with planting/harvesting dates
  - `/crop-varieties` - Database of crop varieties with characteristics
  - `/best-practices` - Agricultural best practices and recommendations

### **data.gov.in APIs**
- **Base URL**: https://api.data.gov.in
- **API Key Required**: Yes (register at https://data.gov.in)
- **Endpoints**:
  - **Agmarknet Market Prices**: Resource ID `9ef84268-d588-465a-a308-a864a43d0070`
    - Real-time market prices from mandis across India
    - Parameters: `api-key`, `format=json`, `limit=1000`, `filters[state]`, `filters[commodity]`
  - **Agricultural Census**: Resource ID `6eece85f-0c1b-4f0c-9cd9-31cc872d0f31`
  - **Soil Health Card**: Resource ID `6eece85f-0c1b-4f0c-9cd9-31cc872d0f32`

### **State Agricultural Universities**
- **Punjab Agricultural University**: https://www.pau.edu
- **Tamil Nadu Agricultural University**: https://tnau.ac.in
- **University of Agricultural Sciences**: https://uasbangalore.edu.in

### **Krishi Vigyan Kendras (KVKs)**
- **Base URL**: https://kvk.icar.gov.in
- **Endpoints**:
  - `/directory` - Directory of all KVKs across India
  - `/recommendations` - Location-specific agricultural recommendations

### **Ministry of Agriculture**
- **Base URL**: https://agriculture.gov.in
- **Endpoints**:
  - `/schemes` - Government schemes for farmers
  - `/advisories` - Seasonal agricultural advisories
  - `/crop-calendar` - National crop calendar

## 🔧 **Configuration**

### Environment Variables

Create a `.env` file in the `backend/` directory:

## 🚨 **Troubleshooting SSL Issues**

Government websites often have SSL certificate issues. The script includes several solutions:

### **SSL Error Solutions**

1. **Use SSL bypass flags:**
   ```bash
   python fetch_agricultural_data.py --skip-ssl-verify
   ```

2. **Test connectivity first:**
   ```bash
   python fetch_agricultural_data.py --test-connectivity
   ```

3. **Skip problematic sources:**
   ```bash
   python fetch_agricultural_data.py --test-connectivity --skip-problematic
   ```

4. **Run SSL connectivity tests:**
   ```bash
   python test_ssl_fix.py
   ```

### **Common SSL Errors**

- **"nodename nor servname provided"**: DNS resolution issue
- **"SSL certificate verify failed"**: Self-signed or expired certificate
- **"Connection timeout"**: Firewall or network issue

### **Debugging Steps**

1. Check if the site is accessible in a browser
2. Test basic connectivity: `ping kvk.icar.gov.in`
3. Check SSL certificate: `openssl s_client -connect kvk.icar.gov.in:443`
4. Use the test script: `python test_ssl_fix.py`

```bash
# data.gov.in API key (required for Agmarknet data)
DATA_GOV_IN_API_KEY=your_api_key_here

# Optional: Custom settings
OUTPUT_DIRECTORY=./data/agricultural
LOG_LEVEL=INFO
```

### Configuration File

The script uses `data_sources_config.yaml` for endpoint configurations. You can modify this file to:

- Add new data sources
- Change API endpoints
- Adjust rate limiting settings
- Configure output formats

## 📁 **Output Structure**

The script generates the following files:

```
data/agricultural/
├── agricultural_data_20241201_143022.json    # Main data file
├── report_20241201_143022.txt                # Summary report (if --generate-report)
└── backup/                                   # Previous data backups
    └── agricultural_data_20241201_120000.json
```

### JSON Output Structure

```json
{
  "metadata": {
    "collection_timestamp": "2024-12-01T14:30:22.123456",
    "script_version": "1.0.0",
    "data_sources": ["icar", "data_gov_in", "state_universities", "kvk", "ministry"],
    "total_sources": 5,
    "success_rate": "4/5"
  },
  "icar": {
    "crop_calendar": {...},
    "crop_varieties": {...},
    "best_practices": {...}
  },
  "data_gov_in": {
    "agmarknet": {...},
    "agricultural_census": {...}
  },
  "state_universities": {
    "punjab": {...},
    "tamil_nadu": {...},
    "karnataka": {...}
  },
  "kvk": {
    "kvk_directory": {...},
    "recommendations": {...}
  },
  "ministry": {
    "schemes": {...},
    "advisories": {...}
  }
}
```

## 🛠️ **Customization**

### Adding New Data Sources

1. **Update `data_sources_config.yaml`**:
```yaml
new_source:
  name: "New Agricultural Source"
  base_url: "https://newsource.gov.in"
  endpoints:
    - name: "Crop Data"
      url: "https://newsource.gov.in/crop-data"
      type: "api"
      description: "New crop information"
```

2. **Add fetch method in `AgriculturalDataCollector`**:
```python
async def fetch_new_source_data(self) -> Dict[str, Any]:
    """Fetch data from new source"""
    # Implementation here
    pass
```

3. **Update `fetch_all_data()` method**:
```python
tasks = [
    self.fetch_icar_data(),
    self.fetch_data_gov_in_data(),
    self.fetch_new_source_data(),  # Add this line
    # ... other sources
]
```

### Data Processing

The script includes data models for structured agricultural information:

- **`CropVariety`** - Crop variety details (DTM, seasons, yield)
- **`GrowthStage`** - Growth stage information (duration, care requirements)
- **`RegionalPractice`** - Location-specific agricultural practices
- **`CropKnowledge`** - Complete crop knowledge base

## 📈 **Performance & Reliability**

### Rate Limiting
- **Default**: 2 requests per second
- **Configurable**: Modify `data_sources_config.yaml`

### Retry Logic
- **Max Retries**: 3 attempts
- **Exponential Backoff**: Yes
- **Initial Delay**: 1 second

### Error Handling
- **Graceful Degradation**: Continues if some sources fail
- **Detailed Logging**: All errors are logged with context
- **Success Rate Tracking**: Reports success/failure for each source

## 🔍 **Troubleshooting**

### Common Issues

1. **API Key Errors**:
   ```bash
   # Check if API key is set
   echo $DATA_GOV_IN_API_KEY
   
   # Or check .env file
   cat .env | grep DATA_GOV_IN_API_KEY
   ```

2. **Rate Limiting**:
   ```bash
   # Use verbose mode to see detailed logs
   python fetch_agricultural_data.py --verbose
   
   # Check rate limiting settings in config
   cat data_sources_config.yaml | grep -A 5 "rate_limiting"
   ```

3. **Network Issues**:
   ```bash
   # Test connectivity to sources
   curl -I https://icar.gov.in
   curl -I https://api.data.gov.in
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python fetch_agricultural_data.py --verbose

# Or set in .env file
LOG_LEVEL=DEBUG
```

## 📚 **Integration with Phase 4**

This script is designed to feed data into the **Crop Cycle Planner** (Phase 4):

1. **Run the script** to collect agricultural data
2. **Process the JSON output** to extract crop knowledge
3. **Store in vector database** for semantic search
4. **Use in AI-powered recommendations** for farmers

### Example Integration

```python
from scripts.fetch_agricultural_data import AgriculturalDataCollector

async def collect_and_process_data():
    async with AgriculturalDataCollector() as collector:
        # Fetch data
        data = await collector.fetch_all_data()
        
        # Process for vector DB
        crop_knowledge = extract_crop_knowledge(data)
        
        # Store in vector database
        store_in_vector_db(crop_knowledge)
        
        return crop_knowledge
```

## 🤝 **Contributing**

To improve the script:

1. **Test with new data sources**
2. **Add better error handling**
3. **Improve data parsing**
4. **Add data validation**
5. **Enhance reporting**

## 📄 **License**

This script is part of the Capital One Farmer App project and follows the same licensing terms.

## 🔗 **Useful Links**

- **data.gov.in API Registration**: https://data.gov.in/user/register
- **ICAR Official Website**: https://icar.gov.in
- **Ministry of Agriculture**: https://agriculture.gov.in
- **KVK Network**: https://kvk.icar.gov.in

---

**Note**: Some endpoints may require authentication or may not be publicly accessible. The script handles these gracefully and continues with available sources.
