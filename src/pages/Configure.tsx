import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, Brain, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RoomCard } from "@/components/RoomCard";
import { PdfInputTile } from "@/components/PdfInputTile";
import { NewRoomModal } from "@/components/NewRoomModal";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";

interface PdfFile {
  id: string;
  name: string;
  file: File;
}

interface Room {
  id: string;
  name: string;
  thumbnail_url: string | null;
  object_count: number;
}

const Configure = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [floorName, setFloorName] = useState(location.state?.floorName || "");
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null); // Changed to single room
  const [pdfFiles, setPdfFiles] = useState<PdfFile[]>(location.state?.pdfFiles || []);
  const [showNewRoomModal, setShowNewRoomModal] = useState(false);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState<{
    currentPdf?: string;
    currentPage?: number;
    totalPages?: number;
    stage?: string;
  }>({});

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      const { data, error } = await supabase
        .from('rooms')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      setRooms(data || []);
    } catch (error) {
      console.error('Error fetching rooms:', error);
      toast.error('Failed to load rooms');
    }
  };

  const handleToggleRoom = (roomId: string) => {
    // Toggle selection - only one room can be selected
    setSelectedRoom((prev) => prev === roomId ? null : roomId);
  };

  const handleAddPdfs = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const newPdfs: PdfFile[] = files.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      file,
    }));
    setPdfFiles((prev) => [...prev, ...newPdfs]);
  };

  const handleRemovePdf = (id: string) => {
    setPdfFiles((prev) => prev.filter((pdf) => pdf.id !== id));
  };

  const handleDeleteRoom = async (roomId: string) => {
    try {
      const { error } = await supabase
        .from('rooms')
        .delete()
        .eq('id', roomId);

      if (error) throw error;
      
      toast.success('Room deleted successfully');
      if (selectedRoom === roomId) {
        setSelectedRoom(null);
      }
      fetchRooms();
    } catch (error) {
      console.error('Error deleting room:', error);
      toast.error('Failed to delete room');
    }
  };

  const handleGenerate = async () => {
    if (!floorName.trim()) {
      toast.error("Please enter a floor name");
      return;
    }
    if (!selectedRoom) {
      toast.error("Please select a room");
      return;
    }
    if (pdfFiles.length === 0) {
      toast.error("Please add at least one PDF");
      return;
    }

    setIsGenerating(true);
    setGenerationProgress({ stage: "Creating floor..." });
    toast.success("Starting generation...");

    try {
      // 1. Find or create floor (case-insensitive)
      setGenerationProgress({ stage: "Creating floor..." });
      
      // Check if floor exists (case-insensitive)
      const { data: existingFloors, error: searchError } = await supabase
        .from('floors')
        .select('*');
      
      if (searchError) throw searchError;
      
      let floor;
      const normalizedFloorName = floorName.trim().toLowerCase();
      const existingFloor = existingFloors?.find(f => 
        f.name.toLowerCase() === normalizedFloorName
      );
      
      if (existingFloor) {
        // Use existing floor
        floor = existingFloor;
        toast.info(`Adding room to existing floor: ${existingFloor.name}`);
      } else {
        // Create new floor
        const { data: newFloor, error: floorError } = await supabase
          .from('floors')
          .insert([{ name: floorName.trim(), status: 'generating' }])
          .select()
          .single();

        if (floorError) throw floorError;
        floor = newFloor;
        toast.success(`Created new floor: ${floorName.trim()}`);
      }

      // 2. Link selected room to floor (only ONE room now)
      // Check if this room is already linked to this floor
      const { data: existingLink } = await supabase
        .from('floor_rooms')
        .select('*')
        .eq('floor_id', floor.id)
        .eq('room_id', selectedRoom)
        .single();

      if (!existingLink) {
        const { error: linkError } = await supabase
          .from('floor_rooms')
          .insert({
            floor_id: floor.id,
            room_id: selectedRoom
          });

        if (linkError) throw linkError;
        console.log('Linked room to floor');
      } else {
        console.log('Room already linked to floor - will replace associations');
        
        // Delete existing associations for this room-floor combination
        const { error: deleteError } = await supabase
          .from('floor_room_objects')
          .delete()
          .eq('floor_id', floor.id)
          .eq('room_id', selectedRoom);

        if (deleteError) {
          console.error('Error deleting old associations:', deleteError);
        } else {
          console.log('Deleted old associations for this room-floor combination');
        }
      }

      // 3. Upload PDFs and extract text using LOCAL API
      let allExtractedText = "";
      const LOCAL_API_URL = "http://localhost:8081";
      
      for (let i = 0; i < pdfFiles.length; i++) {
        const pdf = pdfFiles[i];
        setGenerationProgress({ 
          stage: `Processing PDF ${i + 1}/${pdfFiles.length}...`,
          currentPdf: pdf.name,
          currentPage: 0,
          totalPages: 0
        });
        
        try {
          // Upload to Supabase storage
          const filePath = `${floor.id}/${pdf.file.name}`;
          const { error: uploadError } = await supabase.storage
            .from('pdfs')
            .upload(filePath, pdf.file);

          if (uploadError) throw uploadError;

          // Save PDF file record
          const { data: pdfFile, error: pdfError } = await supabase
            .from('pdf_files')
            .insert({
              floor_id: floor.id,
              file_name: pdf.file.name,
              storage_path: filePath
            })
            .select()
            .single();

          if (pdfError) throw pdfError;

          // Call LOCAL API for PDF extraction
          setGenerationProgress({ 
            stage: `Extracting text from ${pdf.name}...`,
            currentPdf: pdf.name
          });
          
          try {
            const formData = new FormData();
            formData.append('file', pdf.file);

            console.log(`Calling local API to extract text from ${pdf.name}...`);
            const response = await fetch(`${LOCAL_API_URL}/extract_pdf`, {
              method: 'POST',
              body: formData
            });

            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.detail || 'Extraction failed');
            }

            const extractData = await response.json();
            
            console.log(`Extracted text from ${pdf.name}: ${extractData.page_count} pages, ${extractData.extracted_text?.length} chars`);
            toast.success(`Extracted ${extractData.page_count} pages from ${pdf.name}`);
            
            allExtractedText += `\n\n=== ${pdf.name} ===\n\n`;
            allExtractedText += extractData.extracted_text || "[No text extracted]";
            
            // Save extracted text to database
            const { error: updateError } = await supabase
              .from('pdf_files')
              .update({ extracted_text: extractData.extracted_text })
              .eq('id', pdfFile.id);

            if (updateError) {
              console.error('Failed to save extracted text:', updateError);
            }
          } catch (err) {
            console.error('PDF extraction error:', err);
            toast.error(`Error extracting ${pdf.name}: ${err.message}`);
            allExtractedText += "\n\n[PDF extraction error]\n\n";
          }
        } catch (err) {
          console.error('PDF upload error:', err);
          toast.error(`Failed to upload ${pdf.name}`);
        }
      }

      // Add extracted text to vector database for chatbot
      if (allExtractedText && allExtractedText.length > 100) {
        setGenerationProgress({ stage: "Indexing content for AI chatbot..." });
        
        try {
          console.log('Adding PDF text to vector database...');
          const vectorResponse = await fetch(`${LOCAL_API_URL}/add_pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              collection_name: `floor_${floor.id}`,
              pdf_text: allExtractedText,
              pdf_filename: pdfFiles.map(p => p.name).join(', '),
              metadata: {
                floor_id: floor.id,
                floor_name: floorName
              }
            })
          });

          if (vectorResponse.ok) {
            const vectorData = await vectorResponse.json();
            console.log(`Indexed ${vectorData.chunks_added} chunks to vector database`);
            toast.success('Content indexed for AI chatbot');
          } else {
            console.error('Failed to index content:', await vectorResponse.text());
          }
        } catch (err) {
          console.error('Vector indexing error:', err);
          // Don't fail the whole process if indexing fails
        }
      }

      // 4. Fetch room objects for selected rooms
      // 5. Fetch room objects for the SINGLE selected room
      setGenerationProgress({ stage: "Fetching room objects..." });
      
      const { data: roomData, error: roomError } = await supabase
        .from('rooms')
        .select('id, name')
        .eq('id', selectedRoom)
        .single();

      if (roomError) {
        throw new Error(`Failed to fetch room: ${roomError.message}`);
      }

      const { data: objects, error: objectsError } = await supabase
        .from('room_objects')
        .select('*')
        .eq('room_id', selectedRoom)
        .order('position');

      if (objectsError) {
        throw new Error(`Failed to fetch objects: ${objectsError.message}`);
      }

      const roomWithObjects = {
        id: roomData.id,
        name: roomData.name,
        objects: objects || []
      };

      console.log('Room with objects:', roomWithObjects);
      console.log('PDF text length:', allExtractedText.length);

      // 6. Generate associations using LOCAL API
      setGenerationProgress({ stage: "Generating memory associations..." });
      
      try {
        // First, generate concepts from the PDF text
        console.log('Generating concepts from PDF text...');
        const conceptsResponse = await fetch(`${LOCAL_API_URL}/generate_concepts`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            pdf_text: allExtractedText,
            num_concepts: 10
          })
        });

        if (!conceptsResponse.ok) {
          const errorData = await conceptsResponse.json();
          throw new Error(errorData.detail || 'Concept generation failed');
        }

        const { concepts } = await conceptsResponse.json();
        console.log(`Generated ${concepts.length} concepts`);

        // Collect room objects
        const allRoomObjects = roomWithObjects.objects.map(obj => ({
          object_name: obj.object_name || obj.name || 'Unnamed Object',
          short_description: obj.short_description || obj.object_description || obj.description || '',
          room_name: roomWithObjects.name
        }));
        console.log(`Using ${allRoomObjects.length} room objects for ${concepts.length} concepts`);

        // Warn if not enough objects
        if (allRoomObjects.length < concepts.length) {
          toast.warning(`Only ${allRoomObjects.length} objects available for ${concepts.length} concepts. Will use top ${allRoomObjects.length} concepts.`);
          console.warn(`Limited objects: ${allRoomObjects.length} objects for ${concepts.length} concepts`);
        }

        // Generate story-based associations (with transitions between rows)
        setGenerationProgress({ stage: "Creating story-based memory associations..." });
        console.log('Generating story-based associations...');
        
        const associationsResponse = await fetch(`${LOCAL_API_URL}/generate_story_associations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            concepts,
            room_objects: allRoomObjects,
            pdf_text: allExtractedText.substring(0, 1500) // Send context for better transitions
          })
        });

        if (!associationsResponse.ok) {
          const errorData = await associationsResponse.json();
          throw new Error(errorData.detail || 'Story association generation failed');
        }

        const { associations } = await associationsResponse.json();
        console.log(`Generated ${associations.length} story-based associations`);
        console.log('Story associations from API:', associations);

        // Save associations to database
        let savedCount = 0;
        for (const assoc of associations) {
          console.log(`Processing association for object: ${assoc.object_name}`);
          
          // Find the matching room object in the single room
          const roomObject = roomWithObjects.objects.find(obj => 
            (obj.object_name || obj.name) === assoc.object_name
          );

          if (!roomObject) {
            console.warn(`No matching object found for: ${assoc.object_name}`);
            continue;
          }

          console.log(`Saving association: Floor ${floor.id}, Room ${roomWithObjects.id}, Object ${roomObject.id}`);
          console.log(`  - Concept: ${assoc.concept}`);
          console.log(`  - Room Object: ${roomObject.object_name || roomObject.name}`);
          
          // Insert floor_room_object association
          const { data: insertedData, error: insertError } = await supabase
            .from('floor_room_objects')
            .insert({
              floor_id: floor.id,
              room_id: roomWithObjects.id,
              room_object_id: roomObject.id,
              concept: assoc.concept,
              concept_description: assoc.concept_description,
              association_text: assoc.association
            })
            .select();

          if (insertError) {
            console.error('Failed to save association:', insertError);
          } else {
            savedCount++;
            console.log(`Successfully saved association ${savedCount}/${associations.length}`);
            console.log('  Inserted record:', insertedData);
          }
        }

        console.log(`Total associations saved: ${savedCount}/${associations.length}`);
        
        if (savedCount === 0) {
          toast.warning('Associations generated but not saved. Check console for details.');
        } else if (savedCount < associations.length) {
          toast.warning(`Only ${savedCount}/${associations.length} associations saved successfully`);
        } else {
          toast.success(`Mind palace generated with ${savedCount} associations!`);
        }
        
        // Update floor status to completed
        const { error: statusError } = await supabase
          .from('floors')
          .update({ status: 'completed' })
          .eq('id', floor.id);

        if (statusError) {
          console.error('Failed to update floor status:', statusError);
        } else {
          console.log('Floor status updated to completed');
        }
      } catch (err) {
        console.error('Association generation error:', err);
        toast.error(`AI generation failed: ${err.message}`);
      }

      navigate(`/floors/${floor.id}`);
    } catch (error) {
      console.error('Generation error:', error);
      toast.error('Failed to generate mind palace');
    } finally {
      setIsGenerating(false);
    }
  };

  const canGenerate = floorName.trim() && selectedRoom !== null && pdfFiles.length > 0;

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/")}
              className="hover:bg-accent"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-glow">
                <Brain className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">Configure Floor</h1>
                <p className="text-sm text-muted-foreground">Set up your mind palace</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        <div className="flex gap-6 h-[calc(100vh-8rem)]">
          {/* Left: Configuration (75%) */}
          <div className="flex-[3] overflow-y-auto pr-4 space-y-8">
            {/* Floor Name */}
            <div className="space-y-3 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <Label htmlFor="floor-name" className="text-lg font-semibold">
                Floor Name
              </Label>
              <Input
                id="floor-name"
                placeholder="e.g., World History, Organic Chemistry..."
                value={floorName}
                onChange={(e) => setFloorName(e.target.value)}
                className="text-lg h-12 bg-card border-border"
              />
            </div>

            {/* Choose Rooms */}
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-lg font-semibold">Choose Room</Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    Select ONE room where concepts will be placed
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowNewRoomModal(true)}
                  className="gap-2 hover:bg-accent"
                >
                  <Plus className="w-4 h-4" />
                  New Room
                </Button>
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                {rooms.length === 0 ? (
                  <p className="text-muted-foreground col-span-full">No rooms yet. Create your first room!</p>
                ) : (
                  rooms.map((room) => (
                    <RoomCard
                      key={room.id}
                      id={room.id}
                      name={room.name}
                      thumbnailUrl={room.thumbnail_url || ""}
                      objectCount={room.object_count}
                      isSelected={selectedRoom === room.id}
                      onToggle={() => handleToggleRoom(room.id)}
                      onDelete={handleDeleteRoom}
                    />
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right: PDF Inputs (25%) */}
          <div className="flex-[1] min-w-[280px]">
            <div className="sticky top-24 bg-card rounded-2xl border border-border shadow-elegant p-6 flex flex-col h-[calc(100vh-12rem)]">
              <h2 className="text-xl font-bold text-foreground mb-4">PDF Inputs</h2>

              <div className="flex-1 overflow-y-auto space-y-3 mb-4">
                {pdfFiles.map((pdf, index) => (
                  <PdfInputTile
                    key={pdf.id}
                    index={index + 1}
                    name={pdf.name}
                    onRemove={() => handleRemovePdf(pdf.id)}
                  />
                ))}

                <label className="block cursor-pointer">
                  <PdfInputTile isAddButton onAdd={() => {}} />
                  <input
                    type="file"
                    multiple
                    accept=".pdf"
                    className="hidden"
                    onChange={handleAddPdfs}
                  />
                </label>
              </div>

              {isGenerating && generationProgress.stage && (
                <div className="mb-4 p-3 bg-muted rounded-lg border border-border animate-pulse">
                  <p className="text-sm font-medium text-foreground">{generationProgress.stage}</p>
                  {generationProgress.currentPdf && (
                    <p className="text-xs text-muted-foreground mt-1">{generationProgress.currentPdf}</p>
                  )}
                </div>
              )}

              <Button
                onClick={handleGenerate}
                disabled={!canGenerate || isGenerating}
                className="w-full bg-gradient-primary hover:opacity-90 text-primary-foreground shadow-glow"
              >
                {isGenerating ? "Generating..." : "Generate Palace"}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <NewRoomModal
        open={showNewRoomModal}
        onOpenChange={setShowNewRoomModal}
        onSave={() => {
          fetchRooms();
        }}
      />
    </div>
  );
};

export default Configure;
