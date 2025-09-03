"""
Home page for the Graduation Attendance System
"""
import streamlit as st
# Clock moved to navigation bar - no longer needed here

def render_home():
    """Render the home page"""
    
    # Track page visits for navigation state management
    import streamlit as st
    if "last_visited_page" not in st.session_state:
        st.session_state.last_visited_page = None
    
    st.session_state.last_visited_page = "Home"
    # Hero Section - Momento Branding
    st.markdown("""
    <div style="
        text-align: center; 
        padding: 4rem 0 5rem 0;
        max-width: 800px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    ">
        <h1 style="font-size: 4.5rem; font-weight: 300; margin-bottom: 0.5rem; background: linear-gradient(135deg, #2D3436 0%, #636E72 50%, #4A5557 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: -0.02em; font-family: -apple-system, 'SF Pro Display', sans-serif; text-align: center; line-height: 1;">&nbsp;Momento</h1>
        <div style="
            width: 60px; 
            height: 2px; 
            background: linear-gradient(90deg, #74B9FF, #0984E3); 
            margin: 1.5rem auto; 
            border-radius: 2px;
        "></div>
        <p style="
            font-size: 1.4rem; 
            color: #636E72; 
            margin-bottom: 0; 
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            text-align: center;
        ">
            Smart Graduation Recognition
        </p>
        <p style="
            font-size: 1.2rem; 
            color: #A4A6A8; 
            margin-top: 0.75rem;
            font-weight: 400;
            text-align: center;
        ">
            AI-powered attendance management system
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards - Balanced Design
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="
            text-align: center; 
            height: 320px; 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between;
            padding: 2.5rem 2rem;
        ">
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="
                    width: 80px; 
                    height: 80px; 
                    background: linear-gradient(135deg, #E5E5E5, #F8F8F8); 
                    border-radius: 20px; 
                    margin: 0 auto 1.5rem auto; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-size: 2rem;
                    box-shadow: 0 4px 16px rgba(26, 26, 26, 0.08);
                    color: #1A1A1A;
                    border: 2px solid #E5E5E5;
                ">👤</div>
                <h3 style="margin-bottom: 0.75rem; color: #2D3436; font-weight: 600; font-size: 1.25rem;">Student Registration</h3>
                <p style="color: #2D3436; font-size: 0.95rem; line-height: 1.5; margin: 0; height: 60px; display: flex; align-items: center; justify-content: center;">Register students with AI-powered face recognition and automated processing</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 1.5rem 0 0.5rem 0;'></div>", unsafe_allow_html=True)
        if st.button("Start Registration", key="reg_btn", type="primary", use_container_width=True):
            st.session_state["selected_page"] = "Registration"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="
            text-align: center; 
            height: 320px; 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between;
            padding: 2.5rem 2rem;
        ">
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="
                    width: 80px; 
                    height: 80px; 
                    background: linear-gradient(135deg, #E5E5E5, #F8F8F8); 
                    border-radius: 20px; 
                    margin: 0 auto 1.5rem auto; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-size: 2rem;
                    box-shadow: 0 4px 16px rgba(26, 26, 26, 0.08);
                    color: #1A1A1A;
                    border: 2px solid #E5E5E5;
                ">📱</div>
                <h3 style="margin-bottom: 0.75rem; color: #2D3436; font-weight: 600; font-size: 1.25rem;">QR Management</h3>
                <p style="color: #2D3436; font-size: 0.95rem; line-height: 1.5; margin: 0; height: 60px; display: flex; align-items: center; justify-content: center;">Generate and customize QR codes with advanced styling options</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 1.5rem 0 0.5rem 0;'></div>", unsafe_allow_html=True)
        if st.button("Manage QR Codes", key="qr_btn", type="primary", use_container_width=True):
            st.session_state["selected_page"] = "QR Management"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="
            text-align: center; 
            height: 320px; 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between;
            padding: 2.5rem 2rem;
        ">
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <div style="
                    width: 80px; 
                    height: 80px; 
                    background: linear-gradient(135deg, #E5E5E5, #F8F8F8); 
                    border-radius: 20px; 
                    margin: 0 auto 1.5rem auto; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-size: 2rem;
                    box-shadow: 0 4px 16px rgba(26, 26, 26, 0.08);
                    color: #1A1A1A;
                    border: 2px solid #E5E5E5;
                ">✓</div>
                <h3 style="margin-bottom: 0.75rem; color: #2D3436; font-weight: 600; font-size: 1.25rem;">Live Attendance</h3>
                <p style="color: #2D3436; font-size: 0.95rem; line-height: 1.5; margin: 0; height: 60px; display: flex; align-items: center; justify-content: center;">Real-time attendance tracking during ceremony with instant verification</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 1.5rem 0 0.5rem 0;'></div>", unsafe_allow_html=True)
        if st.button("Track Attendance", key="att_btn", type="primary", use_container_width=True):
            st.session_state["selected_page"] = "Attendance"
            st.rerun()
    
    
