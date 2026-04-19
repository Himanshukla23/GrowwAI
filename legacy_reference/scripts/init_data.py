import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.phase2.app.services.ingestion_service import get_processed_restaurants
from src.phase3.database import upsert_restaurants

def main():
    print("Initializing Hugging Face data ingestion...")
    try:
        # This will download the Zomato dataset and process it
        print("Fetching and cleaning data from Hugging Face...")
        df = get_processed_restaurants(force_refresh=True)
        print(f"Processed {len(df)} unique records.")
        
        # This will save the data to the SQLite database
        print("Saving data to SQLite database...")
        upsert_restaurants(df)
        print("Database successfully initialized with real Zomato data!")
    except Exception as e:
        print(f"Ingestion failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
