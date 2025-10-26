import { FileText, Plus, X } from "lucide-react";
import { Card } from "@/components/ui/card";

interface PdfInputTileProps {
  index?: number;
  name?: string;
  onRemove?: () => void;
  isAddButton?: boolean;
  onAdd?: () => void;
}

export const PdfInputTile = ({ index, name, onRemove, isAddButton, onAdd }: PdfInputTileProps) => {
  if (isAddButton) {
    return (
      <Card
        onClick={onAdd}
        className="p-4 bg-secondary hover:bg-accent border-2 border-dashed border-border hover:border-primary cursor-pointer transition-all duration-300 group"
      >
        <div className="flex items-center justify-center h-12">
          <Plus className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 bg-card border-border hover:shadow-card transition-all duration-300 group">
      <div className="flex items-center gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
          <FileText className="w-4 h-4 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs text-muted-foreground">PDF {index}</div>
          <div className="text-sm text-foreground truncate">{name}</div>
        </div>
        {onRemove && (
          <button
            onClick={onRemove}
            className="flex-shrink-0 w-6 h-6 rounded-md hover:bg-destructive/10 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <X className="w-4 h-4 text-destructive" />
          </button>
        )}
      </div>
    </Card>
  );
};
