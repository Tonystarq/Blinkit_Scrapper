# Blinkit Scraper Documentation

## Project Overview
This project implements a robust web scraper for Blinkit's e-commerce platform. The scraper systematically collects product data across different categories and locations by making API requests and processing the responses. The implementation uses Selenium WebDriver for browser automation and JavaScript execution, ensuring reliable data extraction even with dynamic content loading.

## Core Objectives
1. Collect comprehensive product data from Blinkit's platform
2. Support multiple categories and locations
3. Handle dynamic content loading and JavaScript execution
4. Implement rate limiting and error handling
5. Generate structured output in CSV format
6. Provide detailed error logging and debugging capabilities

## Technical Stack
### Dependencies
- Python 3.x (Recommended: 3.8+)
- Selenium 4.x
- tqdm (for progress tracking)
- Chrome WebDriver (matching your Chrome browser version)
- pandas (for data handling)
- requests (for API calls)

### System Requirements
- Chrome browser installed
- Chrome WebDriver in system PATH
- Minimum 4GB RAM
- Stable internet connection
- Sufficient disk space for output files

## Project Structure
```
BlinkitScrapper/
├── blinkit.py                 # Main script file
├── blinkit_categories.csv     # Category hierarchy data
├── blinkit_locations.csv      # Location coordinates
├── output/                    # Output directory
│   ├── blinkit_products_*.csv # Product data files
│   └── exception_*.json       # Error log files
└── Readme.md                  # This documentation
```

## Data Files Specification

### Categories CSV (blinkit_categories.csv)
Detailed format and requirements:
```
l1_category,l1_category_id,l2_category,l2_category_id
Munchies,1237,Bhujia & Mixtures,1178
...
```
- l1_category: Top-level category name
- l1_category_id: Unique identifier for top-level category
- l2_category: Sub-category name
- l2_category_id: Unique identifier for sub-category
- All fields are required
- No duplicate category IDs allowed
- UTF-8 encoding required

### Locations CSV (blinkit_locations.csv)
Detailed format and requirements:
```
latitude,longitude
28.678051,77.314262
...
```
- latitude: Decimal degrees (WGS84)
- longitude: Decimal degrees (WGS84)
- Both fields are required
- Valid coordinate ranges:
  - Latitude: -90 to 90
  - Longitude: -180 to 180
- UTF-8 encoding required

## Implementation Details

### 1. Core Components

#### Browser Automation (Selenium Setup)
- Headless Chrome configuration
- Custom window size (1920x1080)
- User agent spoofing
- Disabled GPU acceleration
- No-sandbox mode for container compatibility
- Custom timeout settings
- JavaScript execution capabilities

#### API Request Handling
- Dynamic URL construction based on:
  - Category IDs
  - Location coordinates
  - Current timestamp
- Rate limiting implementation (2-second delay)
- Request headers management
- Response validation
- Error retry mechanism

#### Data Processing Pipeline
1. Raw API response parsing
2. JSON structure validation
3. Product data extraction
4. Data normalization
5. Metadata enrichment
6. Duplicate detection
7. Output formatting

### 2. Key Functions

#### print_nested_structure(data, indent=0, max_depth=3, current_depth=0)
- Purpose: Advanced debugging tool for complex data structures
- Features:
  - Recursive depth control
  - Customizable indentation
  - Type-aware formatting
  - Circular reference detection
  - Memory-efficient processing

#### extract_product_data(snippet)
- Purpose: Robust product information extraction
- Handles:
  - Nested JSON structures
  - Missing fields
  - Data type conversion
  - Price formatting
  - Image URL validation
  - Stock status interpretation

#### read_categories()
- Purpose: Category data management
- Features:
  - CSV validation
  - Data type conversion
  - Duplicate detection
  - Error reporting
  - Memory optimization

#### read_locations()
- Purpose: Location data management
- Features:
  - Coordinate validation
  - Range checking
  - Format standardization
  - Error handling
  - Data caching

### 3. Main Process Flow

1. Initialization Phase
   - Environment setup
   - Configuration loading
   - Browser initialization
   - Data file validation

2. Execution Phase
   - Category iteration
   - Location iteration
   - API request execution
   - Response processing
   - Data collection
   - Progress tracking

3. Output Phase
   - Data validation
   - CSV generation
   - Error logging
   - Resource cleanup

## Output Specifications

### Product Data CSV
Headers and descriptions:
- date: Timestamp of data collection
- l1_category: Top-level category name
- l1_category_id: Top-level category identifier
- l2_category: Sub-category name
- l2_category_id: Sub-category identifier
- store_id: Unique store identifier
- variant_id: Product variant identifier
- variant_name: Product variant name
- group_id: Product group identifier
- selling_price: Current selling price
- mrp: Maximum retail price
- in_stock: Stock availability status
- inventory: Available quantity
- is_sponsored: Advertisement status
- image_url: Product image URL
- brand_id: Brand identifier
- brand: Brand name
- latitude: Store location latitude
- longitude: Store location longitude

### Error Log JSON
Structure:
```json
{
    "timestamp": "YYYY-MM-DD HH:MM:SS",
    "error_type": "Error class name",
    "error_message": "Detailed error description",
    "api_url": "Failed request URL",
    "category": "Current category info",
    "location": "Current location info",
    "stack_trace": "Full error stack trace"
}
```

## Usage Guide

### Installation
1. Install Python dependencies:
```bash
pip install selenium tqdm pandas requests
```

2. Install Chrome WebDriver:
- Download matching version from ChromeDriver website
- Add to system PATH
- Verify installation:
```bash
chromedriver --version
```

### Configuration
1. Prepare input files:
   - Create blinkit_categories.csv
   - Create blinkit_locations.csv
   - Place in project root directory

2. Optional configuration:
   - Adjust rate limiting in code
   - Modify browser settings
   - Configure output directory

### Execution
```bash
python blinkit.py
```

### Monitoring
- Progress bar shows:
  - Current category and location
  - Overall progress percentage
  - Estimated time remaining
  - Success/failure count
  - Current processing speed

## Error Handling

### Common Scenarios
1. Network Issues
   - Connection timeout
   - DNS resolution failure
   - SSL certificate problems

2. API Issues
   - Rate limiting
   - Invalid responses
   - Format changes

3. Data Issues
   - Invalid coordinates
   - Missing categories
   - Malformed responses

### Recovery Mechanisms
1. Automatic retries
2. Skip and continue
3. Detailed error logging
4. Resource cleanup

## Performance Optimization

### Current Implementation
- Memory-efficient processing
- Batch processing
- Progress tracking
- Resource management

### Future Improvements
1. Parallel Processing
   - Multi-threading support
   - Distributed scraping
   - Load balancing

2. Caching
   - Response caching
   - Category caching
   - Location caching

3. Optimization
   - Memory usage reduction
   - Network efficiency
   - Processing speed

## Security Considerations

1. Rate Limiting
   - Request throttling
   - IP rotation
   - User agent rotation

2. Data Protection
   - Secure storage
   - Access control
   - Data encryption

3. Compliance
   - Terms of service
   - Data privacy
   - Legal requirements

## Maintenance

### Regular Tasks
1. Chrome WebDriver updates
2. Dependency updates
3. Input file validation
4. Output directory cleanup

### Monitoring
1. Error rate tracking
2. Performance metrics
3. Data quality checks
4. Resource usage

## Support and Troubleshooting

### Common Issues
1. Chrome WebDriver
   - Version mismatch
   - Installation problems
   - Configuration issues

2. Network
   - Connectivity problems
   - Proxy configuration
   - Firewall settings

3. Data
   - Invalid formats
   - Missing files
   - Permission issues

### Solutions
1. WebDriver Issues
   - Update Chrome and WebDriver
   - Verify PATH settings
   - Check permissions

2. Network Issues
   - Check connectivity
   - Verify proxy settings
   - Update firewall rules

3. Data Issues
   - Validate input files
   - Check file permissions
   - Verify formats

## Future Roadmap

### Planned Features
1. Enhanced Error Handling
   - Advanced retry mechanisms
   - Better error reporting
   - Recovery options

2. Performance Improvements
   - Parallel processing
   - Caching system
   - Optimization

3. Additional Capabilities
   - Proxy support
   - Database integration
   - API monitoring

### Long-term Goals
1. Scalability
   - Distributed processing
   - Cloud integration
   - Load balancing

2. Reliability
   - Fault tolerance
   - Data validation
   - Backup systems

3. Usability
   - Configuration interface
   - Monitoring dashboard
   - Reporting tools
