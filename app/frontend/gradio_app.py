"""
Gradio interface for GenAI RAG Chatbot.
Provides a user-friendly web UI to interact with the search API endpoint.
"""
import httpx
import gradio as gr
from typing import Optional
import loguru

# Configuration
API_BASE_URL = "http://localhost:8000"
SEARCH_ENDPOINT = f"{API_BASE_URL}/api/v1/search"


async def search_rag(
    query: str,
    similarity_top_k: int,
    use_sub_questions: bool,
) -> tuple[str, str, str]:
    """
    Send a search query to the RAG backend and return the results.
    
    Args:
        query: The search query
        similarity_top_k: Number of top similar results to return
        use_sub_questions: Whether to use SubQuestionQueryEngine
        
    Returns:
        Tuple of (answer, processing_time, results_summary)
    """
    if not query.strip():
        return "❌ Please enter a question.", "0.00s", ""
    
    try:
        loguru.logger.info(f"Sending query to RAG API: {query}")
        
        payload = {
            "query": query,
            "similarity_top_k": similarity_top_k,
            "use_sub_questions": use_sub_questions,
        }
        
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                SEARCH_ENDPOINT,
                json=payload,
            )
            response.raise_for_status()
            
        data = response.json()
        answer = data.get("answer", "No answer received")
        processing_time = data.get("processing_time_seconds", 0)
        results = data.get("results", [])
        
        # Format processing time
        time_str = f"{processing_time:.2f}s"
        
        # Format results summary
        if results:
            results_summary = f"📄 Found {len(results)} source document(s):\n\n"
            for i, result in enumerate(results, 1):
                content = result.get("summary", "")[:200]  # First 200 chars
                score = result.get("score")
                if score:
                    results_summary += f"{i}. [Score: {score:.2f}] {content}...\n"
                else:
                    results_summary += f"{i}. {content}...\n"
        else:
            results_summary = "ℹ️ No source documents found for this query."
        
        loguru.logger.info(f"Successfully retrieved answer in {time_str}")
        return answer, time_str, results_summary
        
    except httpx.ConnectError:
        error_msg = f"❌ Connection error: Cannot reach API at {API_BASE_URL}. Make sure the FastAPI backend is running."
        loguru.logger.error(error_msg)
        return error_msg, "N/A", ""
    except httpx.TimeoutException:
        error_msg = "❌ Request timeout: The query took too long to process. Please try a simpler question."
        loguru.logger.error(error_msg)
        return error_msg, "N/A", ""
    except httpx.HTTPStatusError as e:
        error_detail = e.response.json().get("detail", str(e))
        error_msg = f"❌ API Error: {error_detail}"
        loguru.logger.error(f"HTTP {e.response.status_code}: {error_msg}")
        return error_msg, "N/A", ""
    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        loguru.logger.error(error_msg)
        return error_msg, "N/A", ""


def create_gradio_app() -> gr.Blocks:
    """
    Create and return the Gradio interface for the RAG chatbot.
    
    Returns:
        gr.Blocks: The Gradio interface
    """
    with gr.Blocks(
        title="Airline policies RAG Chatbot Assistant",
        theme=gr.themes.Soft(),
    ) as demo:
        
        # Header
        gr.Markdown(
            """
            # 🤖 Airline policies RAG Chatbot Assistant
            
            Ask questions about airline policies and get AI-powered answers backed by documents.
            """
        )
        
        # Question input at the top
        query_input = gr.Textbox(
            placeholder="e.g., What is the baggage allowance policy?",
            label="📝 Your Question",
            lines=3,
        )
        
        # Advanced settings in accordion
        with gr.Accordion("⚙️ Advanced Settings", open=False):
            similarity_slider = gr.Slider(
                minimum=1,
                maximum=50,
                value=10,
                step=1,
                label="Number of similar documents to retrieve",
                info="Higher values retrieve more documents"
            )
            
            use_sub_questions_check = gr.Checkbox(
                value=True,
                label="Use advanced query decomposition",
                info="Break down complex questions into simpler sub-questions"
            )
        
        # Buttons
        with gr.Row():
            submit_btn = gr.Button("🔍 Search", variant="primary", size="lg")
            clear_btn = gr.Button("🗑️ Clear", size="lg")
        
        # Answer section - full width
        gr.Markdown("# Answer")
        answer_output = gr.Markdown(
            value="",
        )
        
        # Response time and sources in collapsible accordion
        with gr.Accordion("📊 Response Details", open=False):
            with gr.Row():
                time_output = gr.Textbox(
                    label="⏱️ Processing Time",
                    interactive=False,
                    scale=1,
                )
            
            gr.Markdown("## 📚 Source Documents")
            results_output = gr.Textbox(
                label="Source Information",
                lines=12,
                interactive=False,
            )
        
        # Add info box
        gr.Markdown(
            """
            ---
            ### ℹ️ Tips
            - Ask specific questions for better results
            - Use advanced decomposition for complex multi-part questions
            - Adjust the number of documents to retrieve if you get too many or too few results
            """
        )
        
        # Event handlers
        def clear_all():
            """Clear all inputs and outputs."""
            return "", 10, False, "", "", ""
        
        submit_btn.click(
            fn=search_rag,
            inputs=[query_input, similarity_slider, use_sub_questions_check],
            outputs=[answer_output, time_output, results_output],
        )
        
        clear_btn.click(
            fn=clear_all,
            outputs=[
                query_input,
                similarity_slider,
                use_sub_questions_check,
                answer_output,
                time_output,
                results_output,
            ],
        )
        
        # Allow Enter key to submit
        query_input.submit(
            fn=search_rag,
            inputs=[query_input, similarity_slider, use_sub_questions_check],
            outputs=[answer_output, time_output, results_output],
        )
    
    return demo


if __name__ == "__main__":
    demo = create_gradio_app()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
    )
