import streamlit as st
import requests

st.title("LLM Chat based on the information from Medscape site.")

# Display the initial prompt from the model
initial_prompt = "How can I help you?"

# Display the initial prompt
st.chat_message("bot").write(initial_prompt)

# Input field for the user to enter their question
question = st.text_input("Enter your question:")

# Button to submit the question
if st.button("Submit"):
    if question:
        # Display the user's question
        st.chat_message("user").write(question)
        
        # Make a POST request to the FastAPI endpoint
        response = requests.post("http://fastapi:8000/test/", json={"question": question})
        
        # Check the response status
        if response.status_code == 200:
            answer = response.json()["response"]
            # Display the response from the model
            st.chat_message("bot").write(answer)
        else:
            error_message = "Error: " + response.text
            # Display the error message
            st.chat_message("bot").write(error_message)