import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.3";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const GROQ_API_KEY = Deno.env.get("llama32vision");
    if (!GROQ_API_KEY) {
      throw new Error("llama32vision API key not configured");
    }

    const { imageBase64 } = await req.json();
    
    if (!imageBase64) {
      throw new Error("imageBase64 is required");
    }

    console.log("Analyzing room object image with Llama 3.2 Vision...");

    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama-3.2-90b-vision-preview",
        messages: [
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "You are analyzing an object photo for a memory palace technique. Provide a concise, memorable name for this object (2-4 words max) and a brief description (1 sentence) that emphasizes distinctive visual features. Format: {\"name\": \"Object Name\", \"description\": \"Brief description\"}. Return ONLY valid JSON, no markdown or explanation."
              },
              {
                type: "image_url",
                image_url: {
                  url: `data:image/jpeg;base64,${imageBase64}`
                }
              }
            ]
          }
        ],
        temperature: 0.7,
        max_tokens: 150
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Groq API error:", response.status, errorText);
      // Return placeholder text when API fails
      return new Response(
        JSON.stringify({ 
          name: "API Call Text", 
          description: "API Call Text" 
        }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    const content = data.choices[0]?.message?.content;
    
    if (!content) {
      throw new Error("No content in Groq response");
    }

    // Parse JSON from response
    let result;
    try {
      // Remove markdown code blocks if present
      const cleanContent = content.replace(/```json\n?|\n?```/g, '').trim();
      result = JSON.parse(cleanContent);
    } catch (e) {
      console.error("Failed to parse JSON:", content);
      // Fallback: extract name and description manually
      result = {
        name: "Unknown Object",
        description: content.substring(0, 100)
      };
    }

    return new Response(
      JSON.stringify(result),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );

  } catch (error) {
    console.error("Error in analyze-room-image:", error);
    // Return placeholder text when API fails
    return new Response(
      JSON.stringify({ 
        name: "API Call Text", 
        description: "API Call Text" 
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
