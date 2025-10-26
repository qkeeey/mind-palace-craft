import { Brain, X, Plus } from "lucide-react";
import { Card } from "@/components/ui/card";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";

interface Room {
  id: string;
  name: string;
  thumbnail_url: string;
}

interface FloorCardProps {
  floorName: string;
  floorId: string;
  rooms: Room[];
  onOpenRoom: (roomId: string) => void;
  onWalkthroughRoom: (roomId: string) => void;
  onDelete: (floorId: string) => void;
  onAddRoom?: (floorName: string) => void;
}

export const FloorCard = ({ floorName, floorId, rooms, onOpenRoom, onWalkthroughRoom, onDelete, onAddRoom }: FloorCardProps) => {
  return (
    <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary" />
          {floorName}
        </h3>
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 hover:bg-destructive/10 hover:text-destructive"
            >
              <X className="w-4 h-4" />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Floor</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete "{floorName}"? This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => onDelete(floorId)}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
      
      {/* Horizontally scrollable rooms */}
      <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-primary/20 scrollbar-track-transparent">
        {rooms.length === 0 ? (
          <p className="text-muted-foreground text-sm">No rooms created yet</p>
        ) : (
          rooms.map((room) => (
            <div
              key={room.id}
              className="flex-shrink-0 w-[280px] h-[280px]"
              style={{ minWidth: '280px', maxWidth: '280px', minHeight: '280px', maxHeight: '280px' }}
            >
              <Card className="w-full h-full relative overflow-hidden bg-card hover:shadow-elegant transition-all duration-300 hover:-translate-y-1 border-border">
                {/* Room Image - Full Container */}
                <img
                  src={room.thumbnail_url}
                  alt={room.name}
                  className="absolute inset-0 w-full h-full object-cover"
                />
                
                {/* Buttons Overlaid at Bottom */}
                <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 via-black/60 to-transparent">
                  <div className="flex gap-2">
                    <button
                      onClick={() => onOpenRoom(room.id)}
                      className="flex-1 px-3 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors shadow-lg"
                    >
                      Open
                    </button>
                    <button
                      onClick={() => onWalkthroughRoom(room.id)}
                      className="flex-1 px-3 py-2 text-sm font-medium bg-accent text-accent-foreground rounded-md hover:bg-accent/90 transition-colors shadow-lg"
                    >
                      Walkthrough
                    </button>
                  </div>
                </div>
              </Card>
            </div>
          ))
        )}
        
        {/* Add Room Button */}
        {onAddRoom && (
          <div
            className="flex-shrink-0 w-[280px] h-[280px]"
            style={{ minWidth: '280px', maxWidth: '280px', minHeight: '280px', maxHeight: '280px' }}
          >
            <button
              onClick={() => onAddRoom(floorName)}
              className="w-full h-full border-2 border-dashed border-primary/30 rounded-lg hover:border-primary hover:bg-primary/5 transition-all duration-300 flex flex-col items-center justify-center gap-3 group"
            >
              <div className="w-16 h-16 rounded-full bg-primary/10 group-hover:bg-primary/20 flex items-center justify-center transition-colors">
                <Plus className="w-8 h-8 text-primary" />
              </div>
              <span className="text-sm font-medium text-primary">Add Room</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
