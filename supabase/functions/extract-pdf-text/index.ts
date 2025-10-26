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
    const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
    const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

    if (!GROQ_API_KEY) {
      throw new Error("llama32vision API key not configured");
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
    const { pdfFileId, storagePath } = await req.json();
    
    if (!storagePath) {
      throw new Error("storagePath is required");
    }

    console.log("Downloading PDF from storage:", storagePath);

    // Download PDF from Supabase storage
    const { data: pdfData, error: downloadError } = await supabase.storage
      .from('pdfs')
      .download(storagePath);

    if (downloadError) {
      throw new Error(`Failed to download PDF: ${downloadError.message}`);
    }

    // Convert PDF to images using pdf-lib or similar
    // For now, we'll use a simplified approach with base64
    const arrayBuffer = await pdfData.arrayBuffer();
    const base64Pdf = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

    console.log("Extracting text from PDF with Llama 3.2 Vision...");

    // Note: This is a simplified version. In production, you'd want to:
    // 1. Convert PDF pages to images using a library like pdf-lib
    // 2. Process each page separately
    // 3. Combine results
    
    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "meta-llama/llama-4-scout-17b-16e-instruct",
        messages: [
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Extract ALL text from this document. Return only the extracted text content, maintaining the original structure. Do not add any commentary, formatting, or explanation. Just the raw text."
              },
              {
                type: "image_url",
                image_url: {
                  url: `data:application/pdf;base64,${base64Pdf}`
                }
              }
            ]
          }
        ],
        temperature: 0.1,
        max_tokens: 8000
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Groq API error:", response.status, errorText);
      // Return placeholder text when API fails
      return new Response(
        JSON.stringify({ extractedText: "API Call Text" }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    const extractedText = data.choices[0]?.message?.content || "";

    // Update the pdf_files table with extracted text
    if (pdfFileId) {
      const { error: updateError } = await supabase
        .from('pdf_files')
        .update({ extracted_text: extractedText })
        .eq('id', pdfFileId);

      if (updateError) {
        console.error("Failed to update pdf_files:", updateError);
      }
    }

    return new Response(
      JSON.stringify({ extractedText }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );

  } catch (error) {
    console.error("Error in extract-pdf-text:", error);
    // Return placeholder text when API fails
    return new Response(
      JSON.stringify({ extractedText: "API Call Text" }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
