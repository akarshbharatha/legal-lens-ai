import os
import pickle
from PyPDF2 import PdfReader
import glob

def extract_text_from_pdfs(dataset_folder):
    """
    Extract text from all PDF files in the dataset folder
    
    Args:
        dataset_folder: Path to folder containing PDF files
        
    Returns:
        texts: List of extracted text from each PDF
        filenames: List of PDF filenames
    """
    texts = []
    filenames = []
    
    # Get all PDF files
    pdf_files = glob.glob(os.path.join(dataset_folder, '*.PDF'))
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for pdf_path in pdf_files:
        try:
            # Read PDF
            reader = PdfReader(pdf_path)
            
            # Extract text from all pages
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            texts.append(text)
            filenames.append(os.path.basename(pdf_path))
            
            if len(texts) % 10 == 0:
                print(f"Processed {len(texts)} PDFs...")
                
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            continue
    
    # Save extracted data for faster loading next time
    try:
        with open('extracted_data.pkl', 'wb') as f:
            pickle.dump((texts, filenames), f)
        print(f"\nExtracted data saved to extracted_data.pkl")
    except Exception as e:
        print(f"Could not save extracted data: {str(e)}")
    
    return texts, filenames

def load_extracted_data():
    """Load previously extracted data from pickle file"""
    try:
        with open('extracted_data.pkl', 'rb') as f:
            texts, filenames = pickle.load(f)
        print(f"Loaded {len(filenames)} cases from extracted_data.pkl")
        return texts, filenames
    except FileNotFoundError:
        print("No extracted_data.pkl found. Please extract data first.")
        raise

