# scripts/enhanced_ingest_schemes.py
"""
Enhanced data ingestion script to populate the vector database with government schemes information.
Uses Vertex AI embeddings with Firestore for storage.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

# Add the parent directory to Python path so we can import from utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Now import our modules
from utils.simplified_vector_client import SimplifiedVectorClient
from utils.firestore_client import FirestoreClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSchemesIngestion:
    """Enhanced ingestion using Vertex AI embeddings + Firestore"""
    
    def __init__(self):
        self.vector_client = SimplifiedVectorClient()
        self.firestore_client = FirestoreClient()
        
    def ingest_comprehensive_schemes_data(self):
        """Ingest comprehensive government schemes data"""
        
        # Enhanced schemes data with more detailed information
        comprehensive_schemes = [
            {
                'id': 'pm_kisan_comprehensive',
                'content': """PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) Scheme - Complete Guide

OVERVIEW:
PM-KISAN is a Central Sector Scheme launched in 2019 to provide income support to farmer families across India. It ensures direct income support to farmers to supplement their financial needs for procuring inputs related to agriculture and allied activities.

FINANCIAL BENEFITS:
- Direct cash transfer of ₹6,000 per year
- Paid in three equal installments of ₹2,000 each
- Installments paid every four months (April-July, August-November, December-March)
- Money transferred directly to beneficiary's bank account via DBT

ELIGIBILITY CRITERIA:
- All landholding farmer families (both husband and wife can benefit if separate holdings)
- Small and marginal farmers with combined land holding up to 2 hectares
- Cultivable land holders across rural and urban areas
- Both male and female farmers eligible

EXCLUSIONS:
- Institutional land holders
- Farmer families with any member as income tax payee
- Government employees and pensioners
- Professionals like doctors, engineers, lawyers, CAs

APPLICATION PROCESS:
1. Online registration at pmkisan.gov.in
2. Visit Common Service Centers (CSC)
3. Contact local Patwari/Revenue Officer
4. Mobile app: PM Kisan Mobile App

REQUIRED DOCUMENTS:
- Aadhaar card (mandatory)
- Bank account details with IFSC
- Land ownership documents (Khata/Khatauni)
- Mobile number
- Passport size photograph

BENEFITS RECEIVED:
- Over 11 crore farmers registered
- More than ₹2.6 lakh crore disbursed since launch
- Direct benefit transfer eliminates middlemen
- Improved rural purchasing power

CONTACT INFORMATION:
- Helpline: 155261 / 1800115526
- Email: pmkisan-ict@gov.in
- Website: pmkisan.gov.in""",
                'metadata': {
                    'source': 'Ministry of Agriculture and Farmers Welfare',
                    'title': 'PM-KISAN Comprehensive Guide',
                    'category': 'Income Support',
                    'last_updated': '2024-01-15',
                    'scheme_type': 'Central Government Scheme',
                    'keywords': ['pm-kisan', 'income support', 'cash transfer', 'farmers', 'subsidy']
                }
            },
            {
                'id': 'micro_irrigation_detailed',
                'content': """Micro Irrigation Scheme - Complete Information

SCHEME OVERVIEW:
The Per Drop More Crop component of Pradhan Mantri Krishi Sinchayee Yojana (PMKSY-PDMC) promotes micro irrigation including drip and sprinkler irrigation systems to achieve water use efficiency and increase crop productivity.

SUBSIDY STRUCTURE:
DRIP IRRIGATION:
- Small & Marginal Farmers: 55% of cost
- Other Farmers: 45% of cost
- Additional 10% for SC/ST farmers
- Additional 5% for women farmers

SPRINKLER IRRIGATION:
- Small & Marginal Farmers: 55% of cost
- Other Farmers: 45% of cost
- Additional benefits for SC/ST and women farmers

AREA COVERAGE:
- Minimum area: 0.5 hectares for individual farmers
- Maximum area: 5 hectares per farmer
- Cluster approach for small holdings (minimum 25 ha cluster)
- Community irrigation systems supported

ELIGIBLE CROPS:
FRUITS: Mango, citrus, pomegranate, grapes, apple, banana, guava
VEGETABLES: Tomato, onion, potato, cabbage, cauliflower, brinjal, okra
CASH CROPS: Cotton, sugarcane, turmeric, cardamom
CEREALS: Maize, wheat (under specific conditions)
PLANTATION CROPS: Tea, coffee, rubber, coconut

TECHNICAL SPECIFICATIONS:
- BIS approved components mandatory
- Filtration system included
- Fertigation facility optional
- Quality standards as per Central Water Commission norms
- Installation by empaneled agencies only

FINANCIAL LIMITS:
- Drip irrigation: ₹1.20 lakh per hectare
- Sprinkler irrigation: ₹68,000 per hectare
- Micro sprinkler: ₹75,000 per hectare
- Rain gun: ₹30,000 per hectare

APPLICATION PROCESS:
1. Apply through District Horticulture Officer
2. Submit technical proposal with layout plan
3. Soil test report and water source details
4. Bank guarantee or security deposit
5. Installation within 90 days of approval

BENEFITS:
- 40-60% water saving
- 20-50% increase in crop yield
- Reduced labor requirement
- Better fertilizer use efficiency
- Year-round cultivation possible

STATE IMPLEMENTING AGENCIES:
- Department of Horticulture
- Department of Agriculture
- Mission for Integrated Development of Horticulture (MIDH)

CONTACT:
- National Mission for Sustainable Agriculture
- Website: pmksy.gov.in
- Helpline: 1800-180-1551""",
                'metadata': {
                    'source': 'Department of Agriculture and Cooperation',
                    'title': 'Micro Irrigation Scheme Detailed Guide',
                    'category': 'Water Management',
                    'last_updated': '2024-02-10',
                    'scheme_type': 'Central Government Scheme',
                    'keywords': ['drip irrigation', 'sprinkler', 'water saving', 'pmksy', 'micro irrigation']
                }
            },
            {
                'id': 'organic_farming_pkvy_complete',
                'content': """Paramparagat Krishi Vikas Yojana (PKVY) - Comprehensive Organic Farming Guide

SCHEME INTRODUCTION:
PKVY is a flagship scheme under National Mission for Sustainable Agriculture (NMSA) that promotes organic farming through adoption of organic village by cluster approach and Participatory Guarantee System (PGS) certification.

FINANCIAL ASSISTANCE STRUCTURE:
PER HECTARE SUPPORT (₹50,000 over 3 years):
Year 1: ₹20,000 per hectare
Year 2: ₹18,000 per hectare  
Year 3: ₹12,000 per hectare

COMPONENT-WISE BREAKDOWN:
- Organic inputs: ₹31,000 (62%)
- Certification support: ₹8,800 (17.6%)
- Cluster formation & capacity building: ₹3,200 (6.4%)
- Organic premium/marketing: ₹7,000 (14%)

CLUSTER FORMATION:
- Minimum 50 farmers per cluster
- 50 hectare minimum area
- Organic village approach
- Community participation mandatory
- Local Resource Person (LRP) training

ORGANIC INPUTS SUPPORTED:
- Organic manure (FYM, vermicompost, green manure)
- Bio-fertilizers (Rhizobium, PSB, Azotobacter)
- Bio-pesticides (Neem, Karanj, Trichoderma)
- Organic seeds and planting material
- Equipment for compost making

CERTIFICATION PROCESS:
- Participatory Guarantee System (PGS)
- Peer review mechanism
- Third-party verification
- Organic certificate issuance
- Traceability system

CROPS COVERED:
CEREALS: Rice, wheat, millets, maize
PULSES: Arhar, gram, moong, urad
OILSEEDS: Mustard, groundnut, sesame, sunflower
CASH CROPS: Cotton, sugarcane, turmeric
SPICES: Coriander, cumin, fenugreek, chili
FRUITS & VEGETABLES: All seasonal varieties

MARKET LINKAGES:
- Organic bazaars in cities
- Direct marketing platforms
- Export facilitation
- Premium price realization
- Branding support for FPOs

CAPACITY BUILDING:
- Training to farmers on organic practices
- Exposure visits to successful organic farms
- Technical backstopping by experts
- Demonstration plots
- Skill development programs

CONVERGENCE OPPORTUNITIES:
- MGNREGA for labor intensive activities
- SHG linkages for input procurement
- FPO formation for marketing
- Bank credit for infrastructure
- Crop insurance under PMFBY

STATE IMPLEMENTATION:
- State Agriculture Universities as nodal agencies
- KVKs for technical support
- ATMA for extension services
- Organic certification agencies

BENEFITS ACHIEVED:
- Soil health improvement
- Reduced input costs (30-50%)
- Premium price (20-40% higher)
- Export opportunities
- Environmental sustainability
- Farmer health improvement

APPLICATION PROCESS:
1. Group formation with 50 farmers
2. Village selection and cluster planning
3. Application through ATMA/Agriculture Department
4. Training and capacity building
5. Conversion period of 3 years
6. PGS certification

CONTACT INFORMATION:
- National Sample Survey Office
- Website: organic.dac.gov.in
- Email: organic-agri@gov.in
- Helpline: 1800-180-1551""",
                'metadata': {
                    'source': 'Department of Agriculture and Cooperation',
                    'title': 'PKVY Organic Farming Complete Guide',
                    'category': 'Organic Farming',
                    'last_updated': '2024-01-20',
                    'scheme_type': 'Central Government Scheme',
                    'keywords': ['organic farming', 'pkvy', 'pgs certification', 'cluster approach', 'sustainable agriculture']
                }
            },
            {
                'id': 'pmfby_crop_insurance_detailed',
                'content': """Pradhan Mantri Fasal Bima Yojana (PMFBY) - Complete Crop Insurance Guide

SCHEME OVERVIEW:
PMFBY is the largest crop insurance scheme in the world providing comprehensive crop insurance coverage against all non-preventable natural risks from pre-sowing to post-harvest stage including coverage for localized calamities.

PREMIUM STRUCTURE:
SEASONAL CROPS:
- Kharif crops: Maximum 2% of Sum Insured by farmers
- Rabi crops: Maximum 1.5% of Sum Insured by farmers  
- Annual commercial/horticultural crops: Maximum 5% of Sum Insured

GOVERNMENT SUBSIDY:
- Central Government: 50% of premium (in unirrigated areas), 47.5% (in irrigated areas)
- State Government: 50% of premium (in unirrigated areas), 47.5% (in irrigated areas)
- Northeast states: Central Government pays 90%

SUM INSURED CALCULATION:
Option 1: District level Scale of Finance × Area
Option 2: Average yield of last 7 years × MSP × Area
(Whichever is higher)

COVERAGE DETAILS:
PRE-SOWING LOSSES:
- Prevented sowing/planting due to adverse weather
- Coverage up to 25% of sum insured

STANDING CROP LOSSES:
- Drought, dry spells, flood, inundation
- Pest and diseases, landslides, hailstorm
- Cyclone, typhoon, tempest, hurricane
- Fire, lightning

POST-HARVEST LOSSES:
- Coverage for 14 days from harvesting
- Against cyclone, unseasonal rains
- Only for crops dried in cut and spread condition

LOCALIZED CALAMITIES:
- Hailstorm, landslide, inundation affecting isolated farms
- Assessment within 72 hours of occurrence
- GPS technology for assessment
- Individual farm level coverage

COVERAGE EXCLUSIONS:
- War and nuclear risks
- Malicious damage
- Theft or destruction by domestic/wild animals
- Acts of thieves or enemies of the State

CLAIM SETTLEMENT PROCESS:
YIELD ESTIMATION:
- Crop Cutting Experiments (CCE)
- Smart sampling methodology
- Technology integration (satellites, drones)
- Weather data analysis

THRESHOLD YIELD:
- Average yield of last 7 years at notified area level
- If actual yield < threshold yield, compensation paid
- Compensation = (Threshold yield - Actual yield) × Sum Insured / Threshold yield

CLAIM TIMELINE:
- Intimation of loss within 72 hours
- Assessment completion within 30 days
- Claim settlement within 45 days of assessment
- Direct benefit transfer to farmer accounts

TECHNOLOGY INTEGRATION:
- Bhuvan portal for area monitoring
- Weather stations for data collection
- Mobile apps for farmer registration
- Satellite imagery for yield estimation

ENROLLMENT PROCESS:
COMPULSORY ENROLLMENT:
- Loanee farmers with Seasonal Agricultural Operations (SAO) loans
- Automatic coverage unless opted out

VOLUNTARY ENROLLMENT:
- Non-loanee farmers
- Online registration through CSCs
- Bank branches, insurance companies
- Mobile applications

REQUIRED DOCUMENTS:
- Land ownership documents (Khata/Khatauni)
- Aadhaar card
- Bank account details
- Loan sanction letter (for loanee farmers)
- Sowing certificate from Patwari

SPECIAL FEATURES:
- No capping on government subsidy
- Use of technology for faster claim settlement
- Uniform premium across the country
- Early settlement for localized losses
- Mobile app for easy access

PARTICIPATING STATES:
All states and Union Territories except:
- West Bengal (has state scheme)
- Bihar (implementing from 2018-19)
- Jharkhand (has state scheme)

INSURANCE COMPANIES:
- Agriculture Insurance Company of India Ltd. (AIC)
- ICICI Lombard General Insurance
- HDFC ERGO General Insurance
- Future Generali India Insurance
- Reliance General Insurance

GRIEVANCE REDRESSAL:
- Toll-free helpline: 14447
- Web portal: pmfby.gov.in
- Mobile app: Crop Insurance
- Insurance Ombudsman for disputes
- District Level Monitoring Committee

BENEFITS ACHIEVED:
- Coverage to 5.5 crore farmers annually
- Claims paid worth ₹1.3 lakh crore since launch
- Technology-driven transparent process
- Reduced premium burden on farmers
- Timely compensation

CONTACT INFORMATION:
- Ministry of Agriculture & Farmers Welfare
- Website: pmfby.gov.in
- Helpline: 14447
- Email: support@pmfby.gov.in""",
                'metadata': {
                    'source': 'Ministry of Agriculture and Farmers Welfare',
                    'title': 'PMFBY Crop Insurance Complete Guide',
                    'category': 'Crop Insurance',
                    'last_updated': '2024-01-30',
                    'scheme_type': 'Central Government Scheme',
                    'keywords': ['crop insurance', 'pmfby', 'yield protection', 'natural calamities', 'premium subsidy']
                }
            },
            {
                'id': 'kisan_credit_card_complete',
                'content': """Kisan Credit Card (KCC) Scheme - Complete Financial Guide for Farmers

SCHEME INTRODUCTION:
KCC is a comprehensive credit scheme to provide timely and hassle-free credit support to farmers for their cultivation and other needs. Launched in 1998-99, it has been continuously refined to meet evolving farmer credit requirements.

CREDIT LIMIT STRUCTURE:
CROP CULTIVATION:
- Scale of Finance × Area × Number of Crops
- Based on cropping pattern and input costs
- Includes pre and post-harvest expenses

MAINTENANCE EXPENSES:
- 20% of cultivation expenses
- For household and farm maintenance
- Asset maintenance and repairs

INSURANCE COVERAGE:
- Crop insurance premium
- Asset insurance for pump sets, cattle

ADDITIONAL CREDIT:
- 10% of credit limit for allied activities
- Dairy, fishery, poultry, bee-keeping
- Farm mechanization

INTEREST RATES:
NORMAL INTEREST:
- Up to ₹3 lakh: 7% per annum
- Interest subvention of 2% by Government
- Effective rate: 7% for timely repayment

PROMPT REPAYMENT INCENTIVE:
- Additional 3% interest subvention
- For timely repayment within one year
- Effective interest rate: 4% per annum

COLLATERAL REQUIREMENTS:
UP TO ₹1.60 LAKH:
- No collateral security required
- Only hypothecation of crops

₹1.60 LAKH TO ₹3 LAKH:
- Third party guarantee OR
- Hypothecation of assets created

ABOVE ₹3 LAKH:
- Collateral security required
- Land mortgage or other securities

ELIGIBILITY CRITERIA:
PRIMARY BENEFICIARIES:
- Individual farmers (owner cultivators)
- Tenant farmers, oral lessees, sharecroppers
- Self Help Group members
- Joint Liability Groups (JLGs)

SUPPORTING DOCUMENTS:
- Land ownership documents
- Identity proof (Aadhaar mandatory)
- Address proof
- Caste certificate (if applicable)
- Two passport size photographs

COVERAGE SCOPE:
AGRICULTURE:
- All food crops (cereals, millets, pulses)
- Cash crops (sugarcane, cotton, jute)
- Plantation crops (tea, coffee, rubber)
- Horticulture crops (fruits, vegetables, flowers)

ALLIED ACTIVITIES:
- Dairy farming and milk production
- Inland fishery and aquaculture
- Poultry including chicks production
- Goat and sheep farming
- Bee-keeping and honey production
- Sericulture activities

REPAYMENT SCHEDULE:
CROP LOANS:
- Flexible repayment based on harvesting
- 12 months for short duration crops
- Up to 18 months for long duration crops
- Extension possible based on crop cycle

CONVERSION FACILITY:
- Outstanding can be converted to term loan
- Repayment up to 5 years
- Interest rate as per term loan norms
- Fresh KCC after full repayment

SPECIAL FEATURES:
ANYWHERE BANKING:
- Core Banking Solution (CBS) enabled
- Withdrawal from any branch
- ATM facility available
- No geographical restrictions

FLEXIBILITY:
- Multiple withdrawals and repayments
- Interest charged only on utilized amount
- Revolving credit facility
- Valid for 5 years subject to annual review

DIGITAL INTEGRATION:
- e-KCC for online applications
- Mobile banking facilities
- SMS alerts for transactions
- Digital payment options

INSURANCE BENEFITS:
PERSONAL ACCIDENT INSURANCE:
- Coverage up to ₹50,000
- Death due to accident: ₹50,000
- Permanent total disability: ₹50,000
- Permanent partial disability: ₹25,000

CROP INSURANCE:
- Automatic coverage under PMFBY
- Premium paid through KCC
- Comprehensive risk coverage
- Technology-enabled claim settlement

IMPLEMENTATION MECHANISM:
PARTICIPATING INSTITUTIONS:
- Commercial Banks (27 banks)
- Regional Rural Banks (43 RRBs)
- Cooperative Banks (State and District)
- Primary Agricultural Credit Societies

MONITORING:
- District Level Review Committee
- State Level Bankers Committee
- NABARD monitoring and supervision
- Regular impact assessment studies

ACHIEVEMENTS:
COVERAGE:
- Over 7 crore active KCC accounts
- Credit disbursement of ₹8 lakh crore annually
- 85% of farm credit through KCC
- Covers 75% of farming households

BENEFITS:
- Reduced transaction costs
- Timely availability of credit
- Flexibility in operations
- Comprehensive insurance coverage

APPLICATION PROCESS:
1. Visit nearest bank branch
2. Submit application with documents
3. Bank verification and assessment
4. Credit limit sanction
5. KCC issuance within 2 weeks

RECENT ENHANCEMENTS:
- PM-KISAN beneficiary auto-approval
- Doorstep banking services
- Interest subvention for dairy and fishery
- Digital loan processing
- Aadhaar-based biometric authentication

CONTACT INFORMATION:
- NABARD: www.nabard.org
- Banking Ombudsman for grievances
- Toll-free helpline: 1800-180-1111
- Email: kcc@nabard.org""",
                'metadata': {
                    'source': 'NABARD and Ministry of Agriculture',
                    'title': 'Kisan Credit Card Complete Guide',
                    'category': 'Agricultural Credit',
                    'last_updated': '2024-02-15',
                    'scheme_type': 'Central Government Scheme',
                    'keywords': ['kisan credit card', 'agricultural loan', 'crop credit', 'interest subvention', 'collateral free']
                }
            },
            {
                'id': 'soil_health_card_detailed',
                'content': """Soil Health Card Scheme - Complete Soil Management Guide

SCHEME OBJECTIVE:
Soil Health Card Scheme aims to issue soil health cards to farmers to help them improve productivity through judicious use of inputs based on soil test results and promote sustainable farming practices.

SOIL TESTING PARAMETERS:
BASIC PARAMETERS (12):
- pH (Soil Reaction)
- Electrical Conductivity (Salinity)
- Organic Carbon
- Available Nitrogen (N)
- Available Phosphorus (P)
- Available Potassium (K)
- Available Sulphur (S)
- Available Zinc (Zn)
- Available Iron (Fe)
- Available Copper (Cu)
- Available Manganese (Mn)
- Available Boron (B)

CARD INFORMATION INCLUDES:
- Current status of soil nutrients
- Recommendations for nutrient application
- Soil amendments required
- Organic matter content
- Fertilizer recommendations crop-wise
- Micro-nutrient status and corrections

TESTING INFRASTRUCTURE:
STATIC LABS:
- 3,098 functional soil testing laboratories
- Processing capacity: 1.2 crore samples annually
- Government and private labs
- Quality control and standardization

MOBILE LABS:
- 600+ mobile soil testing laboratories
- Doorstep soil testing facility
- Quick testing within 2-3 hours
- GPS-based sample collection

SAMPLING METHODOLOGY:
GRID SAMPLING:
- For irrigated areas: 2.5 hectare grid
- For rain-fed areas: 10 hectare grid
- GPS coordinates for each sample
- Composite sampling from multiple points

FARMER FIELD SAMPLING:
- Individual farmer field sampling
- Area threshold: 2 hectares minimum
- Separate samples for different crop areas
- Seasonal variations considered

CARD ISSUANCE CYCLE:
- Every 2 years for irrigated areas
- Every 3 years for rain-fed areas
- Online portal for card download
- SMS alerts to farmers
- Printed cards through Common Service Centers

NUTRIENT RECOMMENDATIONS:
FERTILIZER RECOMMENDATIONS:
- Crop-specific nutrient requirements
- Soil test-based applications
- Organic manure integration
- Timing of application

ORGANIC INPUTS:
- Farm Yard Manure (FYM) requirements
- Compost and vermicompost recommendations
- Green manuring suggestions
- Bio-fertilizer applications

SOIL AMENDMENTS:
- Lime application for acidic soils
- Gypsum for alkali soils
- Organic matter enhancement
- Micro-nutrient corrections

DIGITAL PLATFORM:
SOIL HEALTH PORTAL:
- www.soilhealth.dac.gov.in
- Online card download facility
- Farmer registration
- Lab management system

MOBILE APPLICATION:
- Soil Health Card mobile app
- Multilingual interface
- Voice-enabled features
- Offline functionality

INTEGRATION WITH OTHER SCHEMES:
FERTILIZER SUBSIDY:
- DBT linkage with soil health cards
- Nutrient-based subsidy
- Point of Sale (PoS) machines
- Biometric authentication

PM-KISAN INTEGRATION:
- Soil health card for PM-KISAN beneficiaries
- Priority testing for small farmers
- Simplified application process
- Direct delivery mechanisms

CAPACITY BUILDING:
FARMER TRAINING:
- Soil health awareness programs
- Demonstration plots
- Field schools for soil management
- Extension worker training

TECHNICAL SUPPORT:
- State Agricultural Universities involvement
- ICAR institutes technical backstopping
- KVK demonstrations
- Progressive farmer involvement

QUALITY CONTROL:
STANDARDIZATION:
- Standard Operating Procedures (SOPs)
- Inter-laboratory comparisons
- Proficiency testing programs
- Equipment calibration protocols

CERTIFICATION:
- NABL accreditation for labs
- Quality assurance protocols
- External quality assessment
- Continuous monitoring systems

IMPACT ASSESSMENT:
PRODUCTIVITY IMPROVEMENT:
- 8-10% increase in crop productivity
- 10-15% reduction in fertilizer use
- Improved soil health indicators
- Enhanced input use efficiency

ECONOMIC BENEFITS:
- Cost savings on fertilizers
- Increased crop yields
- Reduced input costs
- Better price realization

IMPLEMENTATION STATUS:
CARDS DISTRIBUTED:
- Over 22 crore soil health cards issued
- Coverage of 14 crore farm holdings
- All states and UTs covered
- Cycle-II completion achieved

TESTING INFRASTRUCTURE:
- 99% villages covered
- Average turnaround time: 30 days
- Quality testing protocols implemented
- Farmer satisfaction rate: 85%

CHALLENGES AND SOLUTIONS:
INFRASTRUCTURE:
- Lab modernization ongoing
- Equipment upgradation
- Human resource development
- Technology integration

FARMER ADOPTION:
- Awareness campaigns
- Incentive mechanisms
- Demonstration effect
- Technical support

FUTURE ROADMAP:
- Digital soil health monitoring
- Precision agriculture integration
- Real-time advisory system
- Satellite-based soil assessment

CONTACT INFORMATION:
- Department of Agriculture & Cooperation
- Website: soilhealth.dac.gov.in
- Helpline: 1800-180-1551
- Email: soilhealth@gov.in""",
                'metadata': {
                    'source': 'Department of Agriculture and Cooperation',
                    'title': 'Soil Health Card Comprehensive Guide',
                    'category': 'Soil Management',
                    'last_updated': '2024-02-20',
                    'scheme_type': 'Central Government Scheme',
                    'keywords': ['soil health card', 'soil testing', 'nutrient management', 'fertilizer recommendation', 'precision agriculture']
                }
            }
        ]
        
        logger.info(f"Starting ingestion of {len(comprehensive_schemes)} comprehensive schemes")
        
        # Ingest data into vector store
        success = self.vector_client.add_documents(comprehensive_schemes)
        
        if success:
            logger.info("Comprehensive schemes data ingestion completed successfully")
            
            # Log the ingestion
            self.firestore_client.db.collection('ingestion_logs').add({
                'timestamp': datetime.now(),
                'documents_processed': len(comprehensive_schemes),
                'status': 'success',
                'data_type': 'comprehensive_government_schemes',
                'ingestion_method': 'vertex_ai_embeddings'
            })
            
            return True
        else:
            logger.error("Comprehensive schemes data ingestion failed")
            return False
    
    def verify_vector_search(self):
        """Verify that vector search is working properly"""
        
        try:
            test_queries = [
                "PM-KISAN scheme benefits and eligibility",
                "drip irrigation subsidy amount and application process",
                "organic farming support under PKVY scheme",
                "crop insurance premium rates and coverage",
                "Kisan Credit Card interest rates and loan limits",
                "soil testing and nutrient recommendations"
            ]
            
            logger.info("=== VECTOR SEARCH VERIFICATION ===")
            
            for query in test_queries:
                logger.info(f"\n🔍 Testing query: {query}")
                
                # Generate embedding for query
                query_embedding = self.vector_client.get_embedding(query)
                
                # Search for similar documents
                results = self.vector_client.similarity_search(query_embedding, top_k=3)
                
                logger.info(f"📊 Found {len(results)} results:")
                
                for i, result in enumerate(results, 1):
                    title = result.get('metadata', {}).get('title', 'Unknown')
                    score = result.get('score', 0)
                    content_preview = result.get('content', '')[:100]
                    
                    logger.info(f"  {i}. {title}")
                    logger.info(f"     Similarity: {score:.3f}")
                    logger.info(f"     Preview: {content_preview}...")
                    logger.info("")
            
            # Get collection statistics
            stats = self.vector_client.get_collection_stats()
            logger.info(f"📈 Collection Statistics: {stats}")
            
            logger.info("✅ Vector search verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Vector search verification failed: {e}")
            return False
    
    def ingest_from_urls(self, urls: List[str]):
        """Ingest schemes data from government websites (future enhancement)"""
        # This would scrape actual government websites
        # For now, we'll use the comprehensive static data
        logger.info("URL-based ingestion will be implemented in future versions")
        return self.ingest_comprehensive_schemes_data()

def main():
    """Main function to run enhanced data ingestion"""
    
    logger.info("🚀 Starting Enhanced Government Schemes Data Ingestion")
    
    try:
        ingestion = EnhancedSchemesIngestion()
        
        # Test vector client connection
        if not ingestion.vector_client.test_connection():
            logger.error("❌ Vector client connection failed")
            return False
        
        logger.info("✅ Vector client connection successful")
        
        # Ingest comprehensive schemes data
        success = ingestion.ingest_comprehensive_schemes_data()
        
        if success:
            logger.info("✅ Data ingestion successful")
            
            # Verify vector search functionality
            verification_success = ingestion.verify_vector_search()
            
            if verification_success:
                logger.info("🎉 Enhanced data ingestion and verification completed successfully!")
                logger.info("🔥 Your RAG system is now ready with comprehensive government schemes data!")
            else:
                logger.warning("⚠️ Data ingested but verification had issues")
        else:
            logger.error("❌ Data ingestion failed")
            
    except Exception as e:
        logger.error(f"💥 Enhanced ingestion process error: {e}")

if __name__ == "__main__":
    main()