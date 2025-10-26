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
    const GROQ_API_KEY = Deno.env.get("llama4");
    const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
    const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

    if (!GROQ_API_KEY) {
      throw new Error("llama4 API key not configured");
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
    const { floorId, pdfText, rooms } = await req.json();
    
    if (!floorId || !pdfText || !rooms) {
      throw new Error("floorId, pdfText, and rooms are required");
    }

    console.log("Generating mind palace associations with Llama 4...");
    console.log("Rooms:", rooms.length);
    console.log("PDF text length:", pdfText.length);
    
    // Count total objects
    const totalObjects = rooms.reduce((sum: number, room: any) => sum + (room.objects?.length || 0), 0);
    console.log("Total objects:", totalObjects);
    
    if (totalObjects === 0) {
      throw new Error("No room objects found. Please add objects to your rooms first.");
    }

    let concepts: string[] = [];

    // Extract key concepts from PDF text (one per object)
    const conceptResponse = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        messages: [
          {
            role: "system",
            content: "You are an expert at extracting key concepts from educational material for memory palace techniques. Extract the most important concepts that need to be memorized. Always respond with a valid JSON array of strings."
          },
          {
            role: "user",
            content: `Extract exactly ${totalObjects} key concepts from this text that should be memorized. Return ONLY a JSON array of strings, one concept per string. Be specific and concise. Example format: ["Concept 1", "Concept 2", ...]\n\nText: ${pdfText.substring(0, 10000)}`
          }
        ],
        temperature: 0.7,
        max_tokens: 2000
      })
    });

    if (!conceptResponse.ok) {
      const errorText = await conceptResponse.text();
      console.error("Groq API error for concepts:", conceptResponse.status, errorText);
      // Use placeholder concepts when API fails
      concepts = Array(totalObjects).fill("API Call Text");
    } else {
      const conceptData = await conceptResponse.json();
      
      try {
        const content = conceptData.choices[0]?.message?.content || "{}";
        console.log("Raw concept response:", content);
        
        // Try to parse as JSON
        let parsed;
        try {
          parsed = JSON.parse(content);
        } catch {
          // If not valid JSON, try to extract array from text
          const arrayMatch = content.match(/\[[\s\S]*\]/);
          if (arrayMatch) {
            parsed = JSON.parse(arrayMatch[0]);
          } else {
            throw new Error("Could not find array in response");
          }
        }
        
        // Handle different response formats
        if (Array.isArray(parsed)) {
          concepts = parsed;
        } else if (parsed.concepts && Array.isArray(parsed.concepts)) {
          concepts = parsed.concepts;
        } else if (parsed.items && Array.isArray(parsed.items)) {
          concepts = parsed.items;
        } else {
          // Extract any string values from object
          concepts = Object.values(parsed).filter(v => typeof v === 'string');
        }
        
        // Ensure we have enough concepts
        while (concepts.length < totalObjects) {
          concepts.push(`Concept ${concepts.length + 1}`);
        }
        
        // Trim to exact number needed
        concepts = concepts.slice(0, totalObjects);
        
        console.log(`Extracted ${concepts.length} concepts:`, concepts);
      } catch (e) {
        console.error("Failed to parse concepts:", e);
        concepts = Array(totalObjects).fill("API Call Text");
      }
    }

    // Generate associations for each room
    const associations = [];
    let conceptIndex = 0;

    for (const room of rooms) {
      const roomObjects = room.objects || [];
      
      for (const obj of roomObjects) {
        if (conceptIndex >= concepts.length) break;
        
        const concept = concepts[conceptIndex];
        
        // Generate mnemonic
        const mnemonicResponse = await fetch("https://api.groq.com/openai/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${GROQ_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: "llama-3.3-70b-versatile",
            messages: [
              {
                role: "system",
                content: "You are a memory expert creating vivid, memorable associations for the memory palace technique. Create a short, vivid story or image that links the object to the concept."
              },
              {
                role: "user",
                content: `Create a memorable mnemonic linking this object to this concept:\n\nObject: ${obj.name}\nDescription: ${obj.description}\n\nConcept to remember: ${concept}\n\nReturn a single sentence (max 100 words) creating a vivid, memorable association.`
              }
            ],
            temperature: 0.8,
            max_tokens: 150
          })
        });

        let mnemonic = "API Call Text";
        
        if (mnemonicResponse.ok) {
          const mnemonicData = await mnemonicResponse.json();
          mnemonic = mnemonicData.choices[0]?.message?.content || "API Call Text";
        }

        associations.push({
          floor_id: floorId,
          object_id: obj.id,
          core_concept: concept,
          mnemonic_text: mnemonic,
          display_order: conceptIndex
        });

        conceptIndex++;
      }
    }

    // Insert associations into database
    const { data, error } = await supabase
      .from('associations')
      .insert(associations)
      .select();

    if (error) {
      throw new Error(`Failed to save associations: ${error.message}`);
    }

    // Update floor status to 'ready'
    await supabase
      .from('floors')
      .update({ status: 'ready' })
      .eq('id', floorId);

    return new Response(
      JSON.stringify({ associations: data, conceptCount: associations.length }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );

  } catch (error) {
    console.error("Error in generate-associations:", error);
    // Return placeholder response when function fails
    return new Response(
      JSON.stringify({ 
        associations: [], 
        conceptCount: 0,
        error: "Using placeholder data due to API failure" 
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
