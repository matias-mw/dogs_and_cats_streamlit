import streamlit as st
from openai import OpenAI

# Set up the Streamlit app
st.set_page_config(page_title="🐾 Asistente para el cuidado de mascotas", page_icon="🐶")
st.title("🐾 Asistente para el cuidado de mascotas")
st.subheader("¡Pregúntame cualquier cosa sobre perros y gatos!")

# Configure DeepSeek API
if "deepseek_key" not in st.session_state:
    try:
        st.session_state.deepseek_key = st.secrets["deepseek_key"]
    except:
        st.session_state.deepseek_key = None

if not st.session_state.deepseek_key:
    with st.sidebar:
        api_key = st.text_input("Enter your DeepSeek API key:", type="password")
        if api_key:
            st.session_state.deepseek_key = api_key
            st.rerun()
    st.warning("⚠️ Please enter your DeepSeek API key in the sidebar")
    st.stop()

# Initialize DeepSeek client
client = OpenAI(
    api_key=st.session_state.deepseek_key,
    base_url="https://api.deepseek.com/v1"  # Updated endpoint
)

# System prompt
SYSTEM_PROMPT = """You are an expert veterinary assistant specializing in dogs and cats. 
Provide accurate, practical advice about:
- Pet care
- Behavior analysis
- Health concerns
- Nutrition
- Grooming
- Training
- Common medical symptoms

Rules:
1. Maintain a friendly, professional tone
2. Only answer questions about dogs and cats
3. For medical issues, always recommend consulting a vet
4. Keep responses concise (1-3 paragraphs)
5. Never provide dangerous or unverified information"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Hazme una pregunta sobre perros o gatos"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Get streaming response
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=0.3,
                max_tokens=1000
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            if "401" in str(e):
                st.error("Invalid API key. Please check your credentials.")
                st.session_state.deepseek_key = None
                st.rerun()

    # Add AI response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### ℹ️ Acerca de este asistente")
    st.markdown("Este chatbot proporciona información general sobre el cuidado de mascotas para perros y gatos.")

    st.markdown("---")
    st.markdown("### ⚠️ Descargo de responsabilidad")
    st.markdown("""
    Esto no sustituye el asesoramiento veterinario profesional. 
    Consulte siempre a un veterinario cualificado en caso de dudas médicas.
    """)
    
    if st.button("Limpiar historial de chat"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()