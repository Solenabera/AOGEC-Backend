from functools import lru_cache
import re
from gradio_client import Client
from nlp import SentenceSplitter, Tokenizer, SpellingChecker, AutoComplete
from config import settings

# --- NLP Utilities (instantiate once) ---
sentence_splitter = SentenceSplitter.SentenceSplitter()
word_tokenizer = Tokenizer.Tokenizer()
spell_checker = SpellingChecker.SpellingChecker()
autocomplete_engine = AutoComplete.AutoComplete(
    spell_checker.wordSet,
    spell_checker.wordFreq
)

# --- Hugging Face Client Setup ---
@lru_cache(maxsize=1)
def get_hf_client():
    # Connects directly to your deployed Gradio app
    return Client("solenabera55/AOGEC")

def process_text(text: str, selectedCorrectionType: str, IPAddress: str, userId: int | None):
    sentences = sentence_splitter.split(text)

    final_result = []
    grammar_candidates = []
    grammar_indexes = []

    # --- Pass 1: Local Spelling Check and Sentence Filtering ---
    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            continue

        tokens, _ = word_tokenizer.tokenizer(sentence)
        correction_dict = spell_checker.spellCheck(tokens)

        result = {
            "sentenceIndex": i,
            "originalSentence": sentence,
            "spellingCorrections": correction_dict or {},
            "candidateSuggestions": [],
            "errorDescriptionEnglish": "Spelling mistake detected!" if correction_dict else "None",
            "errorDescriptionAfaanOromo": "Dogoggorri qubee argame!" if correction_dict else "None",
        }

        # Only collect for grammar correction if not spelling-only
        if selectedCorrectionType != "Spelling":
            # Original logic: only run grammar if no spelling errors and length >= 3
            if not correction_dict and len(tokens) >= 3:
                grammar_candidates.append(sentence)
                grammar_indexes.append(len(final_result))

        final_result.append(result)

    # --- Pass 2: Cloud Grammar Correction (Hugging Face Batching) ---
    if selectedCorrectionType != "Spelling" and grammar_candidates:
        try:
            # Join the candidate sentences into a single payload separated by newlines
            input_payload = "\n".join(grammar_candidates)
            client = get_hf_client()
            
            # Make a single batch call. 
            # Passing it positionally without api_name forces it to auto-detect the only available endpoint.
            corrected_text, breakdown = client.predict(
                input_payload
            )
            
            # Split the returned string back into a list
            corrected_sentences = [s.strip() for s in corrected_text.split('\n') if s.strip()]
            
            # Extract the specific error types from the breakdown text using Regex
            detected_errors = re.findall(r"🔍 Detected:\s*(.+)", breakdown)
            
            # Map corrections back to the JSON payload
            for i, (idx, corrected) in enumerate(zip(grammar_indexes, corrected_sentences)):
                error_type = detected_errors[i].strip() if i < len(detected_errors) else "unknown"
                
                suggestions = []
                if corrected and corrected.lower() != final_result[idx]["originalSentence"].lower():
                    suggestions.append(corrected)
                
                final_result[idx]["candidateSuggestions"] = suggestions
                
                # Assign error descriptions based on what the HF model detected
                if error_type not in ["no-error", "unknown"] and suggestions:
                    final_result[idx]["errorDescriptionEnglish"] = error_type
                    final_result[idx]["errorDescriptionAfaanOromo"] = error_type
                else:
                    final_result[idx]["errorDescriptionEnglish"] = "No errors detected"
                    final_result[idx]["errorDescriptionAfaanOromo"] = "Dogoggorri hin jiru"
                    
        except Exception as e:
            print(f"Hugging Face API Error: {e}")
            for idx in grammar_indexes:
                final_result[idx]["errorDescriptionEnglish"] = "API Error"
                final_result[idx]["errorDescriptionAfaanOromo"] = "Rakkoo API"

    # --- Final Formatting: Capitalize sentences safely ---
    for item in final_result:
        if item.get("originalSentence"):
            item["originalSentence"] = item["originalSentence"].capitalize()

        if item.get("candidateSuggestions"):
            item["candidateSuggestions"] = [
                s.capitalize() if isinstance(s, str) else s
                for s in item["candidateSuggestions"]
            ]

    return final_result

# --- Original AutoComplete Function ---
def autocomplete_suggestions(query: str):
    return autocomplete_engine.suggest(query)

# --- Original Utility Function ---
def capitalize_sentences(sentences):
    return [s.capitalize() for s in sentences if isinstance(s, str)]