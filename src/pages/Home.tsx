import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Brain, Upload, Plus, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FloorCard } from "@/components/FloorCard";
import { PdfInputTile } from "@/components/PdfInputTile";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

interface PdfFile {
  id: string;
  name: string;
  file: File;
}

interface Floor {
  id: string;
  name: string;
  created_at: string;
  status: string;
  rooms: Array<{
    id: string;
    name: string;
    thumbnail_url: string;
  }>;
}

const Home = () => {
  const navigate = useNavigate();
  const [pdfFiles, setPdfFiles] = useState<PdfFile[]>([]);
  const [floors, setFloors] = useState<Floor[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFloors();
  }, []);

  const fetchFloors = async () => {
    try {
      const { data, error } = await supabase
        .from('floors')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      
      // Fetch rooms for each floor
      const floorsWithRooms = await Promise.all(
        (data || []).map(async (floor) => {
          const { data: floorRooms } = await supabase
            .from('floor_rooms')
            .select(`
              room_id,
              rooms (
                id,
                name,
                thumbnail_url
              )
            `)
            .eq('floor_id', floor.id);

          const rooms = floorRooms
            ?.map(fr => fr.rooms)
            .filter(Boolean)
            .map(room => ({
              id: room.id,
              name: room.name || 'Unnamed Room',
              thumbnail_url: room.thumbnail_url || ''
            })) || [];

          return { ...floor, rooms };
        })
      );

      setFloors(floorsWithRooms);
    } catch (error) {
      console.error('Error fetching floors:', error);
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenRun = (roomId: string) => {
    navigate(`/rooms/${roomId}/table`);
  };

  const handleWalkthroughRun = (roomId: string) => {
    navigate(`/rooms/${roomId}/walkthrough`);
  };

  const handleDeleteFloor = async (floorId: string) => {
    try {
      const { error } = await supabase
        .from('floors')
        .delete()
        .eq('id', floorId);

      if (error) throw error;
      
      toast.success('Floor deleted successfully');
      fetchFloors();
    } catch (error) {
      console.error('Error deleting floor:', error);
      toast.error('Failed to delete floor');
    }
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

  const handleGenerate = () => {
    navigate("/configure", { state: { pdfFiles } });
  };

  const handleAddRoom = (floorName: string) => {
    // Open file picker for PDFs
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.pdf';
    
    input.onchange = (e: Event) => {
      const target = e.target as HTMLInputElement;
      const files = Array.from(target.files || []);
      
      if (files.length === 0) return;
      
      const newPdfs: PdfFile[] = files.map((file) => ({
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        file,
      }));
      
      // Navigate to Configure page with floor name pre-filled
      navigate("/configure", { 
        state: { 
          pdfFiles: newPdfs,
          floorName: floorName  // Pre-fill floor name
        } 
      });
    };
    
    input.click();
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-glow">
              <Brain className="w-6 h-6 text-primary-foreground" />
            </div>
            <h1 className="text-2xl font-bold text-foreground">MindPalace</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        <div className="flex gap-6 h-[calc(100vh-8rem)]">
          {/* Left: History (75%) */}
          <div className="flex-[3] overflow-y-auto pr-4 space-y-1">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold text-foreground">History</h2>
            </div>

            {/* History Section */}
            <div className="bg-card rounded-2xl border border-border shadow-elegant p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-2">
                <BookOpen className="w-6 h-6 text-primary" />
                History
              </h2>

              <div className="space-y-6">
                {loading ? (
                  <p className="text-muted-foreground">Loading...</p>
                ) : floors.length === 0 ? (
                  <p className="text-muted-foreground">No floors created yet. Upload PDFs to get started!</p>
                ) : (
                  floors.map((floor) => (
                    <FloorCard
                      key={floor.id}
                      floorId={floor.id}
                      floorName={floor.name}
                      rooms={floor.rooms}
                      onOpenRoom={handleOpenRun}
                      onWalkthroughRoom={handleWalkthroughRun}
                      onDelete={handleDeleteFloor}
                      onAddRoom={handleAddRoom}
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

              <Button
                onClick={handleGenerate}
                disabled={pdfFiles.length === 0}
                className="w-full bg-gradient-primary hover:opacity-90 text-primary-foreground shadow-glow"
              >
                Choose Room --&gt;
                <Plus className="ml-2 w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
