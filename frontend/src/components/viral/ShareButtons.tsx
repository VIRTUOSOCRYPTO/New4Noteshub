import { useState } from "react";
import { Share2, MessageCircle, Instagram, Twitter, Facebook, Link2, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { apiRequest } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface ShareButtonsProps {
  noteId: string;
  noteTitle: string;
  noteSubject: string;
  compact?: boolean;
}

export function ShareButtons({ noteId, noteTitle, noteSubject, compact = false }: ShareButtonsProps) {
  const [shared, setShared] = useState(false);
  const { toast } = useToast();

  const recordShare = async (platform: string) => {
    try {
      await apiRequest("/api/gamification/share", {
        method: "POST",
        body: JSON.stringify({
          note_id: noteId,
          platform: platform
        })
      });
      
      setShared(true);
      setTimeout(() => setShared(false), 2000);
      
      toast({
        title: "Thanks for sharing! 🎉",
        description: "+10 points earned!",
      });
    } catch (error) {
      console.error("Failed to record share:", error);
    }
  };

  const shareWhatsApp = () => {
    const noteUrl = `${window.location.origin}/notes/${noteId}`;
    const message = `Check out these amazing ${noteSubject} notes: "${noteTitle}" 📚\n\nDownload from NotesHub: ${noteUrl}\n\n#StudySmart #NotesHub`;
    window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, '_blank');
    recordShare('whatsapp');
  };

  const shareInstagram = () => {
    // For Instagram, we'll copy the link and show instructions
    const noteUrl = `${window.location.origin}/notes/${noteId}`;
    navigator.clipboard.writeText(noteUrl);
    
    toast({
      title: "Link Copied! 📋",
      description: "Paste it in your Instagram story or bio",
    });
    
    recordShare('instagram');
  };

  const shareTwitter = () => {
    const noteUrl = `${window.location.origin}/notes/${noteId}`;
    const message = `Found these great ${noteSubject} notes: "${noteTitle}" 📚\n\nDownload from NotesHub 👇`;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(message)}&url=${encodeURIComponent(noteUrl)}`, '_blank');
    recordShare('twitter');
  };

  const shareFacebook = () => {
    const noteUrl = `${window.location.origin}/notes/${noteId}`;
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(noteUrl)}`, '_blank');
    recordShare('facebook');
  };

  const copyLink = () => {
    const noteUrl = `${window.location.origin}/notes/${noteId}`;
    navigator.clipboard.writeText(noteUrl);
    
    toast({
      title: "Link Copied! ✅",
      description: "Share it anywhere you like!",
    });
    
    recordShare('copy_link');
  };

  const useWebShareAPI = async () => {
    const noteUrl = `${window.location.origin}/notes/${noteId}`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: noteTitle,
          text: `Check out these ${noteSubject} notes on NotesHub!`,
          url: noteUrl,
        });
        recordShare('web_share');
      } catch (error) {
        console.log("Web Share cancelled or failed");
      }
    } else {
      // Fallback to copy link
      copyLink();
    }
  };

  if (compact) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button 
            variant="ghost" 
            size="sm"
            data-testid="share-button-compact"
          >
            {shared ? (
              <Check className="h-4 w-4 text-green-500" />
            ) : (
              <Share2 className="h-4 w-4" />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuItem onClick={shareWhatsApp} data-testid="share-whatsapp">
            <MessageCircle className="h-4 w-4 mr-2 text-green-600" />
            Share on WhatsApp
          </DropdownMenuItem>
          <DropdownMenuItem onClick={shareInstagram} data-testid="share-instagram">
            <Instagram className="h-4 w-4 mr-2 text-pink-600" />
            Share on Instagram
          </DropdownMenuItem>
          <DropdownMenuItem onClick={shareTwitter} data-testid="share-twitter">
            <Twitter className="h-4 w-4 mr-2 text-blue-500" />
            Share on Twitter
          </DropdownMenuItem>
          <DropdownMenuItem onClick={shareFacebook} data-testid="share-facebook">
            <Facebook className="h-4 w-4 mr-2 text-blue-600" />
            Share on Facebook
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={copyLink} data-testid="copy-link">
            <Link2 className="h-4 w-4 mr-2" />
            Copy Link
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  return (
    <div className="flex flex-wrap gap-2" data-testid="share-buttons">
      <Button 
        onClick={shareWhatsApp}
        className="bg-green-600 hover:bg-green-700"
        size="sm"
        data-testid="share-whatsapp-full"
      >
        <MessageCircle className="h-4 w-4 mr-2" />
        WhatsApp
      </Button>
      
      <Button 
        onClick={shareInstagram}
        className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
        size="sm"
        data-testid="share-instagram-full"
      >
        <Instagram className="h-4 w-4 mr-2" />
        Instagram
      </Button>

      <Button 
        onClick={shareTwitter}
        className="bg-blue-500 hover:bg-blue-600"
        size="sm"
        data-testid="share-twitter-full"
      >
        <Twitter className="h-4 w-4 mr-2" />
        Twitter
      </Button>

      <Button 
        onClick={useWebShareAPI}
        variant="outline"
        size="sm"
        data-testid="share-more"
      >
        <Share2 className="h-4 w-4 mr-2" />
        More...
      </Button>
    </div>
  );
}
