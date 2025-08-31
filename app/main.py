import streamlit as st
from pathlib import Path
import time
import os

from audio_processor import extract_audio, validate_audio_file
from realtime_transcriber import RealtimeTranscriber
from srt_generator import SRTGenerator
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.file_handler import save_uploaded_file, cleanup_file, get_file_info
from config.settings import SUPPORTED_FORMATS, STREAMLIT_MAX_UPLOAD_SIZE, WHISPER_MODEL

# Page configuration
st.set_page_config(
    page_title="נתן תמלול - המרת אודיו/וידאו ל-SRT",
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
if "transcribed_words" not in st.session_state:
    st.session_state.transcribed_words = []
if "current_segment" not in st.session_state:
    st.session_state.current_segment = ""


def main():
    # Header
    st.title("🎬 נתן תמלול")
    st.markdown("### המרת אודיו/וידאו לכתוביות SRT באמצעות MLX-Whisper")
    st.markdown("*מותאם עבור Apple Silicon (M1/M2) • ללא הגבלת גודל קובץ*")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ הגדרות")
        
        # Model selection
        model_options = {
            "mlx-community/whisper-large-v3-turbo": "Large-v3-turbo (809M) - מהיר ומדויק (מומלץ)",
            "mlx-community/whisper-tiny": "Tiny (39M) - הכי מהיר",
            "mlx-community/whisper-small": "Small (244M) - מאוזן",
            "mlx-community/whisper-medium": "Medium (769M) - דיוק טוב יותר",
            "mlx-community/whisper-large-v3": "Large-v3 (1.5B) - דיוק מקסימלי"
        }
        
        selected_model = st.selectbox(
            "מודל Whisper",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=0  # Default to turbo
        )
        
        # Timestamp mode
        timestamp_mode = st.radio(
            "מצב חותמות זמן",
            options=["sentence", "word", "word_precise"],
            format_func=lambda x: {"sentence": "ברמת משפט", "word": "ברמת מילה (קבוצות)", "word_precise": "ברמת מילה (מדויק)"}[x],
            help="ברמת משפט: כתוביות קריאות | ברמת מילה (קבוצות): מילים בקבוצות קטנות | ברמת מילה (מדויק): מילה אחת בכל כתובית"
        )
        
        st.divider()
        st.markdown("### אודות")
        st.markdown("""
        אפליקציה זו משתמשת ב-**mlx-whisper**, מימוש מותאם 
        של Whisper של OpenAI עבור Apple Silicon.
        
        **פורמטים נתמכים:**
        - וידאו: MP4, AVI, MOV, MKV, WebM
        - אודיו: MP3, WAV, M4A, FLAC, AAC, OGG
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 העלאת קובץ")
        
        uploaded_file = st.file_uploader(
            "בחר קובץ אודיו או וידאו",
            type=SUPPORTED_FORMATS,
            help="תומך בכל גדלי קבצים - עיבוד מקומי ללא הגבלות"
        )
        
        if uploaded_file is not None:
            # Display file info
            st.success(f"✅ קובץ הועלה: {uploaded_file.name}")
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"גודל הקובץ: {file_size_mb:.2f} MB")
            
            # Process button
            if st.button("🚀 התחל תמלול", type="primary", disabled=st.session_state.processing):
                st.session_state.processing = True
                st.session_state.transcribed_words = []
                st.session_state.current_segment = ""
                
                # Progress container
                progress_container = st.container()
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Step 1: Save uploaded file
                        status_text.text("שמירת הקובץ...")
                        progress_bar.progress(10)
                        input_path = save_uploaded_file(uploaded_file)
                        
                        if not input_path:
                            st.error("שגיאה בשמירת הקובץ")
                            st.session_state.processing = False
                            return
                        
                        # Step 2: Extract audio
                        status_text.text("חילוץ אודיו...")
                        progress_bar.progress(20)
                        audio_path = extract_audio(input_path, lambda msg: status_text.text(msg))
                        
                        if not audio_path:
                            st.error("שגיאה בחילוץ האודיו")
                            cleanup_file(input_path)
                            st.session_state.processing = False
                            return
                        
                        # Step 3: Validate audio
                        status_text.text("בדיקת תקינות האודיו...")
                        progress_bar.progress(30)
                        is_valid, message = validate_audio_file(audio_path)
                        
                        if not is_valid:
                            st.error(f"בדיקת האודיו נכשלה: {message}")
                            cleanup_file(input_path)
                            cleanup_file(audio_path)
                            st.session_state.processing = False
                            return
                        
                        st.info(message)
                        
                        # Step 4: Initialize transcriber
                        status_text.text("טעינת מודל Whisper...")
                        progress_bar.progress(40)
                        transcriber = RealtimeTranscriber(selected_model)
                        transcriber.load_model(lambda msg: status_text.text(msg))
                        
                        # Step 5: Transcribe with real-time updates
                        status_text.text("מתחיל תמלול (זה עלול לקחת זמן)...")
                        progress_bar.progress(60)
                        
                        # Create placeholders for real-time updates
                        if col2:
                            with col2:
                                realtime_placeholder = st.empty()
                                with realtime_placeholder.container():
                                    st.subheader("🎤 תמלול בזמן אמת")
                                    current_segment_placeholder = st.empty()
                                    words_placeholder = st.empty()
                        
                        def realtime_update(word, segment_info):
                            """Update real-time display"""
                            st.session_state.transcribed_words.append(word)
                            st.session_state.current_segment = segment_info
                            
                            # Update display
                            current_segment_placeholder.markdown(f"**מגמנט נוכחי:** *{segment_info}*")
                            words_text = " ".join(st.session_state.transcribed_words[-30:])  # Show last 30 words
                            words_placeholder.text_area("מילים שתומללו:", words_text, height=150, disabled=True, key=f"words_{len(st.session_state.transcribed_words)}")
                        
                        result = transcriber.transcribe_with_updates(
                            audio_path, 
                            mode=timestamp_mode,
                            progress_callback=lambda msg: status_text.text(msg),
                            realtime_callback=realtime_update
                        )
                        
                        if not result:
                            st.error("התמלול נכשל")
                            cleanup_file(input_path)
                            cleanup_file(audio_path)
                            st.session_state.processing = False
                            return
                        
                        # Step 6: Generate SRT
                        status_text.text("יוצר קובץ SRT...")
                        progress_bar.progress(80)
                        
                        segments = transcriber.extract_segments(result, mode=timestamp_mode)
                        srt_gen = SRTGenerator()
                        srt_content = srt_gen.generate_srt(segments, mode=timestamp_mode)
                        
                        # Step 7: Validate SRT
                        if not srt_gen.validate_srt(srt_content):
                            st.error("אימות קובץ ה-SRT נכשל")
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
                        status_text.text("✅ התמלול הושלם!")
                        time.sleep(1)
                        
                        st.success("התמלול הושלם בהצלחה!")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"אירעה שגיאה: {str(e)}")
                    finally:
                        st.session_state.processing = False
    
    with col2:
        st.header("📝 תוצאות")
        
        # Real-time transcription display
        if st.session_state.processing:
            st.subheader("🎤 תמלול בזמן אמת")
            realtime_container = st.container()
            with realtime_container:
                if st.session_state.current_segment:
                    st.write("**מגמנט נוכחי:**")
                    st.markdown(f"*{st.session_state.current_segment}*")
                
                if st.session_state.transcribed_words:
                    st.write("**מילים שתומללו:**")
                    words_text = " ".join(st.session_state.transcribed_words[-50:])  # Show last 50 words
                    st.text_area("", words_text, height=200, disabled=True)
        
        if st.session_state.srt_content:
            # Display transcription
            if st.session_state.transcription_result:
                full_text = st.session_state.transcription_result.get("text", "")
                if full_text:
                    with st.expander("צפה בתמלול המלא"):
                        st.text_area("טקסט מתומלל", full_text, height=200)
            
            # Display SRT preview
            st.subheader("תצוגה מקדימה של SRT")
            srt_preview = st.text_area(
                "תוכן SRT", 
                st.session_state.srt_content, 
                height=400,
                help="זהו תוכן קובץ ה-SRT שנוצר"
            )
            
            # Download button
            st.download_button(
                label="⬇️ הורד קובץ SRT",
                data=st.session_state.srt_content,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.srt" if uploaded_file else "subtitles.srt",
                mime="text/plain",
                type="primary"
            )
            
            # Statistics
            if st.session_state.srt_content:
                lines = st.session_state.srt_content.strip().split('\n')
                subtitle_count = len([l for l in lines if l.strip().isdigit()])
                st.metric("סך הכל כתוביות", subtitle_count)
        else:
            st.info("העלה קובץ ולחץ על 'התחל תמלול' כדי ליצור כתוביות")


if __name__ == "__main__":
    main()