import streamlit as st
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

# Streamlit UI
st.title("Sentiment Analysis and Word Cloud Application")
st.write("Enter your text below to analyze its sentiment and generate a word cloud:")

# Text input
user_input = st.text_area("Input Text", "")

# Function to determine sentiment
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity  # Get the polarity score (-1 to 1)

    if sentiment > 0:
        sentiment_label = "Positive"
    elif sentiment < 0:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"
    
    return sentiment_label, sentiment

# Function to generate word cloud
def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    return wordcloud

# Check if the user has entered text
if user_input:
    # Sentiment Analysis
    sentiment, score = analyze_sentiment(user_input)
    
    # Display Sentiment Analysis result
    st.subheader("Sentiment Analysis Result")
    st.write(f"Sentiment: **{sentiment}**")
    st.write(f"Sentiment Score: {score:.2f}")
    
    # Display the overall sentiment as a color-coded label
    if sentiment == "Positive":
        st.markdown('<h3 style="color: green;">Positive Sentiment</h3>', unsafe_allow_html=True)
    elif sentiment == "Negative":
        st.markdown('<h3 style="color: red;">Negative Sentiment</h3>', unsafe_allow_html=True)
    else:
        st.markdown('<h3 style="color: gray;">Neutral Sentiment</h3>', unsafe_allow_html=True)

    # Generate and display the Word Cloud
    st.subheader("Word Cloud")
    wordcloud = generate_wordcloud(user_input)

    # Display the WordCloud using Matplotlib
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)
    
    # Optional: Display the word count as a DataFrame
    word_freq = pd.Series(user_input.split()).value_counts().reset_index()
    word_freq.columns = ['Word', 'Frequency']
    
    st.write("### Word Frequency")
    st.dataframe(word_freq)

