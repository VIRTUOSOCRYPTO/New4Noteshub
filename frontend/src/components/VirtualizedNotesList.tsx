/**
 * Virtualized Notes List
 * Uses virtual scrolling for better performance with large lists
 */

import { useRef, useMemo } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Card, CardContent } from '@/components/ui/card';
import { Download, Eye, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Note {
  id: string;
  title: string;
  subject: string;
  department: string;
  year: number;
  downloadCount: number;
  viewCount: number;
  uploadedAt: string;
}

interface VirtualizedNotesListProps {
  notes: Note[];
  onDownload?: (note: Note) => void;
  onView?: (note: Note) => void;
}

export function VirtualizedNotesList({
  notes,
  onDownload,
  onView
}: VirtualizedNotesListProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  // Initialize virtualizer
  const rowVirtualizer = useVirtualizer({
    count: notes.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120, // Estimated height of each item
    overscan: 5 // Number of items to render outside visible area
  });

  const virtualItems = rowVirtualizer.getVirtualItems();

  if (notes.length === 0) {
    return (
      <div className=\"text-center py-12 text-muted-foreground\">
        <FileText className=\"h-12 w-12 mx-auto mb-4 opacity-50\" />
        <p>No notes found</p>
      </div>
    );
  }

  return (
    <div
      ref={parentRef}
      className=\"h-[600px] overflow-auto border rounded-lg\"
      data-testid=\"virtualized-notes-list\"
    >
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative'
        }}
      >
        {virtualItems.map((virtualItem) => {
          const note = notes[virtualItem.index];
          
          return (
            <div
              key={note.id}
              data-testid={`note-item-${note.id}`}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`
              }}
            >
              <Card className=\"mx-4 my-2\">
                <CardContent className=\"p-4\">
                  <div className=\"flex items-start justify-between\">
                    <div className=\"flex-1\">
                      <h3 className=\"font-semibold text-lg mb-1\" data-testid=\"note-title\">
                        {note.title}
                      </h3>
                      <div className=\"flex items-center gap-4 text-sm text-muted-foreground mb-2\">
                        <span data-testid=\"note-subject\">{note.subject}</span>
                        <span>•</span>
                        <span data-testid=\"note-department\">{note.department}</span>
                        <span>•</span>
                        <span>Year {note.year}</span>
                      </div>
                      <div className=\"flex items-center gap-4 text-sm\">
                        <div className=\"flex items-center gap-1\">
                          <Download className=\"h-4 w-4\" />
                          <span data-testid=\"note-downloads\">{note.downloadCount}</span>
                        </div>
                        <div className=\"flex items-center gap-1\">
                          <Eye className=\"h-4 w-4\" />
                          <span data-testid=\"note-views\">{note.viewCount}</span>
                        </div>
                      </div>
                    </div>
                    <div className=\"flex gap-2\">
                      {onView && (
                        <Button
                          size=\"sm\"
                          variant=\"outline\"
                          onClick={() => onView(note)}
                          data-testid=\"view-button\"
                        >
                          View
                        </Button>
                      )}
                      {onDownload && (
                        <Button
                          size=\"sm\"
                          onClick={() => onDownload(note)}
                          data-testid=\"download-button\"
                        >
                          Download
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          );
        })}
      </div>
    </div>
  );
}
