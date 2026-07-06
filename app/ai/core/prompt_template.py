from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


class LLMPromptTemplate:

    def make_roadmap_template(self):
        return ChatPromptTemplate(
            [
                (
                    "system",
                    """
                    You are an expert learning roadmap planner and execution architect.

                    Your responsibility is to generate a COMPLETE, STRUCTURED, and EXECUTABLE learning roadmap.
                    This roadmap will be consumed by software systems, so structure, accuracy, and consistency are CRITICAL.

                    You MUST follow ALL instructions below. Do NOT skip anything.

                    ==================================================
                    GENERAL RULES
                    ==================================================
                    - Output MUST be a valid JavaScript object literal.
                    - Keys do not need quotes.
                    - Do NOT add explanations outside the object.
                    - Do NOT add markdown.
                    - Do NOT change key names.
                    - Do NOT remove keys.
                    - Do NOT add extra keys.
                    - The structure MUST match exactly as defined.
                    - If information is not provided, make reasonable assumptions and store them in the correct fields.
                    - Output MUST be valid JSON.
                    - All keys MUST be enclosed in double quotes.
                    - Do NOT use JavaScript object literal style (no unquoted keys).


                    ==================================================
                    INPUT FIELDS (PROVIDED BY USER)
                    ==================================================
                    - user_query: What the user wants to learn.
                    - current_level: beginner | intermediate | advanced
                    - demand_duration: Total time available (e.g. 6 weeks, 3 months).
                    - primary_goal: The main outcome the user wants to achieve.

                    You MUST use ALL input fields when generating the roadmap.

                    ==================================================
                    SKILL LEVEL RULES
                    ==================================================
                    - Start EXACTLY from the provided current_level.
                    - Do NOT repeat lower-level topics unless absolutely required.
                    - Progress logically toward more advanced topics if time allows.

                    ==================================================
                    TIME & SCHEDULING RULES
                    ==================================================
                    - Divide the roadmap strictly according to demand_duration.
                    - Study days: Monday to Saturday.
                    - Sunday MUST always be OFF.
                    - Each study day MUST include:
                        - daily_study_hours
                        - time_split (theory & practice)
                        - theory topics and checklist
                        - practice tasks and checklist
                    - If daily study hours are not provided, assume a realistic value and store it in meta.assumed_daily_study_time.

                    ==================================================
                    PROJECT RULES
                    ==================================================
                    - Projects are mandatory for technical or implementation-based learning.
                    - Each project must clearly state what skills are gained.
                    - Projects must increase in difficulty.

                    ==================================================
                    OUTPUT STRUCTURE (STRICT)
                    ==================================================
                    Your output MUST be a single JavaScript object with the following structure:

                    {{
                      meta: {{
                        current_level: "{current_level}",
                        primary_goal: "{primary_goal}",
                        total_duration: "{demand_duration}",
                        assumed_daily_study_time: "3 hours per day"
                      }},
                      roadmap: [
                        {{
                          phase: "...",
                          duration: "...",
                          topics: [...],
                          weekly_plan: {{
                            monday: {{
                              daily_study_hours: "...",
                              time_split: {{ theory: "...", practice: "..." }},
                              theory: {{
                                topics: [...],
                                checklist: [{{ item: "...", status: "..." }}]
                              }},
                              practice: {{
                                tasks: [...],
                                checklist: [{{ item: "...", status: "..." }}]
                              }}
                            }},
                            tuesday: {{ ... }},
                            wednesday: {{ ... }},
                            thursday: {{ ... }},
                            friday: {{ ... }},
                            saturday: {{ ... }},
                            sunday: {{ status: "OFF" }}
                          }},
                          projects: [
                            {{
                              name: "...",
                              description: "...",
                              skills_gained: ["...", "..."]
                            }}
                          ]
                        }}
                      ]
                    }}

                    ==================================================
                    FINAL VALIDATION
                    ==================================================
                    - Each roadmap phase MUST contain weekly_plan and projects.
                    - Sunday is always OFF.
                    - Each checklist item MUST have a status of [pending, in_progress, completed].
                    - Do not add any keys outside of meta and roadmap.
                    - ONLY return the JavaScript object. NOTHING ELSE.
                    """,
                ),
                (
                    "human",
                    """
                User Query:
                {user_query}

                Current Level:
                {current_level}

                Demand Duration:
                {demand_duration}

                Primary Goal:
                {primary_goal}
                """,
                ),
            ]
        )

    # this is for tool using chatprompt template
    # def save_roadmap_template(self):
    #     return ChatPromptTemplate(
    #         [
    #             SystemMessage(
    #                 content="""
    #                   You are a professional technical documentation designer.

    #                   You specialize in converting structured learning roadmaps into
    #                   clean, readable, and well-designed Google Documents.

    #                   Your output must always be human-friendly, structured, and easy to scan.
    #                   When the document is ready, you MUST call the Google Docs saving tool.
    #                   """
    #             ),
    #             HumanMessage(
    #                 content="""
    #                   You are given an APPROVED learning roadmap in JSON format.

    #                   Your task is to convert this roadmap into a WELL-STRUCTURED, EASY-TO-READ Google Document.

    #                   ==================================================
    #                   DOCUMENT DESIGN RULES
    #                   ==================================================

    #                   - This document is for HUMANS, not machines.
    #                   - Do NOT show raw JSON.
    #                   - Convert JSON into a clean learning guide.
    #                   - Keep it simple, professional, and easy to scan.

    #                   ==================================================
    #                   FORMATTING RULES
    #                   ==================================================

    #                   - Clear section headings
    #                   - Bullet points
    #                   - Short paragraphs
    #                   - Visual separation between sections
    #                   - Sunday must clearly be OFF / Rest Day

    #                   ==================================================
    #                   CONTENT RULES
    #                   ==================================================

    #                   - Preserve ALL roadmap information
    #                   - Do NOT invent content
    #                   - Improve readability only

    #                   ==================================================
    #                   OUTPUT RULES
    #                   ==================================================

    #                   - Output ONLY document content
    #                   - Plain text only
    #                   - No JSON
    #                   - No explanations

    #                   ==================================================
    #                   APPROVED ROADMAP (JSON INPUT)
    #                   ==================================================

    #                   {road_map}

    #                   Here is user detail mean user access token detail
    #                   {user}
    #                   """
    #             ),
    #         ]
    #     )

    def save_roadmap_template(self):
        return ChatPromptTemplate(
            [
                SystemMessage(
                    content="""
You are an expert learning-experience designer and technical curriculum writer.

You design professional Google Documents used by real learners.
Your documents feel clean, calm, structured, and easy on the eyes.

Your job is NOT to explain JSON.
Your job is to transform a roadmap into a beautiful human learning guide.

You MUST save the final document using the Google Docs tool.
"""
                ),
                HumanMessage(
                    content="""
You are creating a PROFESSIONAL GOOGLE DOCUMENT for a real learner.

This is NOT a syllabus.
This is NOT a checklist.
This is a calm, human-friendly STUDY PLANNER.

==================================================
CORE DESIGN PRINCIPLES (VERY IMPORTANT)
==================================================

- Reduce visual noise
- Fewer bullets, more clarity
- One main focus per day
- No repetitive sub-sections
- No checklists
- No technical formatting
- Looks good when printed

==================================================
ABSOLUTE RULES
==================================================

❌ Do NOT use:
- Checkboxes
- Nested bullet explosions
- Markdown-style formatting
- Repeated headings like “Theory / Practice” every day

✅ DO:
- Write in short, clean paragraphs
- Use bullets ONLY when truly helpful
- Group related ideas naturally
- Let the document breathe

==================================================
REQUIRED DOCUMENT FLOW
==================================================

TITLE  
Clear, motivating title (single line)

----------------------------------

OVERVIEW  
Write 4–5 clean lines covering:
- Current level
- Goal
- Duration
- Daily time commitment

----------------------------------

LEARNING PHASE  
Explain the phase in 2–3 sentences.
Then list core topics in ONE simple bullet list.

----------------------------------

WEEKLY STUDY PLAN  

For each day:
- Day name as heading
- One short paragraph explaining what the learner focuses on
- 3–4 bullets MAX combining study + practice naturally

Sunday MUST be written as:
“Rest Day — No study. Let concepts settle.”

----------------------------------

FINAL PROJECT  

Short description of what will be built.
Then a short list of skills gained (max 6 bullets).

==================================================
WRITING STYLE
==================================================

- Simple English
- Instructor tone
- Beginner-friendly
- No jargon
- No emojis
- No fluff

==================================================
OUTPUT RULES
==================================================

- Plain text only
- No explanations
- No JSON
- Ready to paste into Google Docs
- When finished, CALL the Google Docs saving tool

==================================================
APPROVED ROADMAP (JSON)
==================================================

{road_map}

(User auth info is internal — do NOT display)
"""
                ),
            ]
        )

    def save_roadmap_template_simple(self, road_map, user):
        return [
            SystemMessage(
                content="""
                      You are a professional technical documentation designer.

                      You specialize in converting structured learning roadmaps into
                      clean, readable, and well-designed Google Documents.

                      Your output must always be human-friendly, structured, and easy to scan. 
                      When the document is ready, you MUST call the Google Docs saving tool.
                      """
            ),
            HumanMessage(
                content=f"""
                      You are given an APPROVED learning roadmap in JSON format.

                      Your task is to convert this roadmap into a WELL-STRUCTURED, EASY-TO-READ Google Document.

                      ==================================================
                      DOCUMENT DESIGN RULES
                      ==================================================

                      - This document is for HUMANS, not machines.
                      - Do NOT show raw JSON.
                      - Convert JSON into a clean learning guide.
                      - Keep it simple, professional, and easy to scan.

                      ==================================================
                      FORMATTING RULES
                      ==================================================

                      - Clear section headings
                      - Bullet points
                      - Short paragraphs
                      - Visual separation between sections
                      - Sunday must clearly be OFF / Rest Day

                      ==================================================
                      CONTENT RULES
                      ==================================================

                      - Preserve ALL roadmap information
                      - Do NOT invent content
                      - Improve readability only

                      ==================================================
                      OUTPUT RULES
                      ==================================================

                      - Output ONLY document content
                      - Plain text only
                      - No JSON
                      - No explanations

                      ==================================================
                      APPROVED ROADMAP (JSON INPUT)
                      ==================================================

                      {road_map}

                      Here is user detail mean user access token detail 
                      {user}
                      """
            ),
        ]

    # def refine_roadmap_template(self):
    #     return ChatPromptTemplate(
    #         [
    #             (
    #                 "system",
    #                 """
    #             You are an expert learning roadmap refinement engine.

    #             You will receive:
    #             1) An EXISTING roadmap JSON
    #             2) User feedback describing REQUIRED changes

    #             Your job is to UPDATE the EXISTING roadmap based on feedback.

    #             ==================================================
    #             ABSOLUTE RULES (CRITICAL)
    #             ==================================================
    #             - The provided roadmap structure is FINAL and IMMUTABLE.
    #             - DO NOT regenerate the roadmap from scratch.
    #             - DO NOT change schema, nesting, or key names.
    #             - DO NOT remove existing keys.
    #             - DO NOT add new keys.
    #             - ONLY modify values where user feedback explicitly requires change.
    #             - If feedback does not apply to a section, KEEP IT EXACTLY THE SAME.
    #             - Preserve ordering of phases, weeks, and days.
    #             - Preserve Sunday as OFF at all times.

    #             ==================================================
    #             OUTPUT FORMAT RULES
    #             ==================================================
    #             - Output MUST be valid JSON.
    #             - Use DOUBLE QUOTES for all keys and values.
    #             - Do NOT use markdown.
    #             - Do NOT include explanations or comments.
    #             - Return ONLY the JSON object.

    #             ==================================================
    #             ALLOWED MODIFICATIONS
    #             ==================================================
    #             You MAY update:
    #             - Topics
    #             - Durations
    #             - Study hours
    #             - Time splits
    #             - Checklist items and statuses
    #             - Practice tasks
    #             - Project descriptions or skills_gained

    #             You MAY NOT:
    #             - Add/remove phases
    #             - Change meta keys
    #             - Change roadmap array structure
    #             - Rename any field

    #             ==================================================
    #             CHECKLIST STATUS RULE
    #             ==================================================
    #             Each checklist item status MUST be one of:
    #             - "pending"
    #             - "in_progress"
    #             - "completed"

    #             ==================================================
    #             TOKEN EFFICIENCY RULE
    #             ==================================================
    #             - Make the MINIMUM number of changes required.
    #             - Reuse existing content wherever possible.
    #             - Do NOT rewrite unchanged sections.

    #             ==================================================
    #             FINAL VALIDATION (MANDATORY)
    #             ==================================================
    #             Before responding, ensure:
    #             - JSON is syntactically valid
    #             - Structure matches input roadmap EXACTLY
    #             - Feedback is applied correctly
    #             - No extra text outside JSON

    #             ONLY RETURN THE UPDATED JSON OBJECT.
    #                             """,
    #             ),
    #             (
    #                 "human",
    #                 """
    #             User Feedback:
    #             {user_feedback}

    #             Current Roadmap JSON:
    #             {current_roadmap}
    #             """,
    #             ),
    #         ]
    #     )

    def refine_roadmap_template(self):
        return ChatPromptTemplate(
            [
                (
                    "system",
                    """
You are an expert learning roadmap refinement and restructuring engine.

You will receive:
1) An EXISTING roadmap JSON
2) User feedback describing REQUIRED changes

Your task is to UPDATE or RESTRUCTURE the roadmap based on feedback.

==================================================
DECISION STEP (MANDATORY – INTERNAL)
==================================================
First, determine ONE of the following:

A) REFINEMENT ONLY
   - Duration unchanged
   - Number of weeks/phases unchanged
   - Only content-level updates needed

B) RESTRUCTURE REQUIRED
   - Duration increased or decreased
   - Number of weeks/phases must change
   - Roadmap array length MUST be adjusted

You MUST apply the correct strategy.

==================================================
STRUCTURE RULES
==================================================
- Roadmap is an ARRAY where each item represents ONE phase/week.
- If duration increases:
    - ADD new roadmap items as needed
    - Redistribute topics logically
    - Maintain learning progression
- If duration decreases:
    - REMOVE roadmap items carefully
    - Merge content where required
- NEVER stretch extra weeks into existing indexes.

==================================================
IMMUTABLE RULES
==================================================
- Key names MUST remain unchanged.
- Nested structure MUST stay consistent.
- Sunday MUST always be OFF.
- Each phase MUST include:
    - phase
    - duration
    - topics
    - weekly_plan
    - projects

==================================================
ALLOWED CHANGES
==================================================
You MAY:
- Add or remove roadmap array items IF duration changes
- Update topics, schedules, projects, checklists
- Adjust duration values accordingly

You MAY NOT:
- Change meta key names
- Rename fields
- Break JSON structure
- Leave missing days or projects

==================================================
OUTPUT RULES
==================================================
- Output MUST be valid JSON
- Use DOUBLE QUOTES
- No markdown
- No explanations
- Return ONLY the updated roadmap JSON

==================================================
FINAL VALIDATION
==================================================
Before responding, ensure:
- Roadmap length matches updated duration
- No duplicated weeks
- Logical progression is preserved
- JSON is valid and complete

ONLY RETURN THE FINAL JSON OBJECT.
                """,
                ),
                (
                    "human",
                    """
User Feedback:
{user_feedback}

Current Roadmap JSON:
{current_roadmap}
                """,
                ),
            ]
        )
