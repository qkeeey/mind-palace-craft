import { Check, X } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";

interface RoomCardProps {
  id: string;
  name: string;
  thumbnailUrl?: string;
  objectCount: number;
  isSelected: boolean;
  onToggle: () => void;
  onDelete?: (id: string) => void;
}

export const RoomCard = ({
  id,
  name,
  thumbnailUrl,
  objectCount,
  isSelected,
  onToggle,
  onDelete,
}: RoomCardProps) => {
  return (
    <Card
      className={cn(
        "relative overflow-hidden transition-all duration-300 hover:shadow-elegant hover:-translate-y-1",
        isSelected
          ? "ring-2 ring-primary shadow-glow"
          : "border-border hover:border-primary/50"
      )}
    >
      {onDelete && (
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 z-10 h-6 w-6 bg-background/80 hover:bg-destructive/10 hover:text-destructive backdrop-blur-sm"
              onClick={(e) => e.stopPropagation()}
            >
              <X className="w-3 h-3" />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Room</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete "{name}"? This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => onDelete(id)}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
      <div className="aspect-video bg-muted relative overflow-hidden cursor-pointer" onClick={onToggle}>
        {thumbnailUrl ? (
          <img
            src={thumbnailUrl}
            alt={name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-subtle">
            <div className="text-4xl text-primary/20">🏠</div>
          </div>
        )}
        {isSelected && (
          <div className="absolute inset-0 bg-primary/20 flex items-center justify-center">
            <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center shadow-glow">
              <Check className="w-6 h-6 text-primary-foreground" />
            </div>
          </div>
        )}
      </div>
      <div className="p-4 cursor-pointer" onClick={onToggle}>
        <h4 className="font-semibold text-foreground mb-1">{name}</h4>
        <p className="text-sm text-muted-foreground">
          {objectCount} {objectCount === 1 ? "object" : "objects"}
        </p>
      </div>
    </Card>
  );
};
