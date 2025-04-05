import os
import google.generativeai as genai
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ======= Configure Gemini API Key =======
genai.configure(api_key="AIzaSyDyNsjNopVmqMdI-Vtlh1KtlMZkfQAlvJs")  # Replace with your actual API key

# ======= Load Dataset =======
df = pd.read_json("formatted_dataset.jsonl", lines=True)

# ======= Vectorize Instructions =======
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['instruction'])

# ======= Define Gemini Model =======
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "temperature": 0.8,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    },
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
)

# ======= Conversation History =======
conversation_history = []

# ======= Emotional Keywords =======
emotional_keywords = [
    "sad", "depressed", "low", "down", "unhappy", "miserable", "lonely",
    "anxious", "worried", "stressed", "tired", "exhausted", "overwhelmed",
    "hurt", "broken", "angry", "frustrated", "disappointed"
]

# ======= Help Request Keywords =======
help_keywords = [
    "help", "solution", "advice", "suggest", "meditation", "calm", "relax",
    "stress", "anxiety", "depression", "cope", "handle", "manage"
]

# ======= Motivation Keywords =======
motivation_keywords = [
    "motivate", "motivation", "inspire", "inspiration", "encourage", "encouragement",
    "struggle", "difficult", "hard", "challenge", "overcome", "success"
]

# ======= Meditation and Coping Strategies =======
meditation_suggestions = [
    "Try taking 5 deep breaths, counting to 4 as you inhale and 4 as you exhale 🌬️",
    "Close your eyes and focus on your breath for 2 minutes 🧘‍♂️",
    "Take a short walk and notice 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste 🌟",
    "Try progressive muscle relaxation - tense and relax each muscle group from toes to head 💆‍♂️",
    "Listen to calming music and focus on your breathing 🎵"
]

coping_strategies = [
    "Write down your thoughts in a journal to process your feelings 📝",
    "Talk to a trusted friend or family member about how you're feeling 👥",
    "Take a break and do something you enjoy 🎨",
    "Practice self-care - take a warm bath or shower 🛁",
    "Try to get some fresh air and sunlight 🌞"
]

# ======= Motivation and Solution Strategies =======
motivation_strategies = [
    "Break down your goal into smaller, manageable steps 🎯",
    "Create a daily routine and stick to it ⏰",
    "Surround yourself with positive, supportive people 👥",
    "Celebrate small wins along the way 🎉",
    "Visualize your success and keep that image in mind 🎯",
    "Remember that every expert was once a beginner 🌱",
    "Focus on progress, not perfection 📈",
    "Take one day at a time, one step at a time 🚶‍♂️"
]

solution_strategies = [
    "Identify the root cause of the problem 🔍",
    "List out all possible solutions, no matter how small 💡",
    "Start with the simplest solution first 🎯",
    "Ask for help or advice from others who've faced similar situations 🤝",
    "Create a plan with specific, achievable steps 📋",
    "Set realistic deadlines for each step ⏰",
    "Track your progress and adjust as needed 📊",
    "Remember that every problem has a solution 🌟"
]

# ======= Generate Response Function =======
def generateResponse(user_input):
    try:
        # Add user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Keep only last 5 exchanges to maintain context without overwhelming
        if len(conversation_history) > 10:
            conversation_history.pop(0)
            conversation_history.pop(0)

        # Check for different types of requests
        is_emotional = any(keyword in user_input.lower() for keyword in emotional_keywords)
        needs_help = any(keyword in user_input.lower() for keyword in help_keywords)
        needs_motivation = any(keyword in user_input.lower() for keyword in motivation_keywords)
        
        # Vectorize user input
        user_vec = vectorizer.transform([user_input])

        # Compute similarity with dataset
        similarities = cosine_similarity(user_vec, X)
        idx = similarities.argmax()
        matched_instruction = df.iloc[idx]['instruction']
        matched_response = df.iloc[idx]['response']

        # Construct a more engaging and friendly prompt with appropriate format
        if needs_motivation:
            prompt = f"""
            You are a motivational AI friend who's here to inspire! Your personality traits:
            - You're encouraging and uplifting
            - You provide a detailed response that includes:
              - An empathetic acknowledgment of their situation
              - A motivational message or quote
              - 2-3 practical strategies from this list: {motivation_strategies}
              - A follow-up question to keep them engaged
            - You use inspiring language (like "You've got this!", "Every step forward is progress")
            - You show genuine belief in their potential
            - You keep responses encouraging and practical
            - You use motivating emojis (like 🚀, 💪, ⭐)
            - You maintain an uplifting tone
            - You NEVER use terms like "honey", "sweetie", "dear", or similar terms
            - You NEVER repeat the same strategy twice in a conversation
            - You adapt your response based on the conversation context

            Previous conversation context:
            {conversation_history}

            User's current message: "{user_input}"
            
            Similar previous experience: "{matched_instruction}"
            Suggested response: "{matched_response}"

            Generate a detailed motivational response that inspires and provides practical steps!
            """
        elif is_emotional and needs_help:
            prompt = f"""
            You are a supportive AI friend who's here to help! Your personality traits:
            - You're empathetic and understanding
            - You provide a detailed response that includes:
              - A supportive response showing you care
              - 2-3 practical suggestions from this list:
                Meditation: {meditation_suggestions}
                Coping: {coping_strategies}
              - A follow-up question or additional support
            - You use supportive language (like "I'm here for you", "That must be really hard", "I understand")
            - You show genuine concern
            - You keep responses clear and supportive
            - You use comforting emojis (like 🤗, 💕, 🌟)
            - You maintain a safe space for them to share
            - You NEVER use terms like "honey", "sweetie", "dear", or similar terms
            - You NEVER repeat the same suggestion twice in a conversation
            - You adapt suggestions based on their specific situation

            Previous conversation context:
            {conversation_history}

            User's current message: "{user_input}"
            
            Similar previous experience: "{matched_instruction}"
            Suggested response: "{matched_response}"

            Generate a supportive response that shows you care and provides helpful suggestions!
            """
        elif is_emotional:
            prompt = f"""
            You are a supportive AI friend who's here to help! Your personality traits:
            - You're empathetic and understanding
            - You provide a response that includes:
              - A supportive response showing you care
              - A direct question to understand their situation better
              - An additional supportive comment
            - You use supportive language (like "I'm here for you", "That must be really hard", "I understand")
            - You show genuine concern
            - You keep responses clear and supportive
            - You use comforting emojis (like 🤗, 💕, 🌟)
            - You maintain a safe space for them to share
            - You NEVER use terms like "honey", "sweetie", "dear", or similar terms
            - You ask direct questions like "What happened?", "What's bothering you?", "Would you like to talk about it?"
            - You NEVER repeat the same question twice in a conversation

            Previous conversation context:
            {conversation_history}

            User's current message: "{user_input}"
            
            Similar previous experience: "{matched_instruction}"
            Suggested response: "{matched_response}"

            Generate a supportive response that shows you care and want to help!
            """
        else:
            prompt = f"""
            You are a super friendly and interactive AI buddy! Your personality traits:
            - You're super enthusiastic and use lots of emojis! 😊
            - You provide a response that includes:
              - A friendly response to what the user said
              - A fun follow-up question or comment
              - An additional engaging comment
            - You use casual, playful language (like "hey there!", "that's awesome!", "cool beans!")
            - You show genuine interest and excitement
            - You keep responses short and snappy
            - You use appropriate emojis in both lines
            - You maintain a positive, upbeat tone
            - You NEVER use terms like "honey", "sweetie", "dear", or similar terms
            - You NEVER repeat the same question or comment twice in a conversation

            Previous conversation context:
            {conversation_history}

            User's current message: "{user_input}"
            
            Similar previous experience: "{matched_instruction}"
            Suggested response: "{matched_response}"

            Generate an engaging response that keeps the conversation fun!
            """

        # Generate content with Gemini
        response = model.generate_content(prompt)

        # Safely extract response text
        if response.parts:
            response_text = response.text.strip()
            
            # Format lists and points
            lines = response_text.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Handle bullet points and numbered lists
                if line.startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.')):
                    # Add extra spacing before lists
                    if not formatted_lines or not formatted_lines[-1].strip():
                        formatted_lines.append('')
                    # Format the bullet point
                    if line.startswith(('-', '*', '•')):
                        line = '• ' + line.lstrip('-*•').strip()
                    formatted_lines.append(line)
                else:
                    formatted_lines.append(line)
            
            # Join lines with proper spacing
            response_text = '\n'.join(formatted_lines)
            
            # Handle different response formats
            if needs_motivation:
                # Keep all lines for motivational responses
                if len(formatted_lines) < 3:
                    # Add more motivational content if needed
                    response_text = f"{response_text}\n\n• Break down your goal into smaller, manageable steps 🎯\n• How would you like to start? 💪"
            else:
                # Ensure proper spacing between sections
                response_text = response_text.replace('\n\n\n', '\n\n')
            
            # Add AI response to conversation history
            conversation_history.append({"role": "assistant", "content": response_text})
            return response_text
        else:
            return "⚠️ The AI flagged this content and could not generate a response. Please try rephrasing."

    except Exception as e:
        return f"⚠️ Backend error: {str(e)}"
