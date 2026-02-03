from nlp import SentenceSplitter, Tokenizer, SpellingChecker, AutoComplete
from dl.inference import check_and_correct, batch_correction

# NLP Utilities (instantiate once)
sentence_splitter = SentenceSplitter.SentenceSplitter()
word_tokenizer = Tokenizer.Tokenizer()
spell_checker = SpellingChecker.SpellingChecker()
autocomplete_engine = AutoComplete.AutoComplete(
    spell_checker.wordSet,
    spell_checker.wordFreq
)

def process_text(text: str):
    sentences = sentence_splitter.split(text)
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
            "correctedSentence": ""
        }

        # collect sentences for grammar correction
        if not correction_dict and len(tokens) >= 3:
            grammar_candidates.append(sentence)
            grammar_indexes.append(len(final_result))

        final_result.append(result)

    # Grammar correction (batch)
    if grammar_candidates:
        corrected_sentences = batch_correction(grammar_candidates)

        for idx, corrected in zip(grammar_indexes, corrected_sentences):
            final_result[idx]["correctedSentence"] = corrected

    # ✅ Capitalize sentences safely
    for item in final_result:
        if item.get("originalSentence"):
            item["originalSentence"] = item["originalSentence"].capitalize()

        if item.get("correctedSentence"):
            item["correctedSentence"] = item["correctedSentence"].capitalize()

    return final_result


def autocomplete_suggestions(query: str):
    return autocomplete_engine.suggest(query)


# Utility function (kept for reuse elsewhere)
def capitalize_sentences(sentences):
    return [s.capitalize() for s in sentences if isinstance(s, str)]
