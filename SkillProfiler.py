import streamlit as st

def main():
    """Streamlit UI for AI-powered skill evaluation."""
    st.title("AI-Powered Skill Evaluation 🚀")
    # Check if the API key is stored
    
    # Ask the user to input their Gemini API key
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = None
    if st.session_state.gemini_api_key:
        st.write("API Key is saved in session.")
    # Display a text input for the Gemini API key
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    
    # Save the API key to session state if provided
    # Add a Save button to store the API key
    if st.button("Submit API Key"):
        if api_key:
            st.session_state.gemini_api_key = api_key
            st.success("API Key saved successfully!")
        else:
            st.warning("Please enter a valid API key.")
    

if __name__ == "__main__":
    main()
