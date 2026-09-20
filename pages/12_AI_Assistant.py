import streamlit as st

from chatbot.assistant import answer_question
from chatbot.data_engine import load_tables


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# TITLE
# ============================================================

st.title("🤖 Life Insurance AI Assistant")

st.markdown(
    """
    Ask questions about your life-insurance data,
    renewal performance, premiums, insurers,
    forecasting results, business insights and
    model performance using natural language.
    """
)

st.info(
    "💡 The assistant answers using the project's available "
    "CSV data and forecasting/model outputs."
)


# ============================================================
# LOAD PROJECT DATA
# ============================================================

if "ai_database" not in st.session_state:

    with st.spinner(
        "Loading project data..."
    ):

        (
            st.session_state.ai_database,
            st.session_state.ai_tables,
        ) = load_tables()


# ============================================================
# CHAT HISTORY
# ============================================================

if "ai_messages" not in st.session_state:

    st.session_state.ai_messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I am your Life Insurance "
                "Analytics Assistant.\n\n"
                "You can ask me about insurers, premiums, "
                "renewals, forecasts, business insights "
                "or model performance."
            ),
        }
    ]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🤖 AI Assistant")

    st.caption(
        f"Loaded "
        f"{len(st.session_state.ai_tables)} "
        f"CSV dataset(s)."
    )

    st.divider()

    st.subheader("💬 Example Questions")

    example_questions = [
        "Which insurer has the highest renewed premium?",
        "What is the overall renewal rate?",
        "Compare forecasting models using MAPE.",
        "Which model has the lowest average MAPE?",
        "Explain the forecast results.",
        "Show me the premium trend by insurer.",
    ]

    for question in example_questions:

        st.write(
            f"• {question}"
        )

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.ai_messages = [
            {
                "role": "assistant",
                "content": (
                    "Chat cleared. "
                    "What would you like to know?"
                ),
            }
        ]

        st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.ai_messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

user_question = st.chat_input(
    "Ask something about your life-insurance data..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_question:

    # --------------------------------------------------------
    # Display user question
    # --------------------------------------------------------

    st.session_state.ai_messages.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with st.chat_message("user"):

        st.markdown(
            user_question
        )

    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "Analyzing your data..."
            ):

                (
                    answer,
                    sql_query,
                    result_df,
                ) = answer_question(
                    question=user_question,
                    connection=st.session_state.ai_database,
                    tables=st.session_state.ai_tables,
                    conversation_history=(
                        st.session_state.ai_messages[:-1]
                    ),
                )

            # ------------------------------------------------
            # Show answer
            # ------------------------------------------------

            st.markdown(
                answer
            )

            # ------------------------------------------------
            # Show data used
            # ------------------------------------------------

            with st.expander(
                "🔎 Show data query used"
            ):

                st.code(
                    sql_query,
                    language="sql"
                )

                if result_df.empty:

                    st.info(
                        "The query returned no rows."
                    )

                else:

                    st.dataframe(
                        result_df,
                        use_container_width=True,
                        hide_index=True,
                    ) 

            # ------------------------------------------------
            # Save assistant answer
            # ------------------------------------------------

            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception as error:

            error_message = (
                "I couldn't answer that question.\n\n"
                "Please check your Gemini API key, "
                "the project data files, and the "
                "terminal error message."
            )

            st.error(
                error_message
            )

            with st.expander(
                "Technical error"
            ):

                st.code(
                    str(error)
                )

            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )
          
