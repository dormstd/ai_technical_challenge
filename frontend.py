#!/usr/bin/env python3
"""
Frontend launcher for GenAI RAG Chatbot.
Run this file to start the Gradio web interface.

Usage:
    uv run frontend.py
    
The Gradio app will be available at http://localhost:7860
Make sure the FastAPI backend is running at http://localhost:8000
"""
import sys
from app.frontend.gradio_app import create_gradio_app


def main():
    """Launch the Gradio frontend."""
    print("\n" + "="*60)
    print("🚀 GenAI RAG Chatbot - Gradio Frontend")
    print("="*60)
    print("\n📝 The Gradio interface is starting...\n")
    print("   🌐 Frontend will be available at: http://localhost:7860")
    print("   📡 Backend API expected at:      http://localhost:8000")
    print("\n⚠️  Make sure your FastAPI backend is running!")
    print("   Start it with: uv run main.py\n")
    print("="*60 + "\n")
    
    try:
        demo = create_gradio_app()
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            show_error=True,
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Gradio frontend...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting frontend: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
