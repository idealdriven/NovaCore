import openai
import os
from typing import List, Dict, Any, Optional, Tuple
import json
import logging
from models import Memory, ConversationMessage
import traceback

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def extract_key_topics(content: str, max_topics: int = 5) -> List[str]:
    """
    Extract key topics from memory content.
    Returns a list of topic strings.
    """
    try:
        # If OpenAI API key is not set, use a simple approach
        if not openai.api_key:
            return extract_topics_simple(content, max_topics)
        
        # Use OpenAI to extract topics
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Extract up to {max_topics} key topics from the following text. Return only the topics as a comma-separated list, with no additional text."},
                {"role": "user", "content": content}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        # Parse the response
        topics_text = response.choices[0].message.content.strip()
        
        # Split by commas and clean up
        topics = [topic.strip() for topic in topics_text.split(",")]
        
        # Limit to max_topics
        return topics[:max_topics]
        
    except Exception as e:
        logger.error(f"Error extracting key topics: {str(e)}")
        logger.error(traceback.format_exc())
        # Fall back to simple approach
        return extract_topics_simple(content, max_topics)

def extract_topics_simple(content: str, max_topics: int = 5) -> List[str]:
    """
    Simple fallback method to extract topics based on word frequency.
    """
    # Lowercase the content
    content_lower = content.lower()
    
    # Split into words
    words = content_lower.split()
    
    # Remove common words and short words
    common_words = [
        "the", "a", "an", "and", "or", "but", "if", "then", "else", "when",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "done", "to", "from", "by", "on", "at", "in", "for",
        "with", "about", "as", "of", "that", "this", "these", "those", "it", "its"
    ]
    
    filtered_words = [word for word in words if word not in common_words and len(word) > 3]
    
    # Count frequencies
    word_counts = {}
    for word in filtered_words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Extract top words
    topics = [word for word, _ in sorted_words[:max_topics]]
    
    return topics

async def analyze_sentiment(text: str) -> float:
    """
    Analyze the sentiment of a text using OpenAI.
    Returns a float between -1.0 (very negative) and 1.0 (very positive).
    """
    try:
        if not openai.api_key:
            logger.warning("OpenAI API key not set. Using neutral sentiment score.")
            return 0.0
        
        system_prompt = "You are a sentiment analysis expert. Analyze the sentiment of text and respond with a single number between -1.0 (very negative) and 1.0 (very positive)."
        
        user_prompt = f"""
        Analyze the sentiment of the following text.
        Respond with ONLY a single number between -1.0 (very negative) and 1.0 (very positive).
        
        Text: {text}
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=10,
            temperature=0.3
        )
        
        sentiment_text = response.choices[0].message.content.strip()
        
        # Convert to float
        sentiment = float(sentiment_text)
        
        # Ensure it's within range
        return max(min(sentiment, 1.0), -1.0)
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return 0.0  # Default to neutral

async def extract_action_items(text: str, max_items: int = 3) -> List[str]:
    """
    Extract action items from a text using OpenAI.
    """
    try:
        if not openai.api_key:
            logger.warning("OpenAI API key not set. Using placeholder action items.")
            return ["placeholder-action-1", "placeholder-action-2"]
        
        system_prompt = "You are an executive assistant skilled at identifying action items in text. Extract the most important action items as a JSON array of strings."
        
        user_prompt = f"""
        Analyze the following text and extract up to {max_items} clear action items that should be acted upon.
        Return ONLY a JSON array of strings, with no explanation.
        If there are no clear action items, return an empty array.
        
        Text: {text}
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        actions_text = response.choices[0].message.content.strip()
        
        # Handle potential formatting issues
        if not actions_text.startswith("["):
            actions_text = "[" + actions_text
        if not actions_text.endswith("]"):
            actions_text = actions_text + "]"
        
        actions = json.loads(actions_text)
        return actions[:max_items]  # Ensure we don't exceed max_items
        
    except Exception as e:
        logger.error(f"Error extracting action items: {str(e)}")
        return []

async def generate_memory_summary(memories: List[Memory], client_name: str) -> str:
    """
    Generate a summary of memories.
    """
    try:
        if not memories:
            return "No memories available to summarize."
        
        if not openai.api_key:
            logger.warning("OpenAI API key not set. Using placeholder summary.")
            return f"Summary of {len(memories)} memories for client {client_name}."
        
        # Create context for the summary
        context = "\n".join([
            f"Memory {i+1}: {memory.title}\n{memory.content}\n" 
            for i, memory in enumerate(memories[:5])  # Limit to 5 memories to avoid token limits
        ])
        
        system_prompt = "You are an AI assistant specializing in business intelligence. Summarize key information from client memories concisely."
        
        user_prompt = f"""
        Summarize the following memories for client "{client_name}".
        Focus on key insights, patterns, and important information.
        Keep the summary concise and informative.
        
        {context}
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        logger.error(f"Error generating memory summary: {str(e)}")
        return f"Error generating summary for {len(memories)} memories."

async def calculate_importance_score(content: str) -> float:
    """
    Calculate an importance score (0.0-1.0) for a memory based on its content.
    Uses a simple heuristic based on content length and keyword presence.
    """
    try:
        # If OpenAI API key is set, we could use more sophisticated scoring
        # For now, implement a simple heuristic
        
        # Base score
        score = 0.5
        
        # Adjust for content length
        content_length = len(content)
        if content_length < 100:
            score -= 0.1
        elif content_length > 500:
            score += 0.1
        
        # Check for important keywords
        important_keywords = [
            "urgent", "critical", "important", "key", "significant", 
            "strategic", "priority", "essential", "crucial"
        ]
        
        content_lower = content.lower()
        for keyword in important_keywords:
            if keyword in content_lower:
                score += 0.1
                break
        
        # Cap the score between 0.1 and 1.0
        score = max(0.1, min(score, 1.0))
        
        return score
        
    except Exception as e:
        logger.error(f"Error calculating importance score: {str(e)}")
        logger.error(traceback.format_exc())
        # Return a default importance score
        return 0.5 