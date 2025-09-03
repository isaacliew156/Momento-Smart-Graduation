import requests
import base64
import streamlit as st
from io import BytesIO
import time

# Try to import optional TTS dependencies
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    # Silently disable offline TTS - no warning needed

def text_to_speech_google(text, lang='en'):
    """
    Generate speech using Google Translate TTS API
    Args:
        text (str): Text to convert to speech
        lang (str): Language code (default: 'en')
    Returns:
        bytes or None: Audio content in MP3 format
    """
    try:
        # URL encode the text for API call
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl={lang}&client=tw-ob"
        
        # Make request with timeout
        response = requests.get(tts_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200 and len(response.content) > 1000:  # Valid audio file
            return response.content
        else:
            print(f"⚠️ Google TTS failed: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Google TTS Error: {str(e)}")
        return None

def text_to_speech_offline(text):
    """
    Generate speech using offline pyttsx3 engine
    Args:
        text (str): Text to convert to speech
    Returns:
        bytes or None: Audio content
    """
    if not PYTTSX3_AVAILABLE:
        return None
        
    try:
        engine = pyttsx3.init()
        
        # Configure engine properties
        engine.setProperty('rate', 150)    # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        # Try to set voice to English
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        
        # Create temporary file for audio
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Generate audio file
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        
        # Read audio content
        if os.path.exists(temp_path):
            with open(temp_path, 'rb') as f:
                audio_content = f.read()
            # Clean up
            os.unlink(temp_path)
            return audio_content
        
        return None
        
    except Exception as e:
        print(f"❌ Offline TTS Error: {str(e)}")
        return None

def enhanced_text_to_speech(text, lang='en', prefer_offline=False):
    """
    Enhanced TTS with multiple fallback methods
    Args:
        text (str): Text to convert to speech
        lang (str): Language code for Google TTS
        prefer_offline (bool): Whether to prefer offline TTS first
    Returns:
        tuple: (audio_content, method_used)
    """
    if prefer_offline and PYTTSX3_AVAILABLE:
        # Try offline first
        audio_content = text_to_speech_offline(text)
        if audio_content:
            return audio_content, 'offline'
        
        # Fallback to Google
        audio_content = text_to_speech_google(text, lang)
        if audio_content:
            return audio_content, 'google'
    else:
        # Try Google first
        audio_content = text_to_speech_google(text, lang)
        if audio_content:
            return audio_content, 'google'
        
        # Fallback to offline
        if PYTTSX3_AVAILABLE:
            audio_content = text_to_speech_offline(text)
            if audio_content:
                return audio_content, 'offline'
    
    # All methods failed
    return None, 'browser'

def play_audio_content(audio_content, autoplay=True):
    """
    Play audio content in Streamlit using HTML audio element
    Args:
        audio_content (bytes): Audio content to play
        autoplay (bool): Whether to autoplay the audio
    """
    if audio_content:
        try:
            # Encode audio to base64
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            # Create HTML audio element
            autoplay_attr = 'autoplay' if autoplay else ''
            audio_html = f'''
            <audio {autoplay_attr} controls style="width: 100%;">
                <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
                <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
            '''
            
            # Display audio player
            st.markdown(audio_html, unsafe_allow_html=True)
            return True
            
        except Exception as e:
            st.error(f"❌ Audio playback error: {str(e)}")
            return False
    return False

def play_browser_tts(text):
    """
    Fallback method using browser Web Speech API
    Args:
        text (str): Text to speak using browser TTS
    """
    try:
        # JavaScript code for browser TTS
        browser_tts_js = f'''
        <script>
        function speakText() {{
            if ('speechSynthesis' in window) {{
                const msg = new SpeechSynthesisUtterance("{text}");
                msg.rate = 1.0;
                msg.pitch = 1.0;
                msg.volume = 1.0;
                msg.lang = 'en-US';
                window.speechSynthesis.speak(msg);
            }} else {{
                console.log('Speech synthesis not supported');
            }}
        }}
        // Auto-trigger speech
        speakText();
        </script>
        '''
        
        st.markdown(browser_tts_js, unsafe_allow_html=True)
        return True
        
    except Exception as e:
        print(f"❌ Browser TTS Error: {str(e)}")
        return False

def announce_student_attendance(student_name, language='en', custom_message=None, auto_mode=False):
    """
    Announce student attendance with visual and audio feedback
    Args:
        student_name (str): Name of the student to announce
        language (str): Language for TTS
        custom_message (str): Custom announcement message (optional)
        auto_mode (bool): Whether to provide auto-mode specific feedback
    Returns:
        dict: Announcement result with status and estimated duration
    """
    try:
        # Prepare announcement text
        if custom_message:
            announcement_text = custom_message.format(name=student_name)
        else:
            announcement_text = student_name  # Just announce the name
        
        # Create visual announcement
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #f8f9ff;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
            animation: pulse 2s infinite;
        ">
            <h2 style="margin: 0; font-size: 1.8em; color: #e8ecff;">🔊 ANNOUNCEMENT</h2>
            <h1 style="margin: 20px 0; font-size: 2.5em; font-weight: bold; color: #ffffff;">
                {student_name}
            </h1>
        </div>
        
        <style>
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}
        </style>
        ''', unsafe_allow_html=True)
        
        # Generate and play audio
        with st.spinner("🔊 Generating announcement audio..."):
            audio_content, method = enhanced_text_to_speech(announcement_text, language)
            
            # Estimate audio duration (rough calculation)
            estimated_duration = len(announcement_text.split()) * 0.6  # ~0.6 seconds per word
            
            if audio_content:
                # Play audio
                play_audio_content(audio_content, autoplay=True)
                if auto_mode:
                    st.success(f"✅ Announcement played using {method.upper()} TTS (est. {estimated_duration:.1f}s)")
                    st.info(f"🤖 Auto mode will activate after audio completes...")
                else:
                    st.success(f"✅ Announcement played using {method.upper()} TTS")
                    
                return {
                    'success': True,
                    'method': method,
                    'duration': estimated_duration,
                    'text': announcement_text
                }
            else:
                # Fallback to browser TTS
                st.info("🔄 Using browser TTS as fallback...")
                play_browser_tts(announcement_text)
                if auto_mode:
                    st.success(f"✅ Announcement played using BROWSER TTS (est. {estimated_duration:.1f}s)")
                    st.info(f"🤖 Auto mode will activate after audio completes...")
                else:
                    st.success("✅ Announcement played using BROWSER TTS")
                    
                return {
                    'success': True,
                    'method': 'browser',
                    'duration': estimated_duration,
                    'text': announcement_text
                }
                
    except Exception as e:
        st.error(f"❌ Announcement failed: {str(e)}")
        return {
            'success': False,
            'method': 'none',
            'duration': 0,
            'error': str(e)
        }

def test_tts_methods():
    """
    Test all available TTS methods and display capabilities
    Returns:
        dict: Status of each TTS method
    """
    test_text = "Testing text to speech functionality"
    results = {
        'google': False,
        'offline': False,
        'browser': True  # Always available in browsers
    }
    
    # Test Google TTS
    try:
        google_audio = text_to_speech_google(test_text)
        results['google'] = google_audio is not None
    except:
        results['google'] = False
    
    # Test Offline TTS
    if PYTTSX3_AVAILABLE:
        try:
            offline_audio = text_to_speech_offline(test_text)
            results['offline'] = offline_audio is not None
        except:
            results['offline'] = False
    else:
        results['offline'] = False
    
    return results

def create_tts_settings_ui():
    """
    Create Streamlit UI for TTS settings configuration
    Returns:
        dict: TTS configuration settings
    """
    st.markdown("### 🔊 TTS Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Test TTS methods
        if st.button("🧪 Test TTS Methods", help="Check which TTS methods are available"):
            with st.spinner("Testing TTS capabilities..."):
                results = test_tts_methods()
                
                st.markdown("**Available TTS Methods:**")
                for method, available in results.items():
                    status = "✅" if available else "❌"
                    st.write(f"{status} {method.upper()} TTS")
    
    with col2:
        # TTS preferences
        prefer_offline = st.checkbox(
            "Prefer Offline TTS", 
            help="Use offline TTS when available (faster, no internet required)"
        )
        
        language = st.selectbox(
            "Language", 
            ["en", "ms", "zh"],
            index=0,
            help="Language for Google TTS"
        )
    
    # Custom message template
    custom_message = st.text_input(
        "Custom Announcement Template",
        value="{name}, please proceed to the stage",
        help="Use {name} as placeholder for student name"
    )
    
    return {
        'prefer_offline': prefer_offline,
        'language': language,
        'custom_message': custom_message if custom_message else None
    }