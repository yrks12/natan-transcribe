import streamlit as st
from pathlib import Path
import time
import os

from app.audio_processor import extract_audio, validate_audio_file
from app.transcriber import WhisperTranscriber
from app.srt_generator import SRTGenerator
from utils.file_handler import save_uploaded_file, cleanup_file, get_file_info
from config.settings import SUPPORTED_FORMATS, STREAMLIT_MAX_UPLOAD_SIZE, WHISPER_MODEL

# Page configuration
st.set_page_config(
    page_title="Natan Transcribe - Audio/Video to SRT",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if "transcription_result" not in st.session_state:
    st.session_state.transcription_result = None
if "srt_content" not in st.session_state:
    st.session_state.srt_content = None
if "processing" not in st.session_state:
    st.session_state.processing = False


def main():
    # Header
    st.title("🎬 Natan Transcribe")
    st.markdown("### Convert Audio/Video to SRT Subtitles using MLX-Whisper")
    st.markdown(f"*Optimized for Apple Silicon (M1/M2) • Max file size: {STREAMLIT_MAX_UPLOAD_SIZE}MB*")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        model_options = {
            "mlx-community/whisper-large-v3-turbo": "Large-v3-turbo (809M) - Fast & Accurate (Recommended)",
            "mlx-community/whisper-tiny": "Tiny (39M) - Fastest",
            "mlx-community/whisper-small": "Small (244M) - Balanced",
            "mlx-community/whisper-medium": "Medium (769M) - Better accuracy",
            "mlx-community/whisper-large-v3": "Large-v3 (1.5B) - Best accuracy"
        }
        
        selected_model = st.selectbox(
            "Whisper Model",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=0  # Default to turbo
        )
        
        # Timestamp mode
        timestamp_mode = st.radio(
            "Timestamp Mode",
            options=["sentence", "word"],
            format_func=lambda x: "Sentence-level" if x == "sentence" else "Word-level",
            help="Sentence-level creates more readable subtitles, Word-level provides more precise timing"
        )
        
        st.divider()
        st.markdown("### About")
        st.markdown("""
        This app uses **mlx-whisper**, an optimized implementation 
        of OpenAI's Whisper for Apple Silicon.
        
        **Supported formats:**
        - Video: MP4, AVI, MOV, MKV, WebM
        - Audio: MP3, WAV, M4A, FLAC, AAC, OGG
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose an audio or video file",
            type=SUPPORTED_FORMATS,
            help=f"Maximum file size: {STREAMLIT_MAX_UPLOAD_SIZE}MB"
        )
        
        if uploaded_file is not None:
            # Display file info
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"File size: {file_size_mb:.2f} MB")
            
            # Process button
            if st.button("🚀 Start Transcription", type="primary", disabled=st.session_state.processing):
                st.session_state.processing = True
                
                # Progress container
                progress_container = st.container()
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Step 1: Save uploaded file
                        status_text.text("Saving uploaded file...")
                        progress_bar.progress(10)
                        input_path = save_uploaded_file(uploaded_file)
                        
                        if not input_path:
                            st.error("Failed to save uploaded file")
                            st.session_state.processing = False
                            return
                        
                        # Step 2: Extract audio
                        status_text.text("Extracting audio...")
                        progress_bar.progress(20)
                        audio_path = extract_audio(input_path, lambda msg: status_text.text(msg))
                        
                        if not audio_path:
                            st.error("Failed to extract audio")
                            cleanup_file(input_path)
                            st.session_state.processing = False
                            return
                        
                        # Step 3: Validate audio
                        status_text.text("Validating audio file...")
                        progress_bar.progress(30)
                        is_valid, message = validate_audio_file(audio_path)
                        
                        if not is_valid:
                            st.error(f"Audio validation failed: {message}")
                            cleanup_file(input_path)
                            cleanup_file(audio_path)
                            st.session_state.processing = False
                            return
                        
                        st.info(message)
                        
                        # Step 4: Initialize transcriber
                        status_text.text("Loading Whisper model...")
                        progress_bar.progress(40)
                        transcriber = WhisperTranscriber(selected_model)
                        transcriber.load_model(lambda msg: status_text.text(msg))
                        
                        # Step 5: Transcribe
                        status_text.text("Transcribing audio (this may take a while)...")
                        progress_bar.progress(60)
                        
                        result = transcriber.transcribe(
                            audio_path, 
                            mode=timestamp_mode,
                            progress_callback=lambda msg: status_text.text(msg)
                        )
                        
                        if not result:
                            st.error("Transcription failed")
                            cleanup_file(input_path)
                            cleanup_file(audio_path)
                            st.session_state.processing = False
                            return
                        
                        # Step 6: Generate SRT
                        status_text.text("Generating SRT file...")
                        progress_bar.progress(80)
                        
                        segments = transcriber.extract_segments(result, mode=timestamp_mode)
                        srt_gen = SRTGenerator()
                        srt_content = srt_gen.generate_srt(segments, mode=timestamp_mode)
                        
                        # Step 7: Validate SRT
                        if not srt_gen.validate_srt(srt_content):
                            st.error("Generated SRT validation failed")
                            cleanup_file(input_path)
                            cleanup_file(audio_path)
                            st.session_state.processing = False
                            return
                        
                        # Store results in session state
                        st.session_state.transcription_result = result
                        st.session_state.srt_content = srt_content
                        
                        # Cleanup
                        cleanup_file(input_path)
                        cleanup_file(audio_path)
                        
                        # Complete
                        progress_bar.progress(100)
                        status_text.text("✅ Transcription complete!")
                        time.sleep(1)
                        
                        st.success("Transcription completed successfully!")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                    finally:
                        st.session_state.processing = False
    
    with col2:
        st.header("📝 Results")
        
        if st.session_state.srt_content:
            # Display transcription
            if st.session_state.transcription_result:
                full_text = st.session_state.transcription_result.get("text", "")
                if full_text:
                    with st.expander("View Full Transcription"):
                        st.text_area("Transcribed Text", full_text, height=200)
            
            # Display SRT preview
            st.subheader("SRT Preview")
            srt_preview = st.text_area(
                "SRT Content", 
                st.session_state.srt_content, 
                height=400,
                help="This is the generated SRT file content"
            )
            
            # Download button
            st.download_button(
                label="⬇️ Download SRT File",
                data=st.session_state.srt_content,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.srt" if uploaded_file else "subtitles.srt",
                mime="text/plain",
                type="primary"
            )
            
            # Statistics
            if st.session_state.srt_content:
                lines = st.session_state.srt_content.strip().split('\n')
                subtitle_count = len([l for l in lines if l.strip().isdigit()])
                st.metric("Total Subtitles", subtitle_count)
        else:
            st.info("Upload a file and click 'Start Transcription' to generate subtitles")


if __name__ == "__main__":
    main()