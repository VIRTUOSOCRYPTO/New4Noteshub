import { useEffect, useState } from "react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Trophy, Share2, X, Instagram } from "lucide-react";
import confetti from "canvas-confetti";

interface AchievementCelebrationProps {
  achievement: {
    id: string;
    name: string;
    description: string;
    icon: string;
    rarity: string;
    points: number;
  } | null;
  onClose: () => void;
  onShare: () => void;
}

export function AchievementCelebration({ achievement, onClose, onShare }: AchievementCelebrationProps) {
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (achievement) {
      setShowModal(true);
      
      // Trigger confetti
      const duration = 3000;
      const end = Date.now() + duration;

      (function frame() {
        confetti({
          particleCount: 3,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: ['#FFD700', '#FFA500', '#FF69B4']
        });
        confetti({
          particleCount: 3,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: ['#FFD700', '#FFA500', '#FF69B4']
        });

        if (Date.now() < end) {
          requestAnimationFrame(frame);
        }
      }());
    }
  }, [achievement]);

  if (!achievement) return null;

  const handleShare = () => {
    onShare();
    // Auto-generate Instagram story
    const message = `🎉 Achievement Unlocked!

${achievement.icon} ${achievement.name}
${achievement.description}

+${achievement.points} points earned!

Join me on NotesHub 📚`;
    
    // Copy to clipboard for easy sharing
    navigator.clipboard.writeText(message);
    
    // Open share dialog
    if (navigator.share) {
      navigator.share({
        title: 'Achievement Unlocked!',
        text: message,
      });
    }
  };

  return (
    <Dialog open={showModal} onOpenChange={setShowModal}>
      <DialogContent className="max-w-2xl p-0 overflow-hidden border-4 border-amber-500">
        {/* Close button */}
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-4 right-4 z-50"
          onClick={() => {
            setShowModal(false);
            onClose();
          }}
        >
          <X className="h-6 w-6" />
        </Button>

        {/* Celebration Content */}
        <div className="relative bg-gradient-to-br from-purple-600 via-pink-600 to-amber-600 text-white p-12 text-center">
          {/* Animated background */}
          <div className="absolute inset-0 opacity-20 animate-pulse"></div>
          
          <div className="relative z-10">
            {/* Trophy animation */}
            <div className="mb-6 animate-bounce">
              <Trophy className="h-24 w-24 mx-auto text-yellow-300 drop-shadow-2xl" />
            </div>

            {/* Achievement icon */}
            <div className="text-8xl mb-4 animate-pulse">
              {achievement.icon}
            </div>

            {/* Title */}
            <h1 className="text-5xl font-bold mb-4 animate-pulse">
              Achievement Unlocked!
            </h1>

            {/* Achievement details */}
            <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-6 mb-6 max-w-md mx-auto">
              <h2 className="text-3xl font-bold mb-2">{achievement.name}</h2>
              <p className="text-xl mb-4 text-white/90">{achievement.description}</p>
              
              <div className="flex items-center justify-center gap-4">
                <div className="bg-white/30 rounded-full px-6 py-2">
                  <p className="text-sm">Rarity</p>
                  <p className="text-xl font-bold uppercase">{achievement.rarity}</p>
                </div>
                <div className="bg-white/30 rounded-full px-6 py-2">
                  <p className="text-sm">Points</p>
                  <p className="text-xl font-bold">+{achievement.points}</p>
                </div>
              </div>
            </div>

            {/* Share buttons */}
            <div className="space-y-3">
              <Button 
                size="lg" 
                className="w-full max-w-md bg-white text-purple-600 hover:bg-gray-100 text-lg font-bold"
                onClick={handleShare}
              >
                <Share2 className="mr-2 h-5 w-5" />
                Share & Get 50 Bonus Points!
              </Button>
              
              <div className="flex gap-2 max-w-md mx-auto">
                <Button 
                  variant="outline" 
                  className="flex-1 bg-white/10 border-white/30 text-white hover:bg-white/20"
                  onClick={() => {
                    // Generate Instagram story
                    window.open('https://www.instagram.com/create/story', '_blank');
                  }}
                >
                  <Instagram className="mr-2 h-4 w-4" />
                  Instagram
                </Button>
                <Button 
                  variant="outline" 
                  className="flex-1 bg-white/10 border-white/30 text-white hover:bg-white/20"
                  onClick={() => {
                    const message = encodeURIComponent(`🎉 I just unlocked "${achievement.name}" on NotesHub! ${achievement.icon}

Join me: [link]`);
                    window.open(`https://wa.me/?text=${message}`, '_blank');
                  }}
                >
                  <Share2 className="mr-2 h-4 w-4" />
                  WhatsApp
                </Button>
              </div>
            </div>

            <p className="text-sm text-white/70 mt-4">
              💡 Share now to inspire your friends and earn bonus points!
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
