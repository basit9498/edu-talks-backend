from transformers import AutoTokenizer



# def get_tokenizer_count(content:str):
#     tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B",token="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")
#     return len(tokenizer.encode(content))

tokenizer = AutoTokenizer.from_pretrained("gpt2")



def get_tokenizer_count(content:str):
    return len(tokenizer.encode(content))