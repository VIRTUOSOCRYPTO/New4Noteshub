import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Card, CardContent } from "@/components/ui/card";
import { Share2, QrCode, Copy, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

interface WhatsAppShareButtonsProps {
  shareType: "note" | "achievement" | "group" | "streak" | "leaderboard" | "referral";
  itemId?: string;
  additionalParams?: Record<string, any>;
}

export function WhatsAppShareButtons({ shareType, itemId, additionalParams }: WhatsAppShareButtonsProps) {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const getShareEndpoint = () => {
    switch (shareType) {
      case "note":
        return `/api/whatsapp/share-note/${itemId}`;
      case "achievement":
        return `/api/whatsapp/share-achievement?achievement_name=${additionalParams?.name}`;
      case "group":
        return `/api/whatsapp/share-group/${itemId}`;
      case "streak":
        return `/api/whatsapp/share-streak`;
      case "leaderboard":
        return `/api/whatsapp/share-leaderboard-rank?rank=${additionalParams?.rank}&leaderboard_type=${additionalParams?.type}`;
      case "referral":
        return `/api/whatsapp/share-referral`;
      default:
        return "";
    }
  };

  // Fetch share link when dialog opens
  const { data: shareData, isLoading } = useQuery({
    queryKey: ["whatsapp-share", shareType, itemId],
    queryFn: async () => {
      const res = await apiRequest("GET", getShareEndpoint());
      return await res.json();
    },
    enabled: isDialogOpen,
  });

  // Track share mutation
  const trackShareMutation = useMutation({
    mutationFn: async () => {
      const res = await apiRequest("POST", "/api/whatsapp/track-share", {
        share_type: shareType,
        item_id: itemId,
      });
      return await res.json();
    },
  });

  const handleShare = () => {
    if (shareData?.whatsapp_link) {
      window.open(shareData.whatsapp_link, "_blank");
      trackShareMutation.mutate();
      setIsDialogOpen(false);
      
      toast({
        title: "Opening WhatsApp...",
        description: "Share completed! +10 points",
      });
    }
  };

  const handleCopyLink = () => {
    if (shareData?.app_url) {
      navigator.clipboard.writeText(shareData.app_url);
      setCopied(true);
      
      toast({
        title: "Link Copied!",
        description: "Link copied to clipboard",
      });
      
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" data-testid="whatsapp-share-button">
          <Share2 className="h-4 w-4 mr-2" />
          Share to WhatsApp
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Share on WhatsApp</DialogTitle>
        </DialogHeader>
        
        {isLoading ? (
          <div className="text-center py-8">Loading...</div>
        ) : (
          <div className="space-y-4">
            {/* QR Code */}
            {shareData?.qr_code && (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <img 
                      src={shareData.qr_code} 
                      alt="QR Code" 
                      className="mx-auto w-48 h-48"
                    />
                    <p className="text-sm text-muted-foreground mt-2">
                      Scan with WhatsApp to share
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Message Preview */}
            {shareData?.message_preview && (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-xs text-muted-foreground mb-2">Preview:</p>
                  <div className="p-3 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 text-sm whitespace-pre-wrap">
                    {shareData.message_preview}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button 
                className="flex-1 bg-green-600 hover:bg-green-700" 
                onClick={handleShare}
                data-testid="share-to-whatsapp"
              >
                <Share2 className="h-4 w-4 mr-2" />
                Share Now
              </Button>
              
              {shareData?.app_url && (
                <Button 
                  variant="outline" 
                  onClick={handleCopyLink}
                  data-testid="copy-link"
                >
                  {copied ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              )}
            </div>

            <p className="text-xs text-center text-muted-foreground">
              💡 Share and earn +10 points!
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
