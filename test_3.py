import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Vertical Button Styling", layout="centered")

# Use your border fallback or Streamlit theme
border = 'rgb(250,250,250,.2)'  # dark mode fallback

# JS-based styling helper
def ChangeButtonColour(widget_label, font_color, hover_color, background_color='transparent'):
    htmlstr = f"""
        <script>
            const elements = window.parent.document.querySelectorAll('button');
            for (let i = 0; i < elements.length; ++i) {{
                const el = elements[i];
                if (el.innerText.trim() === '{widget_label}') {{
                    el.style.color = '{font_color}';
                    el.style.background = '{background_color}';
                    el.style.border = '1px solid {border}';
                    el.onmouseover = function() {{
                        this.style.color = '{hover_color}';
                        this.style.borderColor = '{hover_color}';
                    }};
                    el.onmouseout = function() {{
                        this.style.color = '{font_color}';
                        this.style.borderColor = '{border}';
                    }};
                    el.onfocus = function() {{
                        this.style.boxShadow = '{hover_color} 0px 0px 0px 0.2rem';
                        this.style.borderColor = '{hover_color}';
                        this.style.color = '{hover_color}';
                    }};
                    el.onblur = function() {{
                        this.style.boxShadow = 'none';
                        this.style.borderColor = '{border}';
                        this.style.color = '{font_color}';
                    }};
                }}
            }}
        </script>
    """
    components.html(htmlstr, height=0, width=0)

# ───────────────
# Vertical layout
# ───────────────
st.title("🎨 Vertical Buttons with Custom Colors")

if st.button("Primary", key="btn1"):
    st.toast("Primary clicked")

if st.button("Success", key="btn2"):
    st.toast("Success clicked")

if st.button("Danger", key="btn3"):
    st.toast("Danger clicked")

if st.button("Warning", key="btn4"):
    st.toast("Warning clicked")

if st.button("Info", key="btn5"):
    st.toast("Info clicked")

# ────────────────────────────────
# Apply styles (label must match)
# ────────────────────────────────
ChangeButtonColour("Primary", "#ffffff", "#e0e0e0", "#1f77b4")
ChangeButtonColour("Success", "#ffffff", "#d0ffd0", "#2ca02c")
ChangeButtonColour("Danger", "#ffffff", "#ffdddd", "#d62728")
ChangeButtonColour("Warning", "#000000", "#fff6d1", "#ff7f0e")
ChangeButtonColour("Info", "#ffffff", "#d6f3ff", "#17becf")
