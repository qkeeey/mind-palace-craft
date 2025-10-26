"""
Concept Generator Service
Generates key concepts from PDF text using Groq LLM
"""

import os
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
import json
from logging_config import setup_logger

# Load environment variables
load_dotenv()

# Set up logger
logger = setup_logger(__name__, "concept_generation.log")


class ConceptGenerator:
    """Service for generating key concepts from text using Groq LLM."""
    
    def __init__(self):
        """Initialize Concept Generator with Groq client."""
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            error_msg = "GROQ_API_KEY not found in environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.groq_client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"  # Fast, powerful model
        logger.info(f"ConceptGenerator initialized with model: {self.model_name}")
    
    def generate_concepts(
        self, 
        pdf_text: str, 
        num_concepts: int = 10
    ) -> List[Dict[str, str]]:
        """
        Generate key concepts from PDF text.
        
        Args:
            pdf_text: The extracted text from PDF
            num_concepts: Number of concepts to generate
            
        Returns:
            List of dictionaries containing concept and description
        """
        logger.info(f"Starting concept generation for {num_concepts} concepts from text ({len(pdf_text)} chars)")
        
        if not pdf_text or len(pdf_text.strip()) < 50:
            error_msg = "PDF text is too short to generate concepts"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # Truncate if text is too long (to fit in context window)
        max_chars = 15000
        original_length = len(pdf_text)
        if len(pdf_text) > max_chars:
            pdf_text = pdf_text[:max_chars] + "\n... [text truncated]"
            logger.warning(f"Text truncated from {original_length} to {max_chars} chars to fit context window")
        
        system_prompt = """You are an expert educational content analyzer specializing in the Memory Palace (Method of Loci) technique.

Your task is to identify the most important concepts from study material and make them memorable.

Guidelines:
1. Focus on the most important, fundamental concepts
2. Make concepts specific and actionable
3. Keep concept names short and memorable (2-6 words)
4. Descriptions should be clear and concise (20-40 words)
5. Prioritize concepts that would benefit from visualization
6. Return ONLY valid JSON, no other text

Output format:
{
  "concepts": [
    {
      "concept": "Short memorable name",
      "description": "Clear, concise description of the concept"
    }
  ]
}"""

        user_prompt = f"""Analyze the following study material and extract the {num_concepts} most important concepts.

Study Material:
{pdf_text}

Generate exactly {num_concepts} key concepts with short names and clear descriptions. Return only valid JSON."""

        try:
            logger.info(f"Calling Groq API with model: {self.model_name}")
            logger.debug(f"Prompt length: system={len(system_prompt)}, user={len(user_prompt)}")
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Log API response metadata
            logger.info(f"API call successful. Tokens used: prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}, total={response.usage.total_tokens}")
            
            # Parse response
            result_text = response.choices[0].message.content
            logger.debug(f"Raw API response ({len(result_text)} chars): {result_text[:200]}...")
            
            result = json.loads(result_text)
            logger.info("Successfully parsed JSON response")
            
            # Validate and format
            if "concepts" in result and isinstance(result["concepts"], list):
                concepts = result["concepts"][:num_concepts]
                logger.info(f"Found {len(concepts)} concepts in response")
                
                # Ensure each concept has required fields
                formatted_concepts = []
                for i, concept in enumerate(concepts):
                    if "concept" in concept and "description" in concept:
                        formatted_concepts.append({
                            "concept": concept["concept"],
                            "description": concept["description"]
                        })
                        logger.debug(f"Concept {i+1}: {concept['concept']}")
                    else:
                        logger.warning(f"Skipping invalid concept {i+1}: missing required fields")
                
                logger.info(f"Successfully generated {len(formatted_concepts)} valid concepts")
                return formatted_concepts
            else:
                error_msg = "Invalid response format from LLM - missing 'concepts' array"
                logger.error(f"{error_msg}. Response structure: {list(result.keys())}")
                return {"error": error_msg}
                
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
            logger.error(error_msg, exc_info=True)
            logger.error(f"Raw response that failed to parse: {result_text[:500]}...")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error generating concepts: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"error": error_msg}


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python concept_generator.py <pdf_text_file> [num_concepts]")
        sys.exit(1)
    
    text_file = sys.argv[1]
    num_concepts = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    if not os.path.exists(text_file):
        print(f"Error: File not found: {text_file}")
        sys.exit(1)
    
    with open(text_file, 'r', encoding='utf-8') as f:
        pdf_text = f.read()
    
    print(f"Generating {num_concepts} concepts from {text_file}...")
    
    generator = ConceptGenerator()
    concepts = generator.generate_concepts(pdf_text, num_concepts)
    
    if isinstance(concepts, dict) and "error" in concepts:
        print(f"Error: {concepts['error']}")
    else:
        print(f"\nGenerated {len(concepts)} concepts:\n")
        for i, concept in enumerate(concepts, 1):
            print(f"{i}. {concept['concept']}")
            print(f"   {concept['description']}\n")
