# scripts/ingest_schemes_data.py
"""
Data ingestion script to populate the vector database with government schemes information.
This script processes documents and creates embeddings using Google AI technologies.
"""

import os
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from utils.vector_store_client import VectorStoreClient
from utils.firestore_client import FirestoreClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchemesDataIngestion:
    """Ingest government schemes data into vector database"""
    
    def __init__(self):
        self.vector_store = VectorStoreClient()
        self.firestore_client = FirestoreClient()
        
    def ingest_sample_data(self):
        """Ingest sample government schemes data"""
        
        sample_schemes = [
            {
                'id': 'pm_kisan_001',
                'content': """PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) Scheme
                
This is a Central Sector Scheme that provides income support to farmer families. Under this scheme, financial benefit of Rs. 6000 per year is provided to eligible farmer families in three equal installments of Rs. 2000 each every four months.

Eligibility Criteria:
- All landholding farmer families having cultivable land holding
- Farmer families having combined land holding/ownership of upto 2 hectares
- Both husband and wife can get benefit if they have separate land holdings

Benefits:
- Direct cash transfer of Rs. 6000 per year
- Amount transferred directly to bank accounts
- No intermediaries involved

Application Process:
- Apply online at pmkisan.gov.in
- Visit nearest Common Service Center (CSC)
- Contact local agriculture department
- Required documents: Aadhaar card, bank account details, land ownership documents""",
                'metadata': {
                    'source': 'Ministry of Agriculture and Farmers Welfare',
                    'title': 'PM-KISAN Scheme',
                    'category': 'Income Support',
                    'last_updated': '2024-01-15',
                    'scheme_type': 'Central Government Scheme'
                }
            },
            {
                'id': 'drip_irrigation_002',
                'content': """Drip Irrigation Subsidy Scheme
                
The government provides subsidies for drip irrigation systems to promote water-efficient farming practices. This scheme aims to increase water use efficiency and crop productivity.

Subsidy Amount:
- Small and marginal farmers: Up to 55% subsidy
- Other farmers: Up to 45% subsidy
- Additional 10% subsidy for SC/ST farmers

Eligible Crops:
- Fruits: Mango, citrus, pomegranate, grapes
- Vegetables: Tomato, onion, potato, cabbage
- Cash crops: Cotton, sugarcane
- Spices and condiments

Technical Specifications:
- Minimum area: 0.5 hectares
- Maximum area: 5 hectares per farmer
- Quality components as per BIS standards

Application Process:
- Apply through state horticulture department
- Submit technical proposal and cost estimate
- Field verification by technical officer
- Installation by approved vendors only""",
                'metadata': {
                    'source': 'Department of Agriculture and Cooperation',
                    'title': 'Drip Irrigation Subsidy',
                    'category': 'Water Management',
                    'last_updated': '2024-02-10',
                    'scheme_type': 'State/Central Government Scheme'
                }
            },
            {
                'id': 'organic_farming_003',
                'content': """Paramparagat Krishi Vikas Yojana (PKVY) - Organic Farming
                
PKVY is an elaborate component of Soil Health Management (SHM) under National Mission of Sustainable Agriculture (NMSA). The scheme promotes organic farming and certification.

Financial Assistance:
- Rs. 50,000 per hectare over 3 years
- Rs. 31,000 for organic inputs and cultivation
- Rs. 8,800 for certification and organic premium
- Rs. 10,200 for formation of farmer groups

Cluster Formation:
- Minimum 50 farmers in each cluster
- 50 hectare area coverage
- Participatory Guarantee System (PGS) certification

Benefits:
- Reduction in input costs
- Premium prices for organic produce
- Soil health improvement
- Environmental sustainability
- Export opportunities

Support Provided:
- Training on organic farming practices
- Input supply at subsidized rates
- Market linkage support
- Certification assistance""",
                'metadata': {
                    'source': 'Department of Agriculture and Cooperation',
                    'title': 'Paramparagat Krishi Vikas Yojana (PKVY)',
                    'category': 'Organic Farming',
                    'last_updated': '2024-01-20',
                    'scheme_type': 'Central Government Scheme'
                }
            },
            {
                'id': 'dairy_farming_004',
                'content': """National Livestock Mission - Dairy Development
                
The scheme supports dairy development through various interventions including breed improvement, feed and fodder development, and infrastructure development.

Credit Support:
- Bank loans up to Rs. 10 lakhs for individual farmers
- Subsidy: 25% for general category, 33.33% for SC/ST
- Interest subvention of 2% available

Eligible Activities:
- Purchase of milch animals (cow, buffalo)
- Construction of cattle shed
- Milk processing equipment
- Fodder cultivation and storage
- Biogas plant installation

Breed Improvement:
- Artificial insemination services
- Frozen semen supply
- Breed up-gradation programs
- Training for farmers and veterinarians

Infrastructure Support:
- Milk collection centers
- Chilling units
- Processing facilities
- Marketing support

Technical Support:
- Veterinary services
- Vaccination programs
- Feed testing facilities
- Training and capacity building""",
                'metadata': {
                    'source': 'Department of Animal Husbandry and Dairying',
                    'title': 'National Livestock Mission - Dairy',
                    'category': 'Livestock Development',
                    'last_updated': '2024-02-05',
                    'scheme_type': 'Central Government Scheme'
                }
            },
            {
                'id': 'crop_insurance_005',
                'content': """Pradhan Mantri Fasal Bima Yojana (PMFBY)
                
PMFBY provides comprehensive crop insurance coverage against all non-preventable natural risks from pre-sowing to post-harvest stage.

Premium Rates:
- Kharif crops: Maximum 2% of sum insured
- Rabi crops: Maximum 1.5% of sum insured
- Annual commercial/horticultural crops: Maximum 5% of sum insured

Coverage:
- Yield losses due to natural calamities
- Prevented sowing/planting risk
- Post-harvest losses (up to 14 days)
- Localized calamities (hailstorm, landslide, inundation)

Sum Insured:
- Scale of finance × area OR
- Average yield × MSP × area (whichever is higher)

Claim Settlement:
- Technology-based assessment
- Quick settlement within 45 days
- Direct benefit transfer to farmer accounts

Enrollment:
- Compulsory for loanee farmers
- Voluntary for non-loanee farmers
- Enrollment through banks, CSCs, or online portal""",
                'metadata': {
                    'source': 'Ministry of Agriculture and Farmers Welfare',
                    'title': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
                    'category': 'Crop Insurance',
                    'last_updated': '2024-01-30',
                    'scheme_type': 'Central Government Scheme'
                }
            }
        ]
        
        logger.info(f"Starting ingestion of {len(sample_schemes)} sample schemes")
        
        # Ingest data into vector store
        success = self.vector_store.add_documents(sample_schemes)
        
        if success:
            logger.info("Sample data ingestion completed successfully")
            
            # Create metadata record
            self.firestore_client.db.collection('ingestion_logs').add({
                'timestamp': datetime.now(),
                'documents_processed': len(sample_schemes),
                'status': 'success',
                'data_type': 'government_schemes_sample'
            })
            
            return True
        else:
            logger.error("Sample data ingestion failed")
            return False
    
    def ingest_from_json_file(self, file_path: str):
        """Ingest schemes data from JSON file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                schemes_data = json.load(file)
            
            logger.info(f"Loading {len(schemes_data)} schemes from {file_path}")
            
            # Convert to expected format
            documents = []
            for i, scheme in enumerate(schemes_data):
                doc = {
                    'id': scheme.get('id', f'scheme_{i}'),
                    'content': scheme.get('content', ''),
                    'metadata': scheme.get('metadata', {})
                }
                documents.append(doc)
            
            # Ingest into vector store
            success = self.vector_store.add_documents(documents)
            
            if success:
                logger.info(f"Successfully ingested {len(documents)} schemes from file")
                
                # Log ingestion
                self.firestore_client.db.collection('ingestion_logs').add({
                    'timestamp': datetime.now(),
                    'documents_processed': len(documents),
                    'status': 'success',
                    'data_type': 'json_file',
                    'source_file': file_path
                })
                
                return True
            else:
                logger.error("File-based ingestion failed")
                return False
                
        except Exception as e:
            logger.error(f"Error ingesting from file {file_path}: {e}")
            return False
    
    def verify_ingestion(self):
        """Verify that data has been properly ingested"""
        
        try:
            # Test query
            test_queries = [
                "PM-KISAN scheme benefits",
                "drip irrigation subsidy",
                "organic farming support"
            ]
            
            for query in test_queries:
                logger.info(f"Testing query: {query}")
                
                # Generate embedding
                embedding = self.vector_store.get_embedding(query)
                
                # Search for similar documents
                results = self.vector_store.similarity_search(embedding, top_k=3)
                
                logger.info(f"Found {len(results)} results for query: {query}")
                
                for i, result in enumerate(results, 1):
                    logger.info(f"  Result {i}: {result.get('metadata', {}).get('title', 'Unknown')} (score: {result.get('score', 0):.3f})")
            
            logger.info("Ingestion verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Ingestion verification failed: {e}")
            return False

def main():
    """Main function to run data ingestion"""
    
    logger.info("Starting Government Schemes Data Ingestion")
    
    try:
        ingestion = SchemesDataIngestion()
        
        # Ingest sample data
        success = ingestion.ingest_sample_data()
        
        if success:
            # Verify ingestion
            ingestion.verify_ingestion()
            logger.info("Data ingestion process completed successfully")
        else:
            logger.error("Data ingestion process failed")
            
    except Exception as e:
        logger.error(f"Ingestion process error: {e}")

if __name__ == "__main__":
    main()