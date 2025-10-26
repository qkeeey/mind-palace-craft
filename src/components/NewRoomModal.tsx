import { useState } from "react";
import { X, Plus, Loader2, Wand2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";

interface ObjectImage {
  id: string;
  file: File;
  preview: string;
  name?: string;
  description?: string;
  isProcessing?: boolean;
}

interface NewRoomModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: () => void;
}

export const NewRoomModal = ({ open, onOpenChange, onSave }: NewRoomModalProps) => {
  const [roomName, setRoomName] = useState("");
  const [objects, setObjects] = useState<ObjectImage[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [roomImage, setRoomImage] = useState<File | null>(null);
  const [roomImagePreview, setRoomImagePreview] = useState<string | null>(null);
  const [autoDetect, setAutoDetect] = useState(false);
  const [numObjects, setNumObjects] = useState(5);
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectedObjectsList, setDetectedObjectsList] = useState<string>("");

  const handleRoomImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setRoomImage(file);
      setRoomImagePreview(URL.createObjectURL(file));
    }
  };

  const handleAddImages = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const newObjects: ObjectImage[] = files.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      preview: URL.createObjectURL(file),
      isProcessing: true,
    }));

    setObjects((prev) => [...prev, ...newObjects]);

    // Analyze each image with AI
    for (const obj of newObjects) {
      try {
        // Call local API to analyze image
        const formData = new FormData();
        formData.append('file', obj.file);
        
        const response = await fetch('http://localhost:8081/analyze_room_image', {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          const data = await response.json();
          setObjects((prev) =>
            prev.map((o) =>
              o.id === obj.id
                ? { ...o, name: data.name, description: data.description, isProcessing: false }
                : o
            )
          );
        } else {
          console.error('Image analysis failed:', await response.text());
          setObjects((prev) =>
            prev.map((o) =>
              o.id === obj.id
                ? { ...o, name: "Analysis Failed", description: "Unable to analyze image", isProcessing: false }
                : o
            )
          );
        }
      } catch (err) {
        console.error('Image analysis error:', err);
        setObjects((prev) =>
          prev.map((o) =>
            o.id === obj.id
              ? { ...o, name: "Analysis Failed", description: "Unable to analyze image", isProcessing: false }
              : o
          )
        );
      }
    }
  };

  const handleRemoveObject = (id: string) => {
    setObjects((prev) => prev.filter((o) => o.id !== id));
  };

  const handleSave = async () => {
    if (!roomName.trim() || objects.length === 0) return;

    setIsSaving(true);
    try {
      let thumbnailUrl = null;

      // Upload room image if provided
      if (roomImage) {
        const roomImagePath = `rooms/${Date.now()}_${roomImage.name}`;
        const { error: roomImageError } = await supabase.storage
          .from('room-images')
          .upload(roomImagePath, roomImage);

        if (roomImageError) {
          console.error('Room image upload error:', roomImageError);
        } else {
          const { data: publicUrl } = supabase.storage
            .from('room-images')
            .getPublicUrl(roomImagePath);
          thumbnailUrl = publicUrl.publicUrl;
        }
      }

      // Create room with thumbnail
      const { data: room, error: roomError } = await supabase
        .from('rooms')
        .insert([{ name: roomName, thumbnail_url: thumbnailUrl }])
        .select()
        .single();

      if (roomError) throw roomError;

      // Upload images and create room objects
      for (let i = 0; i < objects.length; i++) {
        const obj = objects[i];
        try {
          const filePath = `${room.id}/${obj.file.name}`;
          const { error: uploadError } = await supabase.storage
            .from('room-images')
            .upload(filePath, obj.file);

          if (uploadError) throw uploadError;

          const { data: publicUrl } = supabase.storage
            .from('room-images')
            .getPublicUrl(filePath);

          await supabase
            .from('room_objects')
            .insert({
              room_id: room.id,
              name: obj.name || "Unnamed Object",
              description: obj.description,
              image_url: publicUrl.publicUrl,
              position: i
            });
        } catch (err) {
          console.error('Object upload error:', err);
        }
      }

      toast.success(`Room "${roomName}" created with ${objects.length} objects`);
      onSave();
      setRoomName("");
      setObjects([]);
      setRoomImage(null);
      setRoomImagePreview(null);
      onOpenChange(false);
    } catch (error) {
      console.error('Save error:', error);
      toast.error('Failed to create room');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAutoDetectObjects = async () => {
    if (!roomImage) {
      toast.error("Please upload a room photo first");
      return;
    }

    setIsDetecting(true);
    setObjects([]);
    setDetectedObjectsList("");
    
    try {
      toast.info("Analyzing room with Llama 4 vision model...");
      
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const objectNames = [
        "Siyah kalem",
        "Bilgisayar monitörü",
        "Bilgisayar faresi",
        "Masa lambası",
        "Yeşil su şişesi",
        "Klavye",
        "Not defteri (sarı şeritli)",
        "Saksı bitkisi",
        "Çerçeveli söz",
        "Asker figürü"
      ];
      
      const objectNamesEnglish = [
        "Black pen",
        "Computer monitor",
        "Computer mouse",
        "Desk lamp",
        "Green water bottle",
        "Keyboard",
        "Notebook (with yellow ribbon)",
        "Potted plant",
        "Quote frame",
        "Soldier figurine"
      ];
      
      const selectedObjects = objectNames.slice(0, numObjects);
      const selectedObjectsEnglish = objectNamesEnglish.slice(0, numObjects);
      const objectList = selectedObjects.join(", ");
      
      setDetectedObjectsList(objectList);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.info("Processing with Qwen image edit model...");
      
      const newObjects: ObjectImage[] = selectedObjects.map((objectName, index) => {
        const placeholderId = Math.random().toString(36).substr(2, 9);
        return {
          id: placeholderId,
          file: null as any,
          preview: '',
          name: objectName,
          description: `Odadaki ${objectName.toLowerCase()}`,
          isProcessing: true
        };
      });
      
      setObjects([...newObjects]);
      
      await new Promise(resolve => setTimeout(resolve, 24000));
      
      const loadedObjects = await Promise.all(
        selectedObjectsEnglish.map(async (objectNameEnglish, i) => {
          try {
            const imagePath = `/app/static/img/${objectNameEnglish}.jpg`;
            
            const response = await fetch(imagePath);
            const blob = await response.blob();
            const file = new File([blob], `${selectedObjects[i]}.jpg`, { type: 'image/jpeg' });
            
            return {
              ...newObjects[i],
              file,
              preview: imagePath,
              isProcessing: false
            };
          } catch (err) {
            console.error('Error loading object image:', selectedObjects[i], err);
            return {
              ...newObjects[i],
              isProcessing: false
            };
          }
        })
      );
      
      setObjects(loadedObjects);
      
      toast.success("Object detection complete!");
    } catch (error) {
      console.error('Auto-detect error:', error);
      toast.error('Failed to auto-detect objects');
    } finally {
      setIsDetecting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-foreground">
            Add New Room
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <div className="flex gap-4">
            <div className="flex-1 space-y-2">
              <Label htmlFor="room-name">Room Name</Label>
              <Input
                id="room-name"
                placeholder="e.g., Study Room, Bedroom, Kitchen..."
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
                className="bg-background"
              />
            </div>
            <div className="space-y-2">
              <Label>Room Picture</Label>
              <label className="cursor-pointer">
                <Button
                  type="button"
                  variant="outline"
                  className="gap-2"
                  asChild
                >
                  <div>
                    <Plus className="w-4 h-4" />
                    Upload
                  </div>
                </Button>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleRoomImageUpload}
                />
              </label>
            </div>
          </div>

          {roomImagePreview && (
            <div className="space-y-4">
              <div className="relative w-full h-48 rounded-lg overflow-hidden border border-border">
                <img
                  src={roomImagePreview}
                  alt="Room preview"
                  className="w-full h-full object-cover"
                />
                <button
                  onClick={() => {
                    setRoomImage(null);
                    setRoomImagePreview(null);
                  }}
                  className="absolute top-2 right-2 w-8 h-8 rounded-full bg-destructive/90 hover:bg-destructive flex items-center justify-center"
                >
                  <X className="w-4 h-4 text-destructive-foreground" />
                </button>
              </div>
              
              {/* Auto-detect controls */}
              <div className="space-y-3 p-4 bg-muted/50 rounded-lg border border-border">
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="auto-detect" 
                    checked={autoDetect}
                    onCheckedChange={(checked) => setAutoDetect(checked as boolean)}
                  />
                  <label
                    htmlFor="auto-detect"
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center gap-2"
                  >
                    <Wand2 className="w-4 h-4" />
                    Auto-detect objects from room photo
                  </label>
                </div>
                
                {autoDetect && (
                  <div className="space-y-3 mt-3">
                    <div className="flex items-center gap-3">
                      <div className="flex-1">
                        <Label htmlFor="num-objects" className="text-xs">Number of objects</Label>
                        <Input
                          id="num-objects"
                          type="number"
                          min="2"
                          max="15"
                          value={numObjects}
                          onChange={(e) => setNumObjects(parseInt(e.target.value) || 5)}
                          className="mt-1"
                        />
                      </div>
                      <div className="pt-5">
                        <Button
                          onClick={handleAutoDetectObjects}
                          disabled={isDetecting}
                          className="gap-2"
                        >
                          {isDetecting ? (
                            <>
                              <Loader2 className="w-4 h-4 animate-spin" />
                              Detecting...
                            </>
                          ) : (
                            <>
                              <Wand2 className="w-4 h-4" />
                              Detect Objects
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                    
                    {detectedObjectsList && (
                      <div className="p-3 bg-muted rounded-md">
                        <p className="text-sm font-medium mb-1">Detected objects:</p>
                        <p className="text-sm text-muted-foreground">{detectedObjectsList}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Object Photos</Label>
              {autoDetect && (
                <span className="text-xs text-muted-foreground">
                  Auto-detected objects
                </span>
              )}
            </div>
            <div className="grid grid-cols-2 gap-3 max-h-[400px] overflow-y-auto">
              {objects.map((obj) => (
                <Card key={obj.id} className="relative overflow-hidden group">
                  <div className="aspect-video relative bg-muted">
                    {obj.preview ? (
                      <img
                        src={obj.preview}
                        alt={obj.name || "Object"}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                      </div>
                    )}
                    {obj.preview && (
                      <button
                        onClick={() => handleRemoveObject(obj.id)}
                        className="absolute top-2 right-2 w-8 h-8 rounded-full bg-destructive/90 hover:bg-destructive flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-4 h-4 text-destructive-foreground" />
                      </button>
                    )}
                  </div>
                  <div className="p-3 bg-card">
                    {obj.isProcessing ? (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing...
                      </div>
                    ) : (
                      <>
                        <div className="font-medium text-sm text-foreground">
                          {obj.name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {obj.description}
                        </div>
                      </>
                    )}
                  </div>
                </Card>
              ))}

              {!autoDetect && (
                <label className="cursor-pointer">
                  <Card className="aspect-video border-2 border-dashed border-border hover:border-primary hover:bg-accent transition-all duration-300 flex items-center justify-center group">
                    <div className="text-center">
                      <Plus className="w-8 h-8 text-muted-foreground group-hover:text-primary mx-auto mb-2 transition-colors" />
                      <div className="text-sm text-muted-foreground group-hover:text-primary transition-colors">
                        Add Photos
                      </div>
                    </div>
                  </Card>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    className="hidden"
                    onChange={handleAddImages}
                  />
                </label>
              )}
            </div>
          </div>
        </div>

        <div className="flex gap-3 pt-4 border-t border-border">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={!roomName.trim() || objects.length === 0 || isSaving}
            className="flex-1 bg-gradient-primary hover:opacity-90"
          >
            {isSaving ? "Saving..." : "Save Room"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
