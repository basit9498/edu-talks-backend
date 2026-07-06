from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.messages import HumanMessage, AIMessage
from .structure_output import paper_question_parser
from .build_prompts import build_question_format_examples
from app.ai.core import ChatModel, MessageMapper
from typing import AsyncGenerator

# LLM initialization

llm_model = ChatModel(
    repo_id="meta-llama/Llama-3.2-3B-Instruct",
    task="text-generation",
)


# v1 without rag
# def chat_model_response(discussion_title, question, old_messages=[]):

#     messages_history = MessageMapper.to_langchain(old_messages)

#     chat_prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 """
#         You are an expert assistant engaged in a one-to-one discussion with the user, user will be asked question  regarding discussion topic and you need to provide best understanding.

#         The discussion topic is:
#         **{discussion_title}**

#         Your job:
#         - Stay strictly within the topic above.
#         - Never introduce content that is outside or irrelevant to the topic.
#         - Be clear, helpful, and structured in your responses.
#         - If the user asks something outside the topic, politely bring them back to the discussion focus.
#         - Provide easy examples that related to the topics
#         - Use the previous messages for context to understand what so far we have chat regrading the topic.


#         Follow these rules carefully.
#         """,
#             ),
#             MessagesPlaceholder(variable_name="chat_history"),
#             ("user", "{question}"),
#         ]
#     )

#     prompt_result = chat_prompt.invoke(
#         {
#             "discussion_title": discussion_title,
#             "question": question,
#             "chat_history": messages_history,
#         }
#     )

#     llm_response = llm_model.invoke(prompt_result)

#     return llm_response


def chat_model_response(
    discussion_title, question, old_messages=[], rag_document_detail: str = None
):
    messages_history = MessageMapper.to_langchain(old_messages)

    system_prompt = """
    You are an expert assistant engaged in a one-to-one discussion with the user.

    Discussion topic:
    **{discussion_title}**

    Your rules:
    - Stay strictly within the discussion topic.
    - Use previous messages for context.
    - Be clear, structured, and easy to understand.
    - Provide simple examples related to the topic.
    - If the question is outside the topic, politely bring the user back.
    """

    # 🔹 Add RAG-specific instructions ONLY if document exists
    if rag_document_detail:
        system_prompt += """

    IMPORTANT:
    You are also given reference document content below.

    Reference Document Content:
    ----------------------------
    {rag_document_detail}
    ----------------------------

    Rules for document usage:
    - Prefer answering using the document content.
    - If the answer comes from the document, explain it clearly.
    - If the document does NOT contain the answer, say:
    "This information is not available in the provided document."
    - Do NOT hallucinate or add information not present in the document.
    """

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{question}"),
        ]
    )

    prompt_result = chat_prompt.invoke(
        {
            "discussion_title": discussion_title,
            "question": question,
            "chat_history": messages_history,
            "rag_document_detail": rag_document_detail or "",
        }
    )

    llm_response = llm_model.invoke(prompt_result)

    return llm_response


async def chat_model_response_stream(
    discussion_title,
    question,
    old_messages=[],
    rag_document_detail: str = None,
) -> AsyncGenerator[str, None]:

    messages_history = MessageMapper.to_langchain(old_messages)

    system_prompt = """
    You are an expert assistant engaged in a one-to-one discussion with the user.

    Discussion topic:
    **{discussion_title}**

    Your rules:
    - Stay strictly within the discussion topic.
    - Use previous messages for context.
    - Be clear, structured, and easy to understand.
    - Provide simple examples related to the topic.
    - If the question is outside the topic, politely bring the user back.
    """

    if rag_document_detail:
        system_prompt += """
    IMPORTANT:
    You are also given reference document content below.

    Reference Document Content:
    ----------------------------
    {rag_document_detail}
    ----------------------------

    Rules for document usage:
    - Prefer answering using the document content.
    - If the answer comes from the document, explain it clearly.
    - If the document does NOT contain the answer, say:
      "This information is not available in the provided document."
    - Do NOT hallucinate.
    """

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{question}"),
        ]
    )

    prompt_result = chat_prompt.invoke(
        {
            "discussion_title": discussion_title,
            "question": question,
            "chat_history": messages_history,
            "rag_document_detail": rag_document_detail or "",
        }
    )

    # 🔴 IMPORTANT: use stream(), not invoke()
    async for chunk in llm_model.astream(prompt_result):
        yield chunk


def chat_model_summary_response(discussion_title, chunk):
    SYSTEM_PROMPT = """
    You are a senior research assistant and expert technical writer.

    Your task is to summarize a chunk of a long multi-message discussion. 
    This summary will later be used to generate full academic papers, 
    technical documentation, research reports, or well-structured study material.

    Your summary MUST follow these rules:

    1. Preserve every important idea — no skipping details.
    2. Identify & retain question / content type:
    - conceptual, technical, coding, real-world, logical, etc.
    3. Maintain all technical details (code, architecture, constraints).
    4. Capture non-technical insights when present.
    5. Use clear structure: headings, bullets, sections.
    6. Do NOT hallucinate; only use original content.
    7. Preserve intent (questions, doubts, explanations).
    8. Make it future-proof for combining with other chunks.

    Provide a detailed, structured, highly accurate summary.
    """

    USER_PROMPT = """
    Below is a chunk of discussion messages. Summarize it according to the system instructions:

    --- BEGIN CHUNK ---
    {chunk}
    --- END CHUNK ---

    Discussion Title: {discussion_title}
    """

    chat_prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("user", USER_PROMPT)]
    )

    prompt_result = chat_prompt.invoke(
        {"discussion_title": discussion_title, "chunk": chunk}
    )

    llm_response = llm_model.invoke(prompt_result)

    return llm_response


def llm_question_creation():

    question_generation_template = PromptTemplate(
        template="""
            You are an expert question paper generator.

            Generate *exactly* 5 MCQ questions strictly from the summary.

            RULES:
            - Output MUST be valid JSON.
            - Follow the JSON structure exactly.
            - DO NOT output schema, $defs, or descriptions.
            - "question_options" MUST contain keys: a, b, c, d.
            - "correct_answer" MUST be one of ["a"], ["b"], ["c"], or ["d"].
            - DO NOT add explanations.
            - Only output REAL DATA in JSON.

            OUTPUT FORMAT:
            {format_instruction}

            Summary:
            {summary}

            User Instruction:
            {user_instruction}

        
          OUTPUT FORMAT (FOLLOW EXACTLY):
            {{
            "questions": [
                {{
                "question": "string",
                "question_type": "mcqs",
                "is_fixed_answer": true,
                "question_options": {{
                    "a": "option 1",
                    "b": "option 2",
                    "c": "option 3",
                    "d": "option 4"
                }},
                "correct_answer": ["a"]
                }}
            ]
            }}

            so need format exactly for 5 questions
            """,
        input_variables=["summary", "user_instruction"],
        partial_variables={
            "format_instruction": paper_question_parser.get_format_instructions()
        },
    )

    llm = HuggingFaceEndpoint(
        repo_id="openai/gpt-oss-120b",
        task="text-generation",
        temperature=0.6,
        huggingfacehub_api_token="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",
    )

    llm_model = ChatHuggingFace(llm=llm)
    chain_model = question_generation_template | llm_model | paper_question_parser
    response = chain_model.invoke(
        {
            "summary": """
            Machine Learning (ML) is a subset of Artificial Intelligence (AI) that enables systems to learn from data, make predictions, and improve their performance over time. In other words, ML allows computers to learn from experience without being explicitly programmed.

            Key Characteristics of Machine Learning:

            Learning from data: ML systems learn from data, which can be in the form of text, images, audio, or other types of data.
            Improving performance: As the system learns from data, its performance improves over time.
            """,
            "user_instruction": "Make conceptual paper",
        }
    )

    return response


# v3
def llm_question_creation_v3(question_type_list: list, summary: str):

    # dynamic_prompt = build_dynamic_prompt(question_type_list)
    #     - short_question
    # - long_answer
    dynamic_prompt = build_question_format_examples(question_type_list)

    type_count_lines = "\n".join(
        [
            f"- Generate exactly {item['count']} questions of type '{item['type']}'."
            for item in question_type_list
        ]
    )

    question_generation_template = PromptTemplate(
        template="""
            You are an expert question paper generator.

            Generate *exactly* 5 MCQ questions strictly from the summary.

            RULES:
            - Output MUST be valid JSON.
            - Follow the JSON structure exactly.
            - DO NOT output schema, $defs, or descriptions.
            - DO NOT add explanations.
            - Only output REAL DATA in JSON.

            VALID QUESTION TYPES:
            - mcqs
            - fill_in_the_blank
        


            - Respect EXACT question counts:
            {type_count_lines}

            OUTPUT FORMAT:
            {format_instruction}

            Summary:
            {summary}

            User Instruction:
            {user_instruction}

        
          OUTPUT FORMAT (FOLLOW EXACTLY):
            {question_formats}

      
            """,
        input_variables=[
            "summary",
            "user_instruction",
            "question_formats",
            "type_count_lines",
        ],
        partial_variables={
            "format_instruction": paper_question_parser.get_format_instructions()
        },
    )

    llm = HuggingFaceEndpoint(
        repo_id="openai/gpt-oss-120b",
        task="text-generation",
        temperature=0.6,
        huggingfacehub_api_token="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",
    )

    llm_model = ChatHuggingFace(llm=llm)
    chain_model = question_generation_template | llm_model | paper_question_parser
    response = chain_model.invoke(
        {
            "summary": summary,
            "user_instruction": "Make conceptual paper",
            "question_formats": dynamic_prompt,
            "type_count_lines": type_count_lines,
        }
    )

    return response
