import { useState } from 'react';
import { Instagram, Download, Share2, Check, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { apiRequest } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface StoryTemplate {
  template_type: string;
  template: {
    title: string;
    gradient: string;
    emoji: string;
    format: string;
  };
  data: Record<string, any>;
  share_url: string;
  hashtags: string[];
}

interface InstagramStoryGeneratorProps {
  type: 'achievement' | 'streak' | 'leaderboard' | 'level' | 'exam' | 'group' | 'note' | 'referral';
  itemId?: string;
  buttonText?: string;
  compact?: boolean;
}

export function InstagramStoryGenerator({ 
  type, 
  itemId, 
  buttonText = 'Share Story',
  compact = false 
}: InstagramStoryGeneratorProps) {
  const [loading, setLoading] = useState(false);
  const [storyData, setStoryData] = useState<StoryTemplate | null>(null);
  const [shared, setShared] = useState(false);
  const { toast } = useToast();

  const generateStory = async () => {
    setLoading(true);
    try {
      let endpoint = '';
      
      switch (type) {
        case 'achievement':
          endpoint = `/api/instagram/generate/achievement/${itemId}`;
          break;
        case 'streak':
          endpoint = '/api/instagram/generate/streak';
          break;
        case 'leaderboard':
          endpoint = '/api/instagram/generate/leaderboard';
          break;
        case 'level':
          endpoint = '/api/instagram/generate/level-up';
          break;
        case 'exam':
          endpoint = `/api/instagram/generate/exam/${itemId}`;
          break;
        case 'group':
          endpoint = `/api/instagram/generate/group/${itemId}`;
          break;
        case 'note':
          endpoint = `/api/instagram/generate/note/${itemId}`;
          break;
        case 'referral':
          endpoint = '/api/instagram/generate/referral';
          break;
      }
      
      const data = await apiRequest(endpoint);
      setStoryData(data);
    } catch (error) {
      console.error('Failed to generate story:', error);
      toast({
        title: 'Error',
        description: 'Failed to generate story template',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadStoryImage = () => {
    if (!storyData) return;

    // Create canvas for story image (1080x1920 - Instagram story size)
    const canvas = document.createElement('canvas');
    canvas.width = 1080;
    canvas.height = 1920;
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return;

    // Create gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, 1920);
    const gradientColors = storyData.template.gradient.match(/from-(\S+)\s+via-(\S+)\s+to-(\S+)/);
    
    // Default gradient colors
    gradient.addColorStop(0, '#f59e0b');
    gradient.addColorStop(0.5, '#ef4444');
    gradient.addColorStop(1, '#dc2626');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 1080, 1920);

    // Add semi-transparent overlay
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fillRect(0, 0, 1080, 1920);

    // Add NotesHub branding at top
    ctx.fillStyle = 'white';
    ctx.font = 'bold 60px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('NotesHub', 540, 150);

    // Add emoji
    ctx.font = '200px Arial';
    ctx.fillText(storyData.template.emoji, 540, 400);

    // Add title
    ctx.font = 'bold 80px Arial';
    ctx.fillText(storyData.template.title, 540, 600);

    // Add main content (split by newlines)
    const formattedText = storyData.template.format;
    const lines = Object.entries(storyData.data)
      .reduce((text, [key, value]) => 
        text.replace(`{${key}}`, String(value)), formattedText
      )
      .split('\n');
    
    ctx.font = 'bold 70px Arial';
    let yPos = 800;
    lines.forEach((line) => {
      ctx.fillText(line, 540, yPos);
      yPos += 100;
    });

    // Add hashtags at bottom
    ctx.font = '40px Arial';
    const hashtagText = storyData.hashtags.map(h => `#${h}`).join(' ');
    ctx.fillText(hashtagText, 540, 1750);

    // Add URL at very bottom
    ctx.font = '35px Arial';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.fillText('Download from NotesHub', 540, 1850);

    // Convert to blob and download
    canvas.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `noteshub-${type}-story.png`;
      a.click();
      URL.revokeObjectURL(url);
      
      toast({
        title: 'Downloaded! 📥',
        description: 'Story image saved. Upload to Instagram!',
      });
    });
  };

  const shareToInstagram = async () => {
    if (!storyData) return;

    // Copy link to clipboard
    await navigator.clipboard.writeText(storyData.share_url);
    
    // Track share
    try {
      await apiRequest('/api/instagram/track-story-share', {
        method: 'POST',
        body: JSON.stringify({
          template_type: type,
          platform: 'instagram'
        })
      });
      
      setShared(true);
      setTimeout(() => setShared(false), 3000);
      
      toast({
        title: 'Ready to share! 🎉',
        description: 'Link copied! Download image and post to Instagram. +10 points earned!',
      });
    } catch (error) {
      console.error('Failed to track share:', error);
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          onClick={generateStory}
          size={compact ? 'sm' : 'default'}
          variant="outline"
          className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0 hover:from-purple-600 hover:to-pink-600"
          data-testid="generate-instagram-story"
        >
          {compact ? (
            <Instagram className="h-4 w-4" />
          ) : (
            <>
              <Instagram className="h-4 w-4 mr-2" />
              {buttonText}
            </>
          )}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Instagram className="h-5 w-5 text-pink-500" />
            Instagram Story Template
          </DialogTitle>
          <DialogDescription>
            Share your achievement with the world!
          </DialogDescription>
        </DialogHeader>
        
        {loading && (
          <div className="flex items-center justify-center py-8">
            <Sparkles className="h-8 w-8 animate-spin text-purple-500" />
          </div>
        )}
        
        {storyData && (
          <Card className="border-2">
            <CardHeader className={`bg-gradient-to-r ${storyData.template.gradient} text-white`}>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <span>{storyData.template.emoji}</span>
                {storyData.template.title}
              </CardTitle>
              <CardDescription className="text-white/90">
                {Object.entries(storyData.data)
                  .reduce((text, [key, value]) => 
                    text.replace(`{${key}}`, String(value)), storyData.template.format
                  )
                  .split('\n')
                  .map((line, i) => (
                    <div key={i} className="font-semibold">{line}</div>
                  ))
                }
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <div className="flex flex-wrap gap-2">
                {storyData.hashtags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    #{tag}
                  </Badge>
                ))}
              </div>
              
              <div className="flex gap-2">
                <Button
                  onClick={downloadStoryImage}
                  className="flex-1"
                  variant="outline"
                  data-testid="download-story-image"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Image
                </Button>
                
                <Button
                  onClick={shareToInstagram}
                  className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                  data-testid="share-to-instagram"
                >
                  {shared ? (
                    <Check className="h-4 w-4 mr-2" />
                  ) : (
                    <Share2 className="h-4 w-4 mr-2" />
                  )}
                  Share (+10 pts)
                </Button>
              </div>
              
              <p className="text-xs text-muted-foreground text-center">
                Download the image, then upload as Instagram Story
              </p>
            </CardContent>
          </Card>
        )}
      </DialogContent>
    </Dialog>
  );
}
