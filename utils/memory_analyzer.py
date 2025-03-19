import openai
import os
import logging
import json
import traceback
from typing import Dict, Any, List, Optional, Tuple
import uuid

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analyze_memory_content(
    title: str, 
    content: str, 
    client_id: uuid.UUID,
    available_brands: List[Dict[str, Any]] = [],
    available_customers: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    """
    Analyze memory content and suggest the appropriate association level
    (client, brand, or customer) and other metadata like tags and memory_type.
    
    Args:
        title: The memory title
        content: The memory content
        client_id: The client ID this memory belongs to
        available_brands: List of brands associated with the client
        available_customers: List of customers associated with the client's brands
        
    Returns:
        A dict with suggested associations and metadata
    """
    try:
        # Check if API key is set
        if not openai.api_key:
            logger.warning("OpenAI API key not set. Using fallback logic for memory analysis.")
            # Fallback logic for development - basic keyword matching
            return fallback_memory_analysis(title, content, available_brands, available_customers)
        
        # Format available brands and customers for the prompt
        brands_text = "Available brands:\n"
        for brand in available_brands:
            brands_text += f"- {brand['name']} (ID: {brand['id']}): {brand.get('description', 'No description')}\n"
            
        customers_text = "Available customers:\n"
        for customer in available_customers:
            customers_text += f"- {customer['name']} (ID: {customer['id']}): Associated with brand {customer['brand_id']}\n"
        
        # Create a system prompt for the analysis
        system_prompt = f"""
        You are an AI assistant that analyzes business memory content and suggests the appropriate 
        association level and metadata. The memory is being added to a knowledge system with a 
        hierarchical structure:
        
        1. Client (top level) - for general information about the client company
        2. Brand (mid level) - for information specific to a brand owned by the client
        3. Customer (detail level) - for information specific to a customer of a brand
        
        Based on the memory title and content, determine:
        1. The most appropriate association level (client, brand, or customer)
        2. If brand or customer level, which specific brand or customer ID to associate with
        3. Suggested tags (3-5 keywords relevant to the content)
        4. Suggested memory_type category (e.g., "client_info", "brand_strategy", "customer_interaction")
        5. Suggested importance score (0.0-1.0) based on the strategic value of the information
        
        {brands_text}
        
        {customers_text}
        
        Respond with a JSON object containing your analysis results.
        """
        
        # Create a user prompt with the memory content
        user_prompt = f"""
        Memory Title: {title}
        
        Memory Content: {content}
        
        Please analyze this memory and suggest the appropriate associations and metadata.
        """
        
        # Call the OpenAI API
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse the response
        result_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        try:
            # Check if the response is already in JSON format
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = result_text[start_idx:end_idx]
                try:
                    result = json.loads(json_str)
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON from OpenAI response")
                    return fallback_memory_analysis(title, content, available_brands, available_customers)
            else:
                logger.error("Failed to extract JSON from OpenAI response")
                return fallback_memory_analysis(title, content, available_brands, available_customers)
        
        # Add the client_id to the result
        result["client_id"] = str(client_id)
        
        # Log the result
        logger.info(f"Memory analysis result: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing memory content: {str(e)}")
        logger.error(traceback.format_exc())
        # Return fallback analysis
        return fallback_memory_analysis(title, content, available_brands, available_customers)
    
def fallback_memory_analysis(
    title: str, 
    content: str, 
    available_brands: List[Dict[str, Any]] = [],
    available_customers: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    """
    Fallback function for basic memory analysis when OpenAI is not available.
    Uses simple keyword matching and heuristics.
    """
    result = {
        "association_level": "client",  # Default to client level
        "brand_id": None,
        "customer_id": None,
        "tags": [],
        "memory_type": "general",
        "importance_score": 0.5  # Default middle importance
    }
    
    # Extract potential tags from title and content
    combined_text = (title + " " + content).lower()
    
    # Check for customer mentions first (most specific)
    for customer in available_customers:
        customer_name = customer["name"].lower()
        if customer_name in combined_text:
            result["association_level"] = "customer"
            result["customer_id"] = str(customer["id"])
            result["brand_id"] = str(customer["brand_id"])
            result["memory_type"] = "customer_interaction"
            break
    
    # If no customer match, check for brand mentions
    if result["association_level"] == "client":
        for brand in available_brands:
            brand_name = brand["name"].lower()
            if brand_name in combined_text:
                result["association_level"] = "brand"
                result["brand_id"] = str(brand["id"])
                result["memory_type"] = "brand_information"
                break
    
    # Extract potential tags using basic frequency analysis
    words = combined_text.split()
    # Remove common words
    common_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "was", "were"]
    filtered_words = [w for w in words if w not in common_words and len(w) > 3]
    
    # Count word frequency
    word_counts = {}
    for word in filtered_words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    
    # Get top 5 words as tags
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    result["tags"] = [word for word, count in sorted_words[:5]]
    
    # Set importance based on content length and keyword presence
    importance_keywords = ["urgent", "important", "critical", "key", "strategic", "opportunity", "threat"]
    importance_score = 0.5  # Default
    
    # Adjust for content length
    content_length = len(content)
    if content_length > 500:
        importance_score += 0.1
    
    # Check for importance keywords
    for keyword in importance_keywords:
        if keyword in combined_text:
            importance_score += 0.1
            break
    
    # Cap at 1.0
    result["importance_score"] = min(importance_score, 1.0)
    
    return result 