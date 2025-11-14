import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Download, Eye } from 'lucide-react';

interface Note {
  id: string;
  title: string;
  subject: string;
  department: string;
  downloadCount: number;
  viewCount: number;
}

interface PopularNotesTableProps {
  notes: Note[];
}

export function PopularNotesTable({ notes }: PopularNotesTableProps) {
  return (
    <Card data-testid="popular-notes-table">
      <CardHeader>
        <CardTitle>Popular Notes</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title</TableHead>
              <TableHead>Subject</TableHead>
              <TableHead>Department</TableHead>
              <TableHead className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Download className="h-4 w-4" />
                  Downloads
                </div>
              </TableHead>
              <TableHead className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Eye className="h-4 w-4" />
                  Views
                </div>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {notes.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-muted-foreground">
                  No notes available
                </TableCell>
              </TableRow>
            ) : (
              notes.map((note) => (
                <TableRow key={note.id} data-testid={`note-row-${note.id}`}>
                  <TableCell className="font-medium">{note.title}</TableCell>
                  <TableCell>{note.subject}</TableCell>
                  <TableCell>{note.department}</TableCell>
                  <TableCell className="text-right">{note.downloadCount}</TableCell>
                  <TableCell className="text-right">{note.viewCount}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
