"""
Beautiful loading animations and progress indicators for OCR processing
Advanced visual feedback system with customizable animations
"""
import streamlit as st
import time
import json
import random
from typing import List, Dict, Optional, Callable, Any
import threading
from datetime import datetime

class OCRLoadingAnimation:
    """Advanced loading animation system for OCR processing with visual effects"""
    
    def __init__(self):
        self.animation_styles = {
            'scanning': {
                'emoji': '🔍',
                'description': 'Scanning document...',
                'progress_color': '#FF6B6B',
                'bg_color': 'linear-gradient(45deg, #FF6B6B, #4ECDC4)'
            },
            'processing': {
                'emoji': '⚙️',
                'description': 'Processing image...',
                'progress_color': '#4ECDC4',
                'bg_color': 'linear-gradient(45deg, #4ECDC4, #45B7D1)'
            },
            'extracting': {
                'emoji': '📝',
                'description': 'Extracting text...',
                'progress_color': '#45B7D1',
                'bg_color': 'linear-gradient(45deg, #45B7D1, #96CEB4)'
            },
            'analyzing': {
                'emoji': '🧠',
                'description': 'Analyzing results...',
                'progress_color': '#96CEB4',
                'bg_color': 'linear-gradient(45deg, #96CEB4, #FECA57)'
            },
            'finalizing': {
                'emoji': '✨',
                'description': 'Finalizing...',
                'progress_color': '#FECA57',
                'bg_color': 'linear-gradient(45deg, #FECA57, #FF9FF3)'
            }
        }
        
        self.fun_messages = [
            "🤖 AI is reading your card like a book...",
            "🔬 Enhancing pixels with mathematical magic...",
            "📊 Teaching machines to read Malaysian names...",
            "⚡ Applying quantum OCR algorithms...",
            "🎯 Decoding student information matrix...",
            "🔮 Using crystal-clear vision processing...",
            "🚀 Launching text recognition rockets...",
            "🌟 Sprinkling some OCR fairy dust...",
            "🔥 Burning through image noise...",
            "💎 Polishing characters to perfection..."
        ]

    def create_loading_container(self, title: str = "Processing Student Card") -> dict:
        """Create animated loading container with advanced visual effects"""
        
        # Main container with gradient background
        container = st.container()
        
        with container:
            st.markdown(f"""
            <style>
            .loading-container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 20px;
                padding: 2rem;
                margin: 1rem 0;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1), 0 5px 15px rgba(0,0,0,0.07);
                position: relative;
                overflow: hidden;
            }}
            
            .loading-container::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: shimmer 3s linear infinite;
                pointer-events: none;
            }}
            
            @keyframes shimmer {{
                0% {{ transform: translateX(-100%) translateY(-100%) rotate(30deg); }}
                100% {{ transform: translateX(100%) translateY(100%) rotate(30deg); }}
            }}
            
            .loading-title {{
                color: white;
                font-size: 1.5rem;
                font-weight: 600;
                text-align: center;
                margin-bottom: 1.5rem;
                text-shadow: 0 2px 10px rgba(0,0,0,0.3);
                animation: pulse 2s ease-in-out infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            
            .progress-stages {{
                display: flex;
                justify-content: space-between;
                margin: 1.5rem 0;
                padding: 0 1rem;
            }}
            
            .stage {{
                display: flex;
                flex-direction: column;
                align-items: center;
                color: white;
                font-size: 0.9rem;
                opacity: 0.5;
                transition: all 0.3s ease;
                position: relative;
            }}
            
            .stage.active {{
                opacity: 1;
                transform: scale(1.1);
                color: #FFD700;
            }}
            
            .stage.completed {{
                opacity: 1;
                color: #4CAF50;
            }}
            
            .stage-icon {{
                font-size: 2rem;
                margin-bottom: 0.5rem;
                animation: bounce 1s ease-in-out infinite;
            }}
            
            .stage.active .stage-icon {{
                animation: bounce 0.6s ease-in-out infinite;
            }}
            
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
            
            .fun-message {{
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 15px;
                padding: 1rem;
                margin: 1rem 0;
                color: white;
                text-align: center;
                font-style: italic;
                backdrop-filter: blur(10px);
                animation: fadeInUp 0.5s ease-out;
            }}
            
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .scanning-line {{
                width: 100%;
                height: 3px;
                background: linear-gradient(90deg, transparent, #FFD700, transparent);
                animation: scanning 2s linear infinite;
                margin: 1rem 0;
                border-radius: 2px;
            }}
            
            @keyframes scanning {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}
            
            .dots-loader {{
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 1rem 0;
            }}
            
            .dot {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #FFD700;
                margin: 0 5px;
                animation: dotBounce 1.4s ease-in-out infinite both;
            }}
            
            .dot:nth-child(1) {{ animation-delay: -0.32s; }}
            .dot:nth-child(2) {{ animation-delay: -0.16s; }}
            
            @keyframes dotBounce {{
                0%, 80%, 100% {{
                    transform: scale(0.8);
                    opacity: 0.5;
                }}
                40% {{
                    transform: scale(1.2);
                    opacity: 1;
                }}
            }}
            </style>
            
            <div class="loading-container">
                <div class="loading-title">{title}</div>
                <div id="progress-stages" class="progress-stages">
                    <!-- Stages will be populated by JavaScript -->
                </div>
                <div class="scanning-line"></div>
                <div id="fun-message" class="fun-message">
                    🚀 Initializing advanced OCR system...
                </div>
                <div class="dots-loader">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
                <div id="progress-bar-container" style="margin: 1rem 0;"></div>
            </div>
            """, unsafe_allow_html=True)
        
        # Initialize stages
        stages = ['scanning', 'processing', 'extracting', 'analyzing', 'finalizing']
        self._create_progress_stages(stages)
        
        return {
            'container': container,
            'stages': stages,
            'current_stage': 0,
            'start_time': time.time()
        }

    def _create_progress_stages(self, stages: List[str]):
        """Create visual progress stages"""
        stages_html = ""
        
        for i, stage in enumerate(stages):
            stage_info = self.animation_styles.get(stage, self.animation_styles['scanning'])
            stages_html += f"""
            <div class="stage" id="stage-{i}">
                <div class="stage-icon">{stage_info['emoji']}</div>
                <div>{stage_info['description'].replace('...', '')}</div>
            </div>
            """
        
        st.markdown(f"""
        <script>
        document.getElementById('progress-stages').innerHTML = '{stages_html.replace("'", "&apos;")}';
        </script>
        """, unsafe_allow_html=True)

    def update_stage(self, loading_info: dict, stage_index: int, message: str = None):
        """Update the current processing stage with animation"""
        
        if stage_index >= len(loading_info['stages']):
            return
        
        # Update current stage
        loading_info['current_stage'] = stage_index
        stage_name = loading_info['stages'][stage_index]
        stage_info = self.animation_styles.get(stage_name, self.animation_styles['scanning'])
        
        # Select fun message
        if not message:
            message = random.choice(self.fun_messages)
        
        # Calculate progress percentage
        progress = (stage_index + 1) / len(loading_info['stages']) * 100
        
        # Get elapsed time
        elapsed_time = time.time() - loading_info['start_time']
        
        # Update UI with JavaScript
        st.markdown(f"""
        <script>
        // Update stages
        for (let i = 0; i < {len(loading_info['stages'])}; i++) {{
            const stage = document.getElementById('stage-' + i);
            if (stage) {{
                stage.classList.remove('active', 'completed');
                if (i < {stage_index}) {{
                    stage.classList.add('completed');
                }} else if (i === {stage_index}) {{
                    stage.classList.add('active');
                }}
            }}
        }}
        
        // Update fun message
        const funMessage = document.getElementById('fun-message');
        if (funMessage) {{
            funMessage.innerHTML = "{message}";
            funMessage.style.animation = 'none';
            funMessage.offsetHeight; // Trigger reflow
            funMessage.style.animation = 'fadeInUp 0.5s ease-out';
        }}
        
        // Update progress bar
        const progressContainer = document.getElementById('progress-bar-container');
        if (progressContainer) {{
            progressContainer.innerHTML = '<div style="background: rgba(255,255,255,0.2); border-radius: 25px; height: 25px; overflow: hidden; position: relative;"><div style="background: {stage_info["bg_color"]}; height: 100%; width: {progress:.1f}%; border-radius: 25px; transition: width 0.8s ease; position: relative; overflow: hidden;"><div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); animation: progressShine 2s linear infinite;"></div></div><div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-weight: 600; font-size: 0.8rem; text-shadow: 0 1px 3px rgba(0,0,0,0.7);">{progress:.0f}% • {elapsed_time:.1f}s</div></div><style>@keyframes progressShine {{ 0% {{ transform: translateX(-100%); }} 100% {{ transform: translateX(200%); }} }}</style>';
        }}
        </script>
        """, unsafe_allow_html=True)

    def complete_loading(self, loading_info: dict, success: bool = True, final_message: str = None):
        """Complete the loading animation with success/failure state"""
        
        if success:
            if not final_message:
                final_message = "🎉 Processing completed successfully!"
            
            # Mark all stages as completed
            st.markdown("""
            <script>
            // Complete all stages
            for (let i = 0; i < 5; i++) {
                const stage = document.getElementById('stage-' + i);
                if (stage) {
                    stage.classList.remove('active');
                    stage.classList.add('completed');
                }
            }
            
            // Update to success message
            const funMessage = document.getElementById('fun-message');
            if (funMessage) {
                funMessage.innerHTML = '🎉 Processing completed successfully!';
                funMessage.style.background = 'rgba(76, 175, 80, 0.2)';
                funMessage.style.borderColor = 'rgba(76, 175, 80, 0.5)';
                funMessage.style.animation = 'none';
                funMessage.offsetHeight;
                funMessage.style.animation = 'fadeInUp 0.5s ease-out';
            }
            
            // Complete progress bar
            const progressContainer = document.getElementById('progress-bar-container');
            if (progressContainer) {
                progressContainer.innerHTML = '<div style="background: rgba(76, 175, 80, 0.3); border-radius: 25px; height: 25px; overflow: hidden; position: relative;"><div style="background: linear-gradient(45deg, #4CAF50, #8BC34A); height: 100%; width: 100%; border-radius: 25px; position: relative; overflow: hidden;"><div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent); animation: successShine 1s ease-in-out 3;"></div></div><div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-weight: 600; font-size: 0.8rem; text-shadow: 0 1px 3px rgba(0,0,0,0.7);">✅ Complete</div></div><style>@keyframes successShine { 0% { transform: translateX(-100%); } 100% { transform: translateX(200%); } }</style>';
            }
            </script>
            """, unsafe_allow_html=True)
            
        else:
            if not final_message:
                final_message = "❌ Processing failed. Please try again."
            
            st.markdown(f"""
            <script>
            // Update to error message
            const funMessage = document.getElementById('fun-message');
            if (funMessage) {{
                funMessage.innerHTML = "{final_message}";
                funMessage.style.background = 'rgba(244, 67, 54, 0.2)';
                funMessage.style.borderColor = 'rgba(244, 67, 54, 0.5)';
                funMessage.style.animation = 'none';
                funMessage.offsetHeight;
                funMessage.style.animation = 'fadeInUp 0.5s ease-out';
            }}
            
            // Error progress bar
            const progressContainer = document.getElementById('progress-bar-container');
            if (progressContainer) {{
                progressContainer.innerHTML = '<div style="background: rgba(244, 67, 54, 0.3); border-radius: 25px; height: 25px; overflow: hidden; position: relative;"><div style="background: linear-gradient(45deg, #F44336, #FF5722); height: 100%; width: 100%; border-radius: 25px; animation: errorPulse 1s ease-in-out 3;"></div><div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-weight: 600; font-size: 0.8rem; text-shadow: 0 1px 3px rgba(0,0,0,0.7);">❌ Error</div></div><style>@keyframes errorPulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}</style>';
            }}
            </script>
            """, unsafe_allow_html=True)

    def create_step_by_step_loader(self, steps: List[Dict[str, str]], title: str = "Processing..."):
        """Create step-by-step loader with detailed progress"""
        
        st.markdown(f"""
        <style>
        .step-loader {{
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            position: relative;
        }}
        
        .step-loader-title {{
            color: white;
            font-size: 1.8rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        
        .step-item {{
            display: flex;
            align-items: center;
            margin: 1rem 0;
            padding: 1rem;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            opacity: 0.6;
        }}
        
        .step-item.active {{
            opacity: 1;
            transform: translateX(10px);
            background: rgba(255,255,255,0.2);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .step-item.completed {{
            opacity: 1;
            background: rgba(76, 175, 80, 0.2);
            border-color: rgba(76, 175, 80, 0.5);
        }}
        
        .step-icon {{
            font-size: 1.5rem;
            margin-right: 1rem;
            width: 40px;
            text-align: center;
        }}
        
        .step-content {{
            flex: 1;
            color: white;
        }}
        
        .step-title {{
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}
        
        .step-description {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .step-spinner {{
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 1rem;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        
        <div class="step-loader">
            <div class="step-loader-title">{title}</div>
            <div id="step-container">
                <!-- Steps will be populated -->
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Populate steps
        steps_html = ""
        for i, step in enumerate(steps):
            steps_html += f"""
            <div class="step-item" id="step-{i}">
                <div class="step-icon">{step.get('icon', '⚙️')}</div>
                <div class="step-content">
                    <div class="step-title">{step.get('title', 'Processing...')}</div>
                    <div class="step-description">{step.get('description', '')}</div>
                </div>
                <div id="step-spinner-{i}" class="step-spinner" style="display: none;"></div>
            </div>
            """
        
        st.markdown(f"""
        <script>
        document.getElementById('step-container').innerHTML = '{steps_html.replace("'", "&apos;")}';
        </script>
        """, unsafe_allow_html=True)
        
        return {'steps': steps, 'current_step': -1}

    def update_step(self, loader_info: dict, step_index: int, status: str = 'active'):
        """Update step status ('active', 'completed', 'error')"""
        
        if step_index >= len(loader_info['steps']):
            return
        
        # Update previous steps to completed
        for i in range(step_index):
            st.markdown(f"""
            <script>
            const prevStep = document.getElementById('step-{i}');
            if (prevStep) {{
                prevStep.classList.remove('active');
                prevStep.classList.add('completed');
                const spinner = document.getElementById('step-spinner-{i}');
                if (spinner) spinner.style.display = 'none';
            }}
            </script>
            """, unsafe_allow_html=True)
        
        # Update current step
        if status == 'active':
            st.markdown(f"""
            <script>
            const currentStep = document.getElementById('step-{step_index}');
            if (currentStep) {{
                currentStep.classList.add('active');
                const spinner = document.getElementById('step-spinner-{step_index}');
                if (spinner) spinner.style.display = 'block';
            }}
            </script>
            """, unsafe_allow_html=True)
        elif status == 'completed':
            st.markdown(f"""
            <script>
            const currentStep = document.getElementById('step-{step_index}');
            if (currentStep) {{
                currentStep.classList.remove('active');
                currentStep.classList.add('completed');
                const spinner = document.getElementById('step-spinner-{step_index}');
                if (spinner) spinner.style.display = 'none';
            }}
            </script>
            """, unsafe_allow_html=True)
        
        loader_info['current_step'] = step_index

# Global instance
ocr_loader = OCRLoadingAnimation()

def show_ocr_processing_animation(processing_function: Callable, *args, **kwargs):
    """
    Wrapper function to show OCR processing with beautiful animations
    
    Args:
        processing_function: Function to execute during animation
        *args, **kwargs: Arguments to pass to the processing function
    
    Returns:
        Result of the processing function
    """
    import streamlit as st
    
    # Show a simple progress message instead of complex animation for streamlit compatibility
    with st.spinner("🤖 AI-Powered OCR Processing..."):
        # Show processing steps as info messages
        st.info("📷 Preprocessing image for optimal OCR...")
        result = processing_function(*args, **kwargs)
        
        if result.get('success'):
            st.success("🎉 Text extraction completed successfully!")
        else:
            st.warning("⚠️ Processing completed with issues")
    
    return result

def create_simple_spinner(message: str = "Processing..."):
    """Create a simple but elegant spinner for quick operations"""
    
    st.markdown(f"""
    <div style="
        display: flex; 
        align-items: center; 
        justify-content: center; 
        padding: 2rem;
        background: linear-gradient(45deg, #4a90e2, #7b68ee);
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    ">
        <div style="
            width: 30px; 
            height: 30px; 
            border: 3px solid rgba(255,255,255,0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 1rem;
        "></div>
        <div style="font-weight: 600; font-size: 1.1rem;">{message}</div>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)