"""
Simple Beautiful Clock for Homepage
Clean, elegant real-time clock display
"""

import streamlit as st
from streamlit.components.v1 import html
import time
from datetime import datetime

def get_greeting_info():
    """Get time-based greeting and day info"""
    now = datetime.now()
    hour = now.hour
    current_time = now.strftime("%H:%M")
    weekday = now.strftime("%A")
    
    # Time-based greetings with more variety
    if 5 <= hour < 8:
        greeting = "🌅 Rise & shine"
        vibe = "Early bird"
    elif 8 <= hour < 12:
        greeting = "☀️ Good morning"
        vibe = "Fresh start"
    elif 12 <= hour < 14:
        greeting = "🍽️ Lunch time"
        vibe = "Midday"
    elif 14 <= hour < 17:
        greeting = "☀️ Afternoon"
        vibe = "Productive"
    elif 17 <= hour < 19:
        greeting = "🌆 Evening"
        vibe = "Golden hour"
    elif 19 <= hour < 22:
        greeting = "🌙 Good evening"
        vibe = "Wind down"
    else:  # 22-5
        greeting = "🌙 Night owl"
        vibe = "Late night"
    
    return {
        'greeting': greeting,
        'vibe': vibe,
        'time': current_time,
        'weekday': weekday
    }

def render_nav_clock():
    """Render a smart greeting clock with time-based messages"""
    
    # Get greeting info
    info = get_greeting_info()
    
    # Balanced design with proper spacing and alignment
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 0.3rem;">
        <div style="display: inline-block; background: rgba(245, 246, 250, 0.9); border: 1px solid rgba(223, 230, 233, 0.8); border-radius: 8px; padding: 0.4rem 1rem; font-family: -apple-system, system-ui, sans-serif; box-shadow: 0 1px 4px rgba(45, 52, 54, 0.06); line-height: 1.2;">
            <span style="font-size: 0.85rem; font-weight: 500; color: #636E72;">{info['greeting']}</span>
            <span style="font-size: 1.1rem; font-weight: 500; color: #636E72; padding: 0 10px;">{info['time']}</span>
            <span style="font-size: 0.75rem; color: #A4A6A8; font-weight: 500;">• {info['weekday']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_live_clock_page():
    """Render a dedicated live clock page with real-time updates"""
    
    st.title("🕐 Live Clock")
    
    # Create placeholder for live updates
    clock_placeholder = st.empty()
    
    # Real-time clock loop (only for dedicated clock page)
    import threading
    import time
    
    def update_clock():
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%A, %B %d, %Y")
            
            clock_placeholder.markdown(f"""
            <div style="text-align: center; margin: 2rem 0;">
                <div style="font-size: 4rem; font-weight: 300; color: #2D3436; margin-bottom: 1rem; font-family: -apple-system, system-ui, sans-serif;">
                    {current_time}
                </div>
                <div style="font-size: 1.2rem; color: #636E72;">
                    {current_date}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(1)
    
    # Start clock in background thread
    if 'clock_running' not in st.session_state:
        st.session_state.clock_running = True
        threading.Thread(target=update_clock, daemon=True).start()

def render_compact_clock():
    """Render a compact version of the clock for smaller spaces"""
    
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%b %d")
    
    compact_html = f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 12px;
        background: rgba(45, 52, 54, 0.9);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 8px 16px;
        color: white;
        font-family: -apple-system, 'SF Pro Display', system-ui, sans-serif;
        font-size: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 10px 0;
    ">
        <div style="
            font-size: 18px;
            font-weight: 600;
            font-variant-numeric: tabular-nums;
        ">
            {current_time}
        </div>
        <div style="
            width: 1px;
            height: 16px;
            background: rgba(255, 255, 255, 0.3);
        "></div>
        <div style="
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
        ">
            {current_date}
        </div>
        <div style="
            width: 4px;
            height: 4px;
            background: #00E676;
            border-radius: 50%;
            animation: pulse 2s infinite;
        "></div>
    </div>
    
    <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
    </style>
    """
    
    st.markdown(compact_html, unsafe_allow_html=True)

# Auto-refresh function for real-time updates (no longer needed - JavaScript handles it)
def auto_refresh_clock():
    """No-op function - clock updates via JavaScript now"""
    pass