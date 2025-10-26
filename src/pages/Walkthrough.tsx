import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, ChevronLeft, ChevronRight, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Chatbot } from "@/components/Chatbot";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

interface Association {
  id: string;
  concept: string;
  concept_description: string;
  association_text: string;
  room_object_id: string;
  room_objects: {
    id: string;
    name: string;
    object_name: string | null;
    image_url: string | null;
  } | null;
}

const Walkthrough = () => {
  const { floorId, roomId } = useParams();
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [floorName, setFloorName] = useState("");
  const [roomName, setRoomName] = useState("");
  const [associations, setAssociations] = useState<Association[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (floorId || roomId) {
      fetchFloorData();
    }
  }, [floorId, roomId]);

  const fetchFloorData = async () => {
    try {
      let currentFloorId = floorId;
      let currentRoomId = roomId;

      // If we have roomId, fetch the room and its floor
      if (roomId) {
        const { data: room, error: roomError } = await supabase
          .from('rooms')
          .select('id, name, floor_rooms(floor_id)')
          .eq('id', roomId)
          .single();

        if (roomError) throw roomError;
        
        setRoomName(room.name);
        currentRoomId = room.id;
        
        // Get floor_id from floor_rooms relationship
        if (room.floor_rooms && room.floor_rooms.length > 0) {
          currentFloorId = room.floor_rooms[0].floor_id;
        }
      }

      // Fetch floor name
      if (currentFloorId) {
        const { data: floor, error: floorError } = await supabase
          .from('floors')
          .select('name')
          .eq('id', currentFloorId)
          .single();

        if (floorError) throw floorError;
        setFloorName(floor.name);
      }

      // Fetch associations - MUST filter by BOTH floor_id AND room_id
      let query = supabase
        .from('floor_room_objects')
        .select(`
          id,
          concept,
          concept_description,
          association_text,
          room_object_id,
          room_id,
          floor_id,
          room_objects (
            id,
            name,
            object_name,
            image_url,
            room_id
          )
        `);

      // CRITICAL: Filter by BOTH floor_id AND room_id to avoid cross-contamination
      if (currentRoomId && currentFloorId) {
        query = query
          .eq('floor_id', currentFloorId)
          .eq('room_id', currentRoomId);
        console.log(`Walkthrough: Filtering by floor_id: ${currentFloorId} AND room_id: ${currentRoomId}`);
      } else if (currentFloorId) {
        // Filter by floor if no specific room
        query = query.eq('floor_id', currentFloorId);
        console.log(`Walkthrough: Filtering by floor_id: ${currentFloorId}`);
      } else if (currentRoomId) {
        // This shouldn't happen, but just in case
        query = query.eq('room_id', currentRoomId);
        console.log(`Walkthrough WARNING: Filtering only by room_id: ${currentRoomId}`);
      }

      const { data: assocData, error: assocError } = await query.order('created_at');

      if (assocError) {
        console.error('Error fetching associations:', assocError);
        throw assocError;
      }

      console.log('Walkthrough: Fetched associations:', assocData?.length);
      console.log('First association:', assocData?.[0]);
      console.log('First room_objects:', assocData?.[0]?.room_objects);
      setAssociations(assocData || []);
    } catch (error) {
      console.error('Error fetching floor data:', error);
      toast.error('Failed to load walkthrough data');
    } finally {
      setLoading(false);
    }
  };

  const currentAssociation = associations[currentIndex];
  const isFirst = currentIndex === 0;
  const isLast = currentIndex === associations.length - 1;

  const handlePrevious = () => {
    if (!isFirst) setCurrentIndex((prev) => prev - 1);
  };

  const handleNext = () => {
    if (!isLast) setCurrentIndex((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-subtle flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-lg font-semibold text-foreground">
              {roomName ? `${floorName} - ${roomName}` : (floorName || "Loading...")}
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                if (roomId) {
                  navigate(`/rooms/${roomId}/table`);
                } else {
                  navigate(`/floors/${floorId}`);
                }
              }}
              className="hover:bg-accent"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-4xl">
          {loading ? (
            <Card className="p-12 shadow-elegant border-border">
              <div className="text-center text-muted-foreground">
                Loading walkthrough...
              </div>
            </Card>
          ) : associations.length === 0 ? (
            <Card className="p-12 shadow-elegant border-border">
              <div className="text-center text-muted-foreground">
                No associations found. Please generate a mind palace first.
              </div>
            </Card>
          ) : (
            <>
              <Card className="p-12 shadow-elegant border-border animate-in fade-in zoom-in-95 duration-500">
                {/* Object Image */}
                <div className="mb-8 flex justify-center">
                  <div className="w-64 h-64 rounded-2xl bg-muted flex items-center justify-center overflow-hidden shadow-card">
                    {currentAssociation.room_objects?.image_url ? (
                      <img 
                        src={currentAssociation.room_objects.image_url} 
                        alt={currentAssociation.room_objects.object_name || currentAssociation.room_objects.name || "Object"}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          console.error('Image failed to load:', currentAssociation.room_objects?.image_url);
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    ) : (
                      <div className="text-8xl">📚</div>
                    )}
                  </div>
                </div>

                {/* Object Name */}
                <h2 className="text-3xl font-bold text-center text-foreground mb-2">
                  {currentAssociation.room_objects?.object_name || currentAssociation.room_objects?.name || "Unknown Object"}
                </h2>

                {/* Concept */}
                <h3 className="text-2xl font-semibold text-center text-primary mb-6">
                  {currentAssociation.concept}
                </h3>

                {/* Mnemonic */}
                <p className="text-lg text-center text-muted-foreground leading-relaxed max-w-2xl mx-auto">
                  {currentAssociation.association_text}
                </p>
              </Card>

              {/* Navigation */}
              <div className="flex items-center justify-between mt-8">
                <Button
                  variant="outline"
                  size="lg"
                  onClick={handlePrevious}
                  disabled={isFirst}
                  className="gap-2 hover:bg-accent"
                >
                  <ChevronLeft className="w-5 h-5" />
                  Previous
                </Button>

                <div className="text-muted-foreground">
                  {currentIndex + 1} / {associations.length}
                </div>

                <Button
                  variant="outline"
                  size="lg"
                  onClick={handleNext}
                  disabled={isLast}
                  className="gap-2 hover:bg-accent"
                >
                  Next
                  <ChevronRight className="w-5 h-5" />
                </Button>
              </div>
            </>
          )}

          {/* Chatbot Section */}
          <div className="mt-8">
            <Chatbot floorId={floorId || ""} className="h-[500px]" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Walkthrough;
