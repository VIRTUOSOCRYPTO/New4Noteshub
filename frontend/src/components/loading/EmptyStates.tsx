import { FileQuestion, Search, Upload, AlertCircle, Inbox } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
}

/**
 * Generic empty state component
 */
export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <Card className="w-full">
      <CardContent className="flex flex-col items-center justify-center py-12 px-6 text-center">
        <div className="mb-4 text-muted-foreground">
          {icon || <Inbox className="h-16 w-16" />}
        </div>
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-muted-foreground mb-6 max-w-md">{description}</p>
        {action && (
          <Button onClick={action.onClick} size="lg">
            {action.label}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

/**
 * Empty state for no notes found
 */
export function NoNotesFound({ onUpload }: { onUpload?: () => void }) {
  return (
    <EmptyState
      icon={<FileQuestion className="h-16 w-16" />}
      title="No notes found"
      description="We couldn't find any notes matching your criteria. Try adjusting your filters or be the first to upload!"
      action={
        onUpload
          ? {
              label: "Upload Note",
              onClick: onUpload,
            }
          : undefined
      }
    />
  )
}

/**
 * Empty state for no search results
 */
export function NoSearchResults({ query, onClear }: { query: string; onClear?: () => void }) {
  return (
    <EmptyState
      icon={<Search className="h-16 w-16" />}
      title="No results found"
      description={`We couldn't find any notes matching "${query}". Try different keywords or check your spelling.`}
      action={
        onClear
          ? {
              label: "Clear Search",
              onClick: onClear,
            }
          : undefined
      }
    />
  )
}

/**
 * Empty state for no uploads
 */
export function NoUploads({ onUpload }: { onUpload?: () => void }) {
  return (
    <EmptyState
      icon={<Upload className="h-16 w-16" />}
      title="No uploads yet"
      description="You haven't uploaded any notes yet. Share your knowledge with your classmates!"
      action={
        onUpload
          ? {
              label: "Upload Your First Note",
              onClick: onUpload,
            }
          : undefined
      }
    />
  )
}

/**
 * Empty state for errors
 */
export function ErrorState({
  title = "Something went wrong",
  description = "We encountered an error while loading this content. Please try again.",
  onRetry,
}: {
  title?: string
  description?: string
  onRetry?: () => void
}) {
  return (
    <EmptyState
      icon={<AlertCircle className="h-16 w-16 text-destructive" />}
      title={title}
      description={description}
      action={
        onRetry
          ? {
              label: "Try Again",
              onClick: onRetry,
            }
          : undefined
      }
    />
  )
}

/**
 * Empty state for no flagged content
 */
export function NoFlaggedContent() {
  return (
    <EmptyState
      icon={<Inbox className="h-16 w-16" />}
      title="No flagged content"
      description="There are no notes flagged for review at the moment. Great job keeping content quality high!"
    />
  )
}

/**
 * Empty state for no notifications
 */
export function NoNotifications() {
  return (
    <EmptyState
      icon={<Inbox className="h-16 w-16" />}
      title="No notifications"
      description="You're all caught up! You'll see notifications here when there's activity on your notes."
    />
  )
}
