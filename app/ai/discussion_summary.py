from .tokenizer import get_tokenizer_count


def summary_chunk(not_summarized_messages):
    MAX_CHUNK_TOKENS = 7000

    chunks = []
    current_chunk_text = ""
    current_chunk_ids = []
    current_chunk_tokens = 0

    for msg in not_summarized_messages:

        # get token count (cached if already in DB)
        token_count = msg.token_count or get_tokenizer_count(msg.content)

        # if adding this message exceeds limit → start new chunk
        if current_chunk_tokens + token_count > MAX_CHUNK_TOKENS:
            # store the finished chunk
            chunks.append({"ids": current_chunk_ids, "content": current_chunk_text})

            # reset for next chunk
            current_chunk_text = msg.content
            current_chunk_ids = [msg.id]
            current_chunk_tokens = token_count
        else:
            # add message content
            current_chunk_text += msg.content
            current_chunk_ids.append(msg.id)
            current_chunk_tokens += token_count

    # append last chunk
    if current_chunk_text:
        chunks.append({"ids": current_chunk_ids, "content": current_chunk_text})

    return chunks


def summary_chunk_single(not_summarized_messages, old_summary, old_summary_token_count):
    MAX_CHUNK_TOKENS = 7000

    chunks = []
    current_chunk_text = ""
    current_chunk_ids = []
    current_chunk_tokens = 0

    print("old_summary", old_summary)
    print("old_summary_token_count", old_summary_token_count)

    if old_summary:
        current_chunk_text = old_summary
        current_chunk_tokens = old_summary_token_count or get_tokenizer_count(
            old_summary
        )

    for msg in not_summarized_messages:

        # get token count (cached if already in DB)
        token_count = msg.token_count or get_tokenizer_count(msg.content)

        # if adding this message exceeds limit → start new chunk
        if current_chunk_tokens + token_count > MAX_CHUNK_TOKENS:
            # make the loop false
            break
        else:
            # add message content
            current_chunk_text += msg.content
            current_chunk_ids.append(msg.id)
            current_chunk_tokens += token_count

    return {"ids": current_chunk_ids, "content": current_chunk_text}
