import torch
from app.dl.model import tokenizer, model, device

def check_and_correct(sentence: str, max_length=128) -> str:
    if not sentence:
        return "Input text is empty."
    input_ids = tokenizer.encode(
        sentence,
        truncation=True,
        max_length=max_length,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids=input_ids,
            decoder_start_token_id=model.config.pad_token_id,
            max_length=max_length
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def batch_correction(sentences: list, batch_size=8, max_length=128):
    results = []
    for i in range(0, len(sentences), batch_size):
        batch = ["grammar: " + s for s in sentences[i:i + batch_size]]

        inputs = tokenizer(
            batch,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length
            )

        results.extend(tokenizer.batch_decode(outputs, skip_special_tokens=True))
    return results
