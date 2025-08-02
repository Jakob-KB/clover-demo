import streamlit as st

# Setup state
if "menu_choice" not in st.session_state:
    st.session_state.menu_choice = None

st.components.v1.html("""
<style>
.combo-wrapper {
  position: relative;
  display: flex;
  width: 240px;
  font-family: "Segoe UI", Roboto, sans-serif;
  margin-bottom: 0.5rem;
}

.combo-button {
  background-color: rgb(38, 39, 48);
  color: white;
  border: 1px solid rgba(250, 250, 250, 0.2);
  padding: 0.5rem 0.75rem;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  transition: background-color 0.2s ease;
}

.combo-button:hover {
  background-color: rgb(64, 65, 78);
}

#main-btn {
  flex-grow: 1;
  border-top-left-radius: 0.5rem;
  border-bottom-left-radius: 0.5rem;
  border-right: none;
  text-align: left;
}

#dots-btn {
  width: 40px;
  text-align: center;
  border-top-right-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
}

/* Updated: Floating menu to the right */
.menu {
  display: none;
  position: absolute;
  top: 0;
  left: 100%;
  margin-left: 6px;
  background-color: #2d2e3e;
  border: 1px solid rgba(250, 250, 250, 0.2);
  border-radius: 6px;
  z-index: 9999;
  min-width: 140px;
  box-shadow: 0 0 8px rgba(0,0,0,0.3);
}

.menu button {
  width: 100%;
  background: none;
  border: none;
  color: white;
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-size: 14px;
  cursor: pointer;
}

.menu button:hover {
  background-color: rgb(64, 65, 78);
}
</style>

<div class="combo-wrapper">
  <button id="main-btn" class="combo-button">Main Action</button>
  <button id="dots-btn" class="combo-button">&#x22EE;</button>

  <div id="menu" class="menu">
    <button onclick="sendChoice('__OPTION_1__')">Option 1</button>
    <button onclick="sendChoice('__OPTION_2__')">Option 2</button>
  </div>
</div>

<script>
const mainBtn = document.getElementById("main-btn");
const dotsBtn = document.getElementById("dots-btn");
const menu = document.getElementById("menu");

mainBtn.addEventListener("click", () => {
  const el = window.parent.document.querySelector('[data-testid="stTextInput"] input');
  if (el) {
    el.value = "__MAIN_ACTION__";
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }
});

dotsBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  menu.style.display = menu.style.display === "block" ? "none" : "block";
});

window.addEventListener("click", () => {
  menu.style.display = "none";
});

function sendChoice(val) {
  const el = window.parent.document.querySelector('[data-testid="stTextInput"] input');
  if (el) {
    el.value = val;
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }
}
</script>

<input style="display:none;" />
""", height=150)

# Trigger
user_input = st.text_input("trigger", key="trigger_input", label_visibility="collapsed")

if user_input == "__MAIN_ACTION__":
    st.toast("Main button clicked!")
    st.session_state.menu_choice = None
elif user_input == "__OPTION_1__":
    st.session_state.menu_choice = "Option 1"
elif user_input == "__OPTION_2__":
    st.session_state.menu_choice = "Option 2"

if st.session_state.menu_choice:
    st.success(f"You selected: {st.session_state.menu_choice}")