from fastapi import APIRouter, HTTPException, Depends, status, Query, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, async_get_db
from app.schemas.discussion import DiscussionPostSchema, MessagePostSchema
from app.middleware.auth import get_current_user
from app.services.discussion import DiscussionService
from app.services.message import MessageService
from app.services.doc import DocService
from app.db.models.message import MessageRoleEnum
from app import ai
from app.utils.doc_loader import doc_loader
from app.utils.doc_splitter import doc_splitter
from app.chroma.query import ingest_documents, query_user_documents
from app.repositories.discussion_repo import DiscussionRepository
from app.db.models import User
import tempfile
import shutil
import math
import os


discussion_router = APIRouter(
    prefix="/discussion",
    tags=["Discussion"],
)


#
def discussion_srv():
    return DiscussionService(DiscussionRepository())


# discussion_service = DiscussionService(DiscussionRepository())
message_service = MessageService()
doc_service = DocService()


@discussion_router.post("/", status_code=status.HTTP_201_CREATED)
def create_discussion(
    payload: DiscussionPostSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    discussion_service=discussion_srv(),
):

    if payload.doc_id:
        doc = doc_service.get_single_doc_detail(payload.doc_id, db=db)

        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not founded"
            )

        if not doc.is_embedded_generated:
            # document loader
            get_doc_id_path = doc.doc_link.split("/")[-1]

            docs = doc_loader(get_doc_id_path)
            # document splitter
            splitter = doc_splitter(docs)

            # save in vector DB
            ingest_documents(
                user_id=str(user.id),
                document_id=str(payload.doc_id),
                langchain_docs=splitter,
            )

            # update document status that is is_embedded_generated = true
            doc_service.update_doc_status(payload.doc_id, db)

    discussion = discussion_service.create_discussion(payload, user, db)
    # if discussion so also need to store a system message in messages table

    return {"success": True, "data": discussion}


@discussion_router.get("/", status_code=status.HTTP_200_OK)
async def all_discussions(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    type: str | None = Query(None),
    db: AsyncSession = Depends(async_get_db),
    user: User = Depends(get_current_user),
    discussion_service=discussion_srv(),
):
    try:
        discussion_list, count = await discussion_service.get_all_discussions(
            user.id, offset=offset, limit=limit, search=search, type=type, db=db
        )
        data = {
            "data": discussion_list,
            "total_count": count,
            "total_pages": math.ceil(count / limit),
        }
        return {"success": True, "result": data}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Some things goes wrong"
        )


@discussion_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_discussion(
    id: str,
    db: AsyncSession = Depends(async_get_db),
    user: User = Depends(get_current_user),
    discussion_service=discussion_srv(),
):
    try:
        result = await discussion_service.delete_discussion(db, id, user.id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some things goes wrong, while deleting discussion",
            )

        await db.commit()

        return {"success": True, "message": "Discussion has been deleted successfully"}
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some things goes wrong, while deleting discussion",
        )


@discussion_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_single_discussion_with_detail(
    id: str,
    db: AsyncSession = Depends(async_get_db),
    user: User = Depends(get_current_user),
    discussion_service=discussion_srv(),
):
    discussion = await discussion_service.get_single_discussion_with_detail(
        db, id, user.id
    )
    return {"success": True, "data": discussion}


# Discussion chat related
@discussion_router.post("/message")
def discussion_chat_create(
    payload: MessagePostSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    discussion_service=discussion_srv(),
):
    payload_json = payload.model_dump()

    # getting discussion from DB
    discussion = discussion_service.get_discussion_detail_only(
        payload_json["discussion_id"], user, db
    )

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Discussion detail not found!"
        )

    # first look is there any document involved
    rag_document_detail = None
    if discussion.doc_id:
        rag_document_detail = query_user_documents(
            user_id=str(user.id),
            document_ids=[str(discussion.doc_id)],
            query=payload_json["content"],
        )
    # save user message first
    payload_json["role"] = MessageRoleEnum.user
    payload_json["token_count"] = ai.get_tokenizer_count(payload_json["content"])

    pre_message_status = message_service.create_message(payload_json, db)

    if not pre_message_status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # get Latest 5 recants messages
    old_messages = message_service.get_latests_messages(
        payload_json["discussion_id"], db
    )

    # response from ai
    response = ai.chat_model_response(
        discussion.title,
        payload_json["content"],
        old_messages,
        rag_document_detail=rag_document_detail,
    )
    # save assistant message second
    payload_json["role"] = MessageRoleEnum.assistant
    payload_json["content"] = response.content
    payload_json["token_count"] = ai.get_tokenizer_count(response.content)

    pre_message_status = message_service.create_message(payload_json, db)

    if not pre_message_status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return {"success": True, "data": response.content}


@discussion_router.post("/stream/message")
async def discussion_stream_chat_create(
    payload: MessagePostSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    discussion_service=discussion_srv(),
):
    payload_json = payload.model_dump()

    discussion = discussion_service.get_discussion_detail_only(
        payload_json["discussion_id"], user, db
    )

    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion detail not found!",
        )

    # 🔹 RAG
    rag_document_detail = None
    if discussion.doc_id:
        rag_document_detail = query_user_documents(
            user_id=str(user.id),
            document_ids=[str(discussion.doc_id)],
            query=payload_json["content"],
        )

    # 🔹 Save USER message first
    payload_json["role"] = MessageRoleEnum.user
    payload_json["token_count"] = ai.get_tokenizer_count(payload_json["content"])

    if not message_service.create_message(payload_json, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    old_messages = message_service.get_latests_messages(
        payload_json["discussion_id"], db
    )

    async def stream_and_save():
        full_response = ""

        async for chunk in ai.chat_model_response_stream(
            discussion.title,
            payload_json["content"],
            old_messages,
            rag_document_detail,
        ):
            full_response += chunk
            yield chunk

        # 🔹 Save ASSISTANT message after streaming ends
        assistant_payload = payload_json.copy()
        assistant_payload["role"] = MessageRoleEnum.assistant
        assistant_payload["content"] = full_response
        assistant_payload["token_count"] = ai.get_tokenizer_count(full_response)

        message_service.create_message(assistant_payload, db)

    return StreamingResponse(
        stream_and_save(),
        media_type="text/plain",
    )


# @discussion_router.get("/{id}/message/summary/", status_code=status.HTTP_201_CREATED)
# def discussion_messages_summary(
#     id: str, db: Session = Depends(get_db), user=Depends(get_current_user)
# ):
#     # get all is_summarized messages which false
#     not_summarized_messages = message_service.get_all_not_summarized_messages(id, db)

#     if not_summarized_messages and len(not_summarized_messages) >= 10:
#         # preparing the message for summary
#         prepare_summary_chunk = ai.summary_chunk(not_summarized_messages)
#         # generate the summary per chunk
#         # getting discussion from DB
#         discussion = discussion_service.get_discussion(id, user, db)

#         for prep in prepare_summary_chunk:
#             print("prep", prep["content"])
#             summary = ai.chat_model_summary_response(discussion.title, prep["content"])
#             if summary:
#                 summary_count = ai.get_tokenizer_count(summary.content)
#                 # update ids that is_summarized true
#                 save_status = message_service.messages_status_is_summarized(
#                     prep["ids"], db
#                 )
#                 # store that summary
#                 discussion_service.save_discussion_summary(
#                     {
#                         "discussion_id": id,
#                         "content": summary.content,
#                         "token_count": summary_count,
#                     },
#                     db,
#                 )

#         return {"success": True, "message": "Summary successfully done"}
#     else:
#         return {
#             "success": True,
#             "message": "Length of the messages is less than the required",
#         }


@discussion_router.get(
    "/{id}/message/single/summary", status_code=status.HTTP_201_CREATED
)
def discussion_messages_summary(
    id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    discussion_service=discussion_srv(),
):
    # Note: add the transaction as will in here
    # get all is_summarized messages which false
    not_summarized_messages = message_service.get_all_not_summarized_messages(id, db)

    if not_summarized_messages and len(not_summarized_messages) >= 8:
        # getting discussion from DB
        discussion = discussion_service.get_discussion(id, user, db)
        # preparing the message for summary
        prepare_summary_chunk = ai.summary_chunk_single(
            not_summarized_messages, discussion.summary, discussion.summary_token_count
        )
        # generate the summary per chunk

        if prepare_summary_chunk:
            summary = ai.chat_model_summary_response(
                discussion.title, prepare_summary_chunk["content"]
            )
            if summary:
                summary_count = ai.get_tokenizer_count(summary.content)
                # update ids that is_summarized true
                message_service.messages_status_is_summarized(
                    prepare_summary_chunk["ids"], db
                )
                # store that summary
                discussion_service.save_summary(
                    {
                        "discussion_id": id,
                        "content": summary.content,
                        "token_count": summary_count,
                    },
                    db,
                )
                # this is for each summary as a record latter on user can see how many summaries is generated so far
                discussion_service.save_discussion_summary(
                    {
                        "discussion_id": id,
                        "content": summary.content,
                        "token_count": summary_count,
                    },
                    db,
                )

        return {"success": True, "message": "Summary successfully done"}
    else:
        return {
            "success": False,
            "message": "Length of the messages is less than the required",
        }


@discussion_router.get("/{id}/summary-list", status_code=status.HTTP_200_OK)
def discussion_summary_list(
    id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    discussion_service=discussion_srv(),
):
    discussion_summary_list = discussion_service.list_of_summaries(id, db)
    return {
        "success": True,
        "data": discussion_summary_list,
    }


@discussion_router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(), user: User = Depends(get_current_user)
):
    print("file", file)

    # if not file.filename.endswith((".webm", ".mp3", ".wav", ".m4a")):
    #     raise HTTPException(status_code=400, detail="Invalid audio format")

    ALLOWED_TYPES = [
        "audio/webm",
        "audio/mpeg",
        "audio/wav",
        "audio/x-wav",
        "audio/ogg",
    ]

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Please upload a valid audio file.",
        )

    # We still use a temp file because the 'pipeline' needs a stable path/buffer
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        # STEP 1: Transcribe using Hugging Face
        text = ai.aiVoiceToText.transcribe(tmp_path)

        return {
            "success": True,
            "data": text,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
