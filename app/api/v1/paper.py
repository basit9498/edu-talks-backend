from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from app.middleware.auth import get_current_user
from app.db.session import get_db
from app.schemas.paper import PaperCreateSchema
from app.ai import llm_question_creation, llm_question_creation_v3
from app.services.paper import PaperService
from app.services.discussion import DiscussionService
from app.services.message import MessageService
from app import ai
from app.repositories.discussion_repo import DiscussionRepository


paper_router = APIRouter(
    prefix="/paper",
    tags=["Paper"],
)

paper_services = PaperService()
discussion_services = DiscussionService(DiscussionRepository())
message_service = MessageService()


@paper_router.post("/ai-create", status_code=status.HTTP_200_OK)
async def create_ai_paper(
    payload: PaperCreateSchema,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # here we need to look if there is any messages which is not summarized then first summarized that then go with paper creation

    # process of the summarization start -----------------------------------

    not_summarized_messages = message_service.get_all_not_summarized_messages(
        payload.discussion_id, db
    )

    update_summary = None
    print("--------------", not_summarized_messages)
    if not_summarized_messages and len(not_summarized_messages) >= 1:
        print("------------------coming not_summarized_messages")
        # getting discussion from DB
        discussion = discussion_services.get_discussion(payload.discussion_id, user, db)
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
                update_summary = summary.content
                summary_count = ai.get_tokenizer_count(summary.content)
                # update ids that is_summarized true
                message_service.messages_status_is_summarized(
                    prepare_summary_chunk["ids"], db
                )
                # store that summary
                discussion_services.save_summary(
                    {
                        "discussion_id": payload.discussion_id,
                        "content": summary.content,
                        "token_count": summary_count,
                    },
                    db,
                )
                # this is for each summary as a record latter on user can see how many summaries is generated so far
                discussion_services.save_discussion_summary(
                    {
                        "discussion_id": payload.discussion_id,
                        "content": summary.content,
                        "token_count": summary_count,
                    },
                    db,
                )

    # process of the summarization end.  -----------------------------------
    new_paper = paper_services.create_paper(payload, db)

    if not update_summary:
        print("------------------coming with nit update summary")
        discussion_detail = discussion_services.get_simple_discussion(
            payload.discussion_id, db
        )

        update_summary = discussion_detail.summary

    llm_question_setup = []

    for setup in new_paper.question_setup:
        llm_question_setup.append(
            {"type": setup["type"], "count": setup["number_of_questions"]}
        )

    # Paper Question Creation
    data = llm_question_creation_v3(llm_question_setup, update_summary)

    paper_services.create_paper_questions(
        payload_list=data.questions, paper_id=new_paper.id, db=db
    )

    return {"success": True, "message": "Paper Create successfully", "data": data}


@paper_router.get("/{id}/question-list", status_code=status.HTTP_200_OK)
def paper_question(
    id: str, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    paper_question_list = paper_services.paper_question_list(id, db)
    return {
        "success": True,
        "message": "Paper Question List",
        "data": paper_question_list,
    }
