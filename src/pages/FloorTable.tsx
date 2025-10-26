import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Brain, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { Chatbot } from "@/components/Chatbot";

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

interface RoomImage {
  id: string;
  name: string;
  thumbnail_url: string | null;
}

const FloorTable = () => {
  const { floorId, roomId } = useParams();
  const navigate = useNavigate();
  const [floorName, setFloorName] = useState("");
  const [roomName, setRoomName] = useState("");
  const [associations, setAssociations] = useState<Association[]>([]);
  const [roomImages, setRoomImages] = useState<RoomImage[]>([]);
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

      // Fetch floor info
      if (currentFloorId) {
        const { data: floor, error: floorError } = await supabase
          .from('floors')
          .select('name, status')
          .eq('id', currentFloorId)
          .single();

        if (floorError) throw floorError;
        setFloorName(floor.name);
      }

      // Fetch rooms associated with this floor
      if (currentFloorId) {
        let roomsQuery = supabase
          .from('floor_rooms')
          .select(`
            room_id,
            rooms (
              id,
              name,
              thumbnail_url
            )
          `)
          .eq('floor_id', currentFloorId);

        // If viewing a specific room, filter to show only that room's image
        if (currentRoomId) {
          roomsQuery = roomsQuery.eq('room_id', currentRoomId);
        }

        const { data: floorRooms, error: roomsError } = await roomsQuery;

        if (!roomsError && floorRooms) {
          const rooms = floorRooms
            .map(fr => fr.rooms)
            .filter(Boolean) as RoomImage[];
          setRoomImages(rooms);
        }
      }

      // Query floor_room_objects - MUST filter by BOTH floor_id AND room_id
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
        console.log(`Filtering associations by floor_id: ${currentFloorId} AND room_id: ${currentRoomId}`);
      } else if (currentFloorId) {
        // Filter by floor if no specific room
        query = query.eq('floor_id', currentFloorId);
        console.log(`Filtering associations by floor_id: ${currentFloorId}`);
      } else if (currentRoomId) {
        // This shouldn't happen, but just in case
        query = query.eq('room_id', currentRoomId);
        console.log(`WARNING: Filtering only by room_id: ${currentRoomId} (might show cross-floor data)`);
      }

      const { data: assocData, error: assocError } = await query.order('created_at');

      if (assocError) {
        console.error('Error fetching associations:', assocError);
        throw assocError;
      }
      
      console.log('=== FLOOR TABLE DEBUG ===');
      console.log('Current Room ID:', currentRoomId);
      console.log('Current Floor ID:', currentFloorId);
      console.log('Fetched associations count:', assocData?.length);
      console.log('Fetched associations:', assocData);
      console.log('First association:', assocData?.[0]);
      console.log('========================');
      setAssociations(assocData || []);
    } catch (error) {
      console.error('Error fetching floor data:', error);
      toast.error('Failed to load floor data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
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
                  <h1 className="text-2xl font-bold text-foreground">
                    {roomName ? `${floorName} - ${roomName}` : (floorName || "Loading...")}
                  </h1>
                  <p className="text-sm text-muted-foreground">
                    {associations.length} concepts
                  </p>
                </div>
              </div>
            </div>

            <Button
              onClick={() => {
                if (roomId) {
                  navigate(`/rooms/${roomId}/walkthrough`);
                } else {
                  navigate(`/floors/${floorId}/walkthrough`);
                }
              }}
              className="bg-gradient-accent hover:opacity-90 text-accent-foreground gap-2"
            >
              <Eye className="w-4 h-4" />
              Walkthrough
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Table Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Room Pictures */}
            {roomImages.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {roomImages.map((room) => (
                  <div key={room.id} className="relative rounded-xl overflow-hidden border border-border shadow-elegant">
                    <div className="aspect-video bg-muted">
                      {room.thumbnail_url ? (
                        <img
                          src={room.thumbnail_url}
                          alt={room.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gradient-subtle">
                          <div className="text-4xl text-primary/20">🏠</div>
                        </div>
                      )}
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
                      <p className="text-white font-medium text-sm">{room.name}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Table */}
            <div className="bg-card rounded-2xl border border-border shadow-elegant overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="bg-muted/50">
                    <TableHead className="w-[250px]">Object</TableHead>
                    <TableHead className="w-[200px]">Core Concept</TableHead>
                    <TableHead>Mnemonic Association</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={3} className="text-center text-muted-foreground">
                        Loading...
                      </TableCell>
                    </TableRow>
                  ) : associations.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} className="text-center text-muted-foreground">
                        No associations generated yet.
                      </TableCell>
                    </TableRow>
                  ) : (
                    associations.map((assoc, index) => (
                      <TableRow
                        key={assoc.id}
                        className="animate-in fade-in slide-in-from-bottom-2"
                        style={{ animationDelay: `${index * 100}ms` }}
                      >
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="w-48 h-48 rounded-lg bg-muted overflow-hidden">
                              {assoc.room_objects?.image_url ? (
                                <img 
                                  src={assoc.room_objects.image_url} 
                                  alt={assoc.room_objects.object_name || assoc.room_objects.name || "Object"}
                                  className="w-full h-full object-cover"
                                  onError={(e) => {
                                    console.error('Image failed to load:', assoc.room_objects?.image_url);
                                    e.currentTarget.style.display = 'none';
                                  }}
                                />
                              ) : (
                                <div className="w-full h-full flex items-center justify-center text-2xl">📚</div>
                              )}
                            </div>
                            <div className="font-medium">
                              {assoc.room_objects?.object_name || assoc.room_objects?.name || "Unknown"}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="font-semibold text-primary">
                          {assoc.concept}
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {assoc.association_text}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Chatbot Section */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <Chatbot floorId={floorId || ""} className="h-[600px]" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FloorTable;
