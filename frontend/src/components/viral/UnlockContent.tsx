import { useState, useEffect } from 'react';
import { Lock, Unlock, Share2, Users, Upload, TrendingUp, Check } from 'lucide-react';
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
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { apiRequest } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface UnlockOption {
  method: string;
  requirement: string;
  description: string;
  points_reward?: number;
  current_level?: number;
}

interface LockStatus {
  locked: boolean;
  note_id: string;
  access?: string;
  unlock_options?: UnlockOption[];
}

interface UnlockContentProps {
  noteId: string;
  contentType?: 'note' | 'ai_summary';
  children?: React.ReactNode;
  onUnlock?: () => void;
}

export function UnlockContent({ 
  noteId, 
  contentType = 'note',
  children,
  onUnlock 
}: UnlockContentProps) {
  const [lockStatus, setLockStatus] = useState<LockStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [unlocking, setUnlocking] = useState(false);
  const [shareProgress, setShareProgress] = useState(0);
  const { toast } = useToast();

  useEffect(() => {
    checkLockStatus();
  }, [noteId, contentType]);

  const checkLockStatus = async () => {
    setLoading(true);
    try {
      const endpoint = contentType === 'ai_summary'
        ? `/api/virality/ai-summary-lock/${noteId}`
        : `/api/virality/locked-content/${noteId}`;
      
      const data = await apiRequest(endpoint);
      setLockStatus(data);
    } catch (error) {
      console.error('Failed to check lock status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUnlock = async (method: string) => {
    setUnlocking(true);
    try {
      const endpoint = contentType === 'ai_summary'
        ? `/api/virality/unlock-ai-summary/${noteId}`
        : `/api/virality/unlock/${noteId}`;
      
      const data = await apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify({ method })
      });
      
      toast({
        title: 'Unlocked! 🎉',
        description: data.message,
      });
      
      // Refresh lock status
      await checkLockStatus();
      onUnlock?.();
    } catch (error: any) {
      toast({
        title: 'Not Yet',
        description: error.message || 'Complete the requirement first',
        variant: 'destructive',
      });
    } finally {
      setUnlocking(false);
    }
  };

  const handleShare = async (platform: string) => {
    try {
      const data = await apiRequest('/api/virality/share-to-unlock', {
        method: 'POST',
        body: JSON.stringify({
          note_id: noteId,
          platform
        })
      });
      
      setShareProgress((data.unique_platforms / 3) * 100);
      
      if (data.unlock_achieved) {
        toast({
          title: 'Unlocked! 🎉',
          description: 'You can now access this content!',
        });
        await checkLockStatus();
        onUnlock?.();
      } else {
        toast({
          title: `Progress: ${data.unique_platforms}/3`,
          description: data.message,
        });
      }
    } catch (error) {
      console.error('Failed to track share:', error);
    }
  };

  if (loading) {
    return (
      <Card className="p-6 text-center">
        <Lock className="h-8 w-8 mx-auto mb-2 animate-pulse" />
        <p className="text-sm text-muted-foreground">Checking access...</p>
      </Card>
    );
  }

  if (!lockStatus?.locked) {
    // Content is unlocked - render children
    return <>{children}</>;
  }

  // Content is locked - show unlock options
  return (
    <Card className="border-2 border-amber-200 bg-amber-50/50" data-testid="locked-content">
      <CardHeader className="text-center">
        <div className="mx-auto mb-2 h-16 w-16 rounded-full bg-amber-100 flex items-center justify-center">
          <Lock className="h-8 w-8 text-amber-600" />
        </div>
        <CardTitle className="text-amber-900">
          {contentType === 'ai_summary' ? 'AI Summary Locked' : 'Premium Content Locked'}
        </CardTitle>
        <CardDescription>
          Unlock by completing any of these actions
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {lockStatus.unlock_options?.map((option) => (
          <Card key={option.method} className="p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start gap-4">
              <div className="h-12 w-12 rounded-full bg-gradient-to-r from-purple-100 to-pink-100 flex items-center justify-center flex-shrink-0">
                {option.method === 'share' && <Share2 className="h-6 w-6 text-purple-600" />}
                {option.method === 'referral' && <Users className="h-6 w-6 text-purple-600" />}
                {option.method === 'upload' && <Upload className="h-6 w-6 text-purple-600" />}
                {option.method === 'level' && <TrendingUp className="h-6 w-6 text-purple-600" />}
                {option.method === 'tag_friends' && <Users className="h-6 w-6 text-purple-600" />}
                {option.method === 'study_group' && <Users className="h-6 w-6 text-purple-600" />}
              </div>
              <div className="flex-1">
                <h4 className="font-semibold">{option.requirement}</h4>
                <p className="text-sm text-muted-foreground mt-1">{option.description}</p>
                {option.points_reward && (
                  <Badge variant="secondary" className="mt-2">
                    +{option.points_reward} points reward
                  </Badge>
                )}
                {option.current_level !== undefined && (
                  <div className="mt-2">
                    <Progress value={(option.current_level / 10) * 100} className="h-2" />
                    <p className="text-xs text-muted-foreground mt-1">
                      Level {option.current_level}/10
                    </p>
                  </div>
                )}
              </div>
              
              {option.method === 'share' ? (
                <Dialog>
                  <DialogTrigger asChild>
                    <Button size="sm" data-testid={`unlock-${option.method}`}>
                      Share Now
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Share to 3 Platforms</DialogTitle>
                      <DialogDescription>
                        Share this content to unlock it
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <Progress value={shareProgress} className="h-2" />
                      <p className="text-sm text-center">{Math.round(shareProgress / 33)} / 3 platforms</p>
                      
                      <div className="grid grid-cols-2 gap-2">
                        <Button
                          onClick={() => handleShare('whatsapp')}
                          variant="outline"
                          className="w-full"
                        >
                          WhatsApp
                        </Button>
                        <Button
                          onClick={() => handleShare('instagram')}
                          variant="outline"
                          className="w-full"
                        >
                          Instagram
                        </Button>
                        <Button
                          onClick={() => handleShare('twitter')}
                          variant="outline"
                          className="w-full"
                        >
                          Twitter
                        </Button>
                        <Button
                          onClick={() => handleShare('facebook')}
                          variant="outline"
                          className="w-full"
                        >
                          Facebook
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              ) : (
                <Button
                  onClick={() => handleUnlock(option.method)}
                  disabled={unlocking}
                  size="sm"
                  data-testid={`unlock-${option.method}`}
                >
                  {unlocking ? 'Checking...' : 'Try Unlock'}
                </Button>
              )}
            </div>
          </Card>
        ))}
        
        <div className="text-center pt-4 border-t">
          <p className="text-sm text-muted-foreground">
            These actions help grow NotesHub and benefit all students 🎓
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
