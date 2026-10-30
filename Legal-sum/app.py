from flask import Flask, render_template, request, jsonify, send_file
from pdf_extractor import extract_text_from_pdfs, load_extracted_data
from nlp_model import LegalCaseMatcher
from summarizer import LegalCaseSummarizer
from ai_analyzer import LegalAIAnalyzer
from chatbot import LegalChatbot
import os
import io
from PyPDF2 import PdfReader

app = Flask(__name__)

# Global objects
model = None
summarizer = None
ai_analyzer = None
chatbot = None


# ============================
# INITIALIZE MODEL ON STARTUP
# ============================
def initialize_model():
    global model, summarizer, ai_analyzer, chatbot

    try:
        # Initialize summarizer
        summarizer = LegalCaseSummarizer()
        print("✓ Summarizer initialized.")

        # Initialize AI analyzer
        ai_analyzer = LegalAIAnalyzer()
        if ai_analyzer.is_available():
            print("✓ AI Analyzer initialized with GPT-4o-mini.")
        else:
            print("⚠ AI Analyzer not available (no OPENAI_API_KEY).")

        dataset_path = "Dataset"

        # Load or extract data
        if os.path.exists("extracted_data.pkl"):
            print("Loading cached data...")
            texts, filenames = load_extracted_data()
        else:
            print("Extracting text from PDFs...")
            texts, filenames = extract_text_from_pdfs(dataset_path)

        # Train model
        print("Training model...")
        model = LegalCaseMatcher()
        model.train(texts, filenames)
        print(f"✓ Model loaded successfully. {len(filenames)} cases indexed.")

        # ✅ Create chatbot AFTER model training
        chatbot = LegalChatbot(model)

    except Exception as e:
        print(f"❌ Error loading model: {e}")
        model = None
        chatbot = None


# Run initialization
initialize_model()

# ============================
# ROUTES
# ============================

@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/search')
def index():
    return render_template('index.html')


@app.route('/pdf/<filename>')
def get_pdf(filename):
    try:
        pdf_path = os.path.join('Dataset', filename)
        if os.path.exists(pdf_path):
            return send_file(pdf_path, mimetype='application/pdf')
        return jsonify({'error': 'PDF not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search_cases():
    try:
        data = request.json
        case_study = data.get('case_study', '')

        if not case_study:
            return jsonify({'error': 'No case study provided'}), 400

        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500

        # Use FULL case text for matching (not summarized)
        # This way exact duplicates will get 100% match
        results = model.find_similar_cases(case_study, top_n=5)
        
        # Generate summary separately for display
        summarized_case = summarizer.summarize_case_study(case_study, max_sentences=3)

        ai_analysis = None
        if ai_analyzer and ai_analyzer.is_available():
            ai_analysis = ai_analyzer.analyze_case(case_study, results)

        return jsonify({
            'results': results,
            'original_summary': case_study,
            'summarized_input': summarized_case,
            'ai_analysis': ai_analysis
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search-pdf', methods=['POST'])
def search_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files allowed'}), 400
        
        # Extract text from uploaded PDF
        try:
            pdf_reader = PdfReader(io.BytesIO(file.read()))
            extracted_text = ""
            
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
            
            if not extracted_text.strip():
                return jsonify({'error': 'Could not extract text from PDF. The file may be empty or corrupted.'}), 400
        
        except Exception as e:
            return jsonify({'error': f'Error reading PDF: {str(e)}'}), 400
        
        # Process extracted text same as regular search
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Use FULL extracted text for matching (not summarized)
        results = model.find_similar_cases(extracted_text, top_n=5)
        
        # Generate summary separately for display
        summarized_case = summarizer.summarize_case_study(extracted_text, max_sentences=3)
        
        ai_analysis = None
        if ai_analyzer and ai_analyzer.is_available():
            ai_analysis = ai_analyzer.analyze_case(extracted_text, results)
        
        return jsonify({
            'results': results,
            'original_summary': extracted_text[:500],
            'summarized_input': summarized_case,
            'ai_analysis': ai_analysis
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    try:
        data = request.json
        text = data.get('text', '')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        if summarizer is None:
            return jsonify({'error': 'Summarizer not initialized'}), 500

        summary = summarizer.summarize(text, max_sentences=5)
        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    if chatbot is None:
        return jsonify({"reply": "Chatbot is still initializing. Please wait."})

    data = request.json
    user_message = data.get("message", "")

    reply = chatbot.get_response(user_message)
    return jsonify({"reply": reply})


@app.route("/chatbot")
def chatbot_ui():
    return render_template("chat.html")


# ============================
# RUN SERVER
# ============================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
