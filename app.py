from flask import Flask, jsonify, request
from checkText import process_user_text, generate_text, checkText
from TextChecker import TextChecker
import SentenceSplitter
import SpellingChecker
import Tokenizer

# from checkAndGenerateText import checkAndGenerateUserText

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

import torch
import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained('t5-base')
# model = T5ForConditionalGeneration.from_pretrained('AOGEC_Model_Output_1')
model = T5ForConditionalGeneration.from_pretrained('AOGEC_Model_Output_2')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.eval()
model.to(device)

print("Torch device:", device)
print("Model device:", next(model.parameters()).device)

sentence_splitter = SentenceSplitter.SentenceSplitter()
word_tokenizer = Tokenizer.Tokenizer()
spellChecker = SpellingChecker.SpellingChecker()

def checkAndCorrectGrammaticalError(eachSentence):
    if not eachSentence:
        return "Input text is empty."

    input_sentence = eachSentence
    max_length = 128

    # input_ids = tokenizer.encode(input_sentence, 
                                 # max_length=128, 
                                 # truncation=True, 
                                 # padding='max_length', 
                                 # return_tensors="pt"
                                 # ).to(device)

    # outputs = model.generate(input_ids=input_ids, 
    #                          decoder_start_token_id=model.config.pad_token_id,
    #                          max_length=max_length, 
    #                          num_beams=5)
    
    input_ids = tokenizer.encode(input_sentence,
                                 truncation=True,
                                 max_length=max_length, 
                                 return_tensors="pt"
                                 ).to(device)
    
    outputs = model.generate(input_ids=input_ids,
                             decoder_start_token_id=model.config.pad_token_id,
                             max_length=max_length
                            )
    
    predicted_sentence = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return predicted_sentence

@app.route('/api/test')
def testBackend():
    return jsonify({"message": "Hello! This is test from the backend!"})

@app.route('/api/check-user-text', methods=['POST']) 
def process_user_text_request():
    print("Requesting")
    data = request.get_json() 
    text = data.get('userInputText')
    print(text)

    if text == "" or text is None:
        return jsonify({
        'status' : "failed",
        'data' : {},
        "msg": 'No Text to Process!',
        }), 400  
    
    # print(checkText(text))
    formattedText = "grammar: " + text
    response = checkAndCorrectGrammaticalError(formattedText)  

    return jsonify({
        'status' : "success",
        'data' : {
            'inputText': text,
            'predictedText': response,
            # 'userTextErrorMapping' : [0, 0, 0, 0, 2, 0, 0],
        },
        'msg': 'Text Processed Successfully!',
        }), 200

@app.route('/api/process-user-text', methods=['GET', 'POST'])
def process():
    data = request.get_json()
    text = data.get('userInputText')

    finalResult = []  

    if text:
        sentences = sentence_splitter.split(text)

        for i, sentence in enumerate(sentences):
            print(f"Processing sentence {i}: {sentence}")
            if not sentence.strip():
                continue

            # Tokenize and spell check
            tokenList, tokenList_for_whitespace = word_tokenizer.tokenizer(sentence)
            correctionDict = spellChecker.spellCheck(tokenList)
            print("Correction dict:", correctionDict)

            # Prepare result object for this sentence
            sentence_result = {
                "sentenceIndex": i,
                "originalSentence": sentence,
                "spellingCorrections": {},
                "correctedSentence": ""
            }

            # If spelling errors found → record them and skip grammar correction 
            # Otherwise perform grammar correction
            if correctionDict:
                sentence_result["spellingCorrections"] = correctionDict
            else:
                correctedGrammar = checkAndCorrectGrammaticalError(sentence)
                sentence_result["correctedSentence"] = correctedGrammar

            finalResult.append(sentence_result)

        return jsonify({
            "status": "success",
            "data": finalResult,
            "msg": "Text Processed Successfully!"
        }), 200

    return jsonify({
        "status": "failed",
        "data": {},
        "msg": "No Text to Process!"
    }), 400

if __name__ == '__main__':
    port = 5001
    print("Listening for incoming connections on port ",  port) 
    # print(generate_text("grammar: Toltuun deemte mana barumsaa .")) 
    app.run(debug=True, port=port)