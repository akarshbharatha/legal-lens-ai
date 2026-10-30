# Legal Case Reference Finder

A simple NLP-based application to find similar legal cases from a dataset of PDF documents using TF-IDF and cosine similarity.

## Features

- 📄 Extract text from legal case PDFs
- 🤖 Find similar cases using TF-IDF (Term Frequency-Inverse Document Frequency)
- ✂️ Automatic case summarization for better matching
- 🤖 AI-Powered verdict prediction (optional, requires OpenAI API)
- 📊 Win probability analysis with detailed reasoning
- 🎨 Modern and intuitive web interface
- ⚡ Fast and efficient text matching
- 📄 Direct PDF viewing for reference cases

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Flask application:
```bash
python app.py
```

2. Wait for the dataset to load:
   - The application automatically extracts text from PDFs on first startup
   - This may take a few minutes
   - You'll see "Model loaded successfully" message in the console

3. Open your browser and navigate to:
```
http://localhost:5000
```

4. Search for similar cases:
   - Enter your case study in the text area
   - Click "Find Similar Cases"
   - View the top 5 most similar cases with their similarity scores
   - Click "Open PDF" button on any result to view the full case document

## How It Works

1. **PDF Extraction**: Text is extracted from all PDF files in the `Dataset` folder
2. **Summarization**: Your case study is automatically summarized using extractive summarization
3. **Text Vectorization**: TF-IDF is used to convert case texts into numerical vectors
4. **Similarity Matching**: Cosine similarity finds the most similar cases based on the summarized input
5. **Results Display**: Top 5 matching cases are displayed with similarity scores and PDF access

## Project Structure

```
Legal-sum/
├── app.py                 # Flask backend application
├── pdf_extractor.py       # PDF text extraction utility
├── nlp_model.py          # TF-IDF based NLP model
├── summarizer.py         # Extractive summarization module
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend JavaScript
└── Dataset/              # Legal case PDFs
```

## Technologies Used

- **Backend**: Flask (Python)
- **NLP**: scikit-learn TF-IDF
- **Summarization**: Extractive summarization (word frequency + legal keyword boosting)
- **AI Analysis**: OpenAI GPT-4o-mini (optional)
- **Frontend**: HTML, CSS, JavaScript
- **PDF Processing**: PyPDF2

## AI Analysis Setup (Optional)

To enable AI-powered verdict prediction:
1. Get OpenAI API key from https://platform.openai.com/api-keys
2. Set environment variable: `OPENAI_API_KEY=sk-your-key`
3. See `SETUP_AI.md` for detailed instructions
4. Without API key, all other features work normally

## Notes

- **Automatic Loading**: The dataset loads automatically when you start the application
- **Summarization**: Your case study is automatically summarized to extract key points before matching
- **Cached Data**: Extracted data is cached in `extracted_data.pkl` for faster subsequent loads
- **Similarity Scores**: Range from 0-100%
- **PDF Opening**: Click "Open PDF" button on any result to view the full case document
- **Model**: Uses TF-IDF with unigrams and bigrams for better matching
- **First Run**: Will take time to extract text from all PDFs (subsequent runs are faster)
- **No Deep Learning**: Uses simple extractive summarization without PyTorch/TensorFlow for simplicity

