from functools import lru_cache
import json
from nlp import SentenceSplitter, Tokenizer, SpellingChecker, AutoComplete
from dl.inference import check_and_correct, batch_correction
from config import settings
import google.generativeai as genai


# NLP Utilities (instantiate once)
sentence_splitter = SentenceSplitter.SentenceSplitter()
word_tokenizer = Tokenizer.Tokenizer()
spell_checker = SpellingChecker.SpellingChecker()
autocomplete_engine = AutoComplete.AutoComplete(
    spell_checker.wordSet,
    spell_checker.wordFreq
)

def process_text(text: str, selectedCorrectionType: str, IPAddress: str, userId: int | None):
    sentences = sentence_splitter.split(text)
    # Add SentenceSplitter to split text into sentences by Gemini model, then process each sentence for spelling and grammar corrections. Finally, return the corrected sentences in a structured format.

    final_result = []
    grammar_candidates = []
    grammar_indexes = []

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
            if not correction_dict and len(tokens) >= 3:
                grammar_candidates.append(sentence)
                grammar_indexes.append(len(final_result))

        final_result.append(result)

    # Grammar correction (batch) only if not spelling-only
    if selectedCorrectionType != "Spelling" and grammar_candidates:
        correct_suggestion_local_model = batch_correction(grammar_candidates)
        gemini_results = process_user_text_using_gemini_batch(grammar_candidates)

        for i, (idx, corrected) in enumerate(zip(grammar_indexes, correct_suggestion_local_model)):
            gemini_data = gemini_results[i] if i < len(gemini_results) else {}

            suggestions = []
            if corrected:
                suggestions.append(corrected)
            for suggestion in gemini_data.get("candidateSuggestions", []):
                if suggestion and suggestion not in suggestions:
                    suggestions.append(suggestion)

            final_result[idx]["candidateSuggestions"] = suggestions
            final_result[idx]["errorDescriptionEnglish"] = gemini_data.get("errorDescriptionEnglish", "No errors detected")
            final_result[idx]["errorDescriptionAfaanOromo"] = gemini_data.get("errorDescriptionAfaanOromo", "Dogoggorri hin jiru")

    # ✅ Capitalize sentences safely
    for item in final_result:
        if item.get("originalSentence"):
            item["originalSentence"] = item["originalSentence"].capitalize()

        if item.get("candidateSuggestions"):
            item["candidateSuggestions"] = [
                s.capitalize() if isinstance(s, str) else s
                for s in item["candidateSuggestions"]
            ]

    return final_result

def autocomplete_suggestions(query: str):
    return autocomplete_engine.suggest(query)


# Utility function (kept for reuse elsewhere)
def capitalize_sentences(sentences):
    return [s.capitalize() for s in sentences if isinstance(s, str)]

@lru_cache(maxsize=1)
def _get_gemini_model():
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")

    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel(settings.GEMINI_MODEL)


def _parse_gemini_batch_response(raw_text: str, expected_count: int):
    try:
        data = json.loads(raw_text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    return [
        {
            "candidateSuggestions": [],
            "errorDescriptionEnglish": "No errors detected",
            "errorDescriptionAfaanOromo": "Dogoggorri hin jiru",
        }
        for _ in range(expected_count)
    ]



def _parse_gemini_response(raw_text: str):
    suggestions = []
    error_en = ""
    error_om = ""

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    section = None

    for line in lines:
        if line.lower().startswith("candidate suggestions"):
            section = "suggestions"
            continue
        if line.lower().startswith("error description (english)"):
            section = "error_en"
            continue
        if line.lower().startswith("error description (afaan oromo)"):
            section = "error_om"
            continue

        if section == "suggestions":
            if line[0].isdigit() and "." in line:
                _, suggestion = line.split(".", 1)
                suggestion = suggestion.strip()
                if suggestion:
                    suggestions.append(suggestion)
            else:
                suggestions.append(line)
        elif section == "error_en":
            error_en = f"{error_en} {line}".strip()
        elif section == "error_om":
            error_om = f"{error_om} {line}".strip()

    return {
        "candidateSuggestions": suggestions,
        "errorDescriptionEnglish": error_en,
        "errorDescriptionAfaanOromo": error_om,
        "raw": raw_text,
    }


def process_user_text_using_gemini_batch(sentences: list[str]):
    CATEGORIES = [
        "subject–adjective-agreement-errors",
        "subject–verb-agreement-errors",
        "word-order-errors",
        "adverb–verb-agreement-errors",
        "subject–adverb-agreement-errors"
    ]

    prompt = f"""
You are an Afaan Oromo language expert.

Check each sentence for grammar and punctuation errors.
Return ALL reasonable corrected versions for each sentence.

For each sentence, classify the error into one of the following categories:
{CATEGORIES}

Respond with ONLY valid JSON array (no extra text).
Each item must contain:
- sentenceIndex (number)
- candidateSuggestions (array of strings)
- errorDescriptionEnglish (string, one of the above categories or 'No errors detected')
- errorDescriptionAfaanOromo (string)

If a sentence is correct, return the original sentence as the only candidate suggestion and 'No errors detected' for errorDescriptionEnglish.
Use 'Dogoggorri hin jiru' for descriptions.

Input:
{json.dumps([{"sentenceIndex": i, "text": s} for i, s in enumerate(sentences)], ensure_ascii=False)}
"""

    try:
        model = _get_gemini_model()
        response = model.generate_content(prompt)
        raw_text = response.text if hasattr(response, "text") else str(response)
        return _parse_gemini_batch_response(raw_text, len(sentences))
    except Exception:
        # Return only errorDescriptionEnglish and errorDescriptionAfaanOromo for error category
        error_type = "Unknown error type"
        return [
            {
                "candidateSuggestions": [],
                "errorDescriptionEnglish": error_type,
                "errorDescriptionAfaanOromo": error_type,
            }
            for _ in range(len(sentences))
        ]

# def process_user_text_using_gemini(text: str):
    prompt = f"""You are an Afaan Oromo language expert.

Analyze the following Afaan Oromo text for:
- grammatical errors
- spelling errors
- punctuation errors

There may be MORE THAN ONE valid correction.
Provide all reasonable corrected versions.

Respond using ONLY the format below.
Do NOT add explanations outside this format.

Candidate Suggestions:
1. <corrected Afaan Oromo text>
2. <corrected Afaan Oromo text>
(If only one correction exists, provide only one.)

Error Description (English):
<brief explanation of the error(s)>

Error Description (Afaan Oromo):
<short explanation in Afaan Oromo>

Text: {text}
"""

    model = _get_gemini_model()
    response = model.generate_content(prompt)
    raw_text = response.text if hasattr(response, "text") else str(response)
    return _parse_gemini_response(raw_text)

CATEGORIES = [
    "subject–adjective-agreement-errors",
    "subject–verb-agreement-errors",
    "word-order-errors",
    "adverb–verb-agreement-errors",
    "subject–adverb-agreement-errors"
]

def process_user_text_using_gemini(text: str):

    prompt = f"""
Analyze the following sentence and identify the grammatical error.

Instead of giving a description, classify the error into one of the following categories:

{CATEGORIES}

Return the response in the SAME format as before, but replace the description field
with the category name.

Sentence:
{text}
"""

    try:
        model = _get_gemini_model()
        response = model.generate_content(prompt)
        print("Gemini raw response:\n", response)  # Debug print
        raw_text = response.text if hasattr(response, "text") else str(response)
        return _parse_gemini_response(raw_text)
    except Exception:
        return {
            "candidateSuggestions": [],
            "errorDescriptionEnglish": "Internal Server Error. Please try again later",
            "errorDescriptionAfaanOromo": "Internal Server Error. Please try again later",
            "raw": ""
        }
