import { useEffect, useState } from "react";
import { Users, Gift, Copy, Check, Share2, TrendingUp } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { apiRequest } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { useQuery } from "@tanstack/react-query";

interface ReferralData {
  referral_code: string;
  total_referrals: number;
  rewards_earned: {
    bonus_downloads: number;
    ai_access_days: number;
    premium_days: number;
  };
  referral_link: string;
}

interface ReferralStats {
  total_referrals: number;
  rewards_earned: any;
  next_milestone: {
    count: number;
    reward: string;
    progress: number;
    needed: number;
  } | null;
  all_milestones: Record<string, any>;
}

export function ReferralDashboard() {
  const [referralData, setReferralData] = useState<ReferralData | null>(null);
  const [stats, setStats] = useState<ReferralStats | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [timeLeft, setTimeLeft] = useState("");
  const { toast } = useToast();

  // Fetch recent activity
  const { data: recentActivity } = useQuery({
    queryKey: ["/api/referrals/recent-activity"],
    queryFn: async () => {
      const res = await apiRequest("/api/referrals/recent-activity");
      return res;
    },
    refetchInterval: 15000, // Refresh every 15 seconds
  });

  // Fetch ranking data
  const { data: rankingData } = useQuery({
    queryKey: ["/api/referrals/my-ranking"],
    queryFn: async () => {
      const res = await apiRequest("/api/referrals/my-ranking");
      return res;
    },
  });

  // Fetch active bonus
  const { data: bonusData } = useQuery({
    queryKey: ["/api/referrals/active-bonus"],
    queryFn: async () => {
      const res = await apiRequest("/api/referrals/active-bonus");
      return res;
    },
    refetchInterval: 60000, // Refresh every minute
  });

  useEffect(() => {
    fetchReferralData();
  }, []);

  // Countdown timer for flash bonus
  useEffect(() => {
    if (bonusData?.expires_at) {
      const interval = setInterval(() => {
        const now = new Date().getTime();
        const end = new Date(bonusData.expires_at).getTime();
        const diff = end - now;
        
        if (diff > 0) {
          const hours = Math.floor(diff / (1000 * 60 * 60));
          const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((diff % (1000 * 60)) / 1000);
          setTimeLeft(`${hours}h ${minutes}m ${seconds}s`);
        } else {
          setTimeLeft("EXPIRED");
        }
      }, 1000);
      
      return () => clearInterval(interval);
    }
  }, [bonusData]);

  const fetchReferralData = async () => {
    try {
      const [data, statsData] = await Promise.all([
        apiRequest("/api/referrals/my-referral"),
        apiRequest("/api/referrals/stats")
      ]);
      setReferralData(data);
      setStats(statsData);
    } catch (error) {
      console.error("Failed to fetch referral data:", error);
    } finally {
      setLoading(false);
    }
  };

  const copyReferralCode = () => {
    if (referralData) {
      navigator.clipboard.writeText(referralData.referral_code);
      setCopied(true);
      toast({
        title: "Copied!",
        description: "Referral code copied to clipboard",
      });
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const copyReferralLink = () => {
    if (referralData) {
      navigator.clipboard.writeText(referralData.referral_link);
      toast({
        title: "Link Copied!",
        description: "Share this link with your friends",
      });
    }
  };

  const shareWhatsApp = () => {
    if (referralData) {
      const message = `Hey! 📚 Join NotesHub using my referral code *${referralData.referral_code}* and get 20 FREE downloads! 🎉\n\nBest notes sharing platform for students!\n${referralData.referral_link}`;
      window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, '_blank');
    }
  };

  if (loading) {
    return (
      <Card data-testid="referral-dashboard-loading">
        <CardHeader>
          <CardTitle>Loading Referrals...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-20 bg-muted rounded"></div>
            <div className="h-16 bg-muted rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!referralData || !stats) {
    return null;
  }

  const milestoneProgress = stats.next_milestone 
    ? (stats.next_milestone.progress / stats.next_milestone.count) * 100 
    : 100;

  return (
    <div className="space-y-6" data-testid="referral-dashboard">
      {/* Flash Bonus Alert */}
      {bonusData?.active && (
        <Card className="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-950 dark:to-orange-950 border-2 border-red-500 animate-pulse">
          <CardContent className="pt-6">
            <div className="text-center">
              <Badge className="bg-red-500 text-white mb-2 animate-bounce">⚡ FLASH BONUS</Badge>
              <h3 className="text-2xl font-bold mb-2">{bonusData.title}</h3>
              <p className="text-lg mb-4">{bonusData.description}</p>
              <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-4">
                ⏰ {timeLeft}
              </div>
              <Button size="lg" className="bg-red-600 hover:bg-red-700" onClick={shareWhatsApp}>
                Share Now & Get {bonusData.bonus_multiplier}x Points! 🔥
              </Button>
              <p className="text-xs text-muted-foreground mt-2">
                {bonusData.participants_count} students already participating!
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Referral Code Card */}
      <Card className="bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Gift className="h-6 w-6 text-purple-500" />
            <CardTitle>Your Referral Code</CardTitle>
          </div>
          <CardDescription>
            Invite friends and earn instant rewards!
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Referral Code */}
          <div className="flex items-center gap-2">
            <Input 
              value={referralData.referral_code}
              readOnly
              className="text-2xl font-bold text-center bg-white dark:bg-black"
              data-testid="referral-code-input"
            />
            <Button 
              onClick={copyReferralCode}
              variant="outline"
              size="icon"
              data-testid="copy-code-button"
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>

          {/* Share Buttons */}
          <div className="flex gap-2">
            <Button 
              onClick={shareWhatsApp}
              className="flex-1 bg-green-600 hover:bg-green-700"
              data-testid="share-whatsapp-button"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share on WhatsApp
            </Button>
            <Button 
              onClick={copyReferralLink}
              variant="outline"
              className="flex-1"
              data-testid="copy-link-button"
            >
              <Copy className="h-4 w-4 mr-2" />
              Copy Link
            </Button>
          </div>

          {/* Live Activity Feed */}
          <Card className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 border-2 border-blue-200 mt-4">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Live Referral Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-32">
                <div className="space-y-2">
                  {recentActivity?.activities?.map((activity: any, idx: number) => (
                    <div key={idx} className="text-xs p-2 bg-white dark:bg-black rounded flex items-center gap-2">
                      <Users className="h-3 w-3 text-blue-500" />
                      <span className="flex-1">
                        <strong>{activity.user_name}</strong> just got {activity.count} referrals
                      </span>
                      <span className="text-muted-foreground">{activity.time_ago}</span>
                    </div>
                  ))}
                  {(!recentActivity?.activities || recentActivity.activities.length === 0) && (
                    <p className="text-xs text-muted-foreground text-center py-4">No recent activity</p>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Competitive Ranking */}
          <Card className="border-2 border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950 dark:to-orange-950 mt-4">
            <CardContent className="pt-6">
              <div className="text-center mb-4">
                <p className="text-sm text-muted-foreground mb-1">Your Referral Rank</p>
                <p className="text-4xl font-bold text-amber-600">
                  #{rankingData?.rank || "--"}
                </p>
              </div>
              
              {rankingData?.behind && (
                <div className="p-3 bg-white dark:bg-black rounded-lg text-sm">
                  <p className="text-muted-foreground mb-1">
                    🎯 You're <strong>{rankingData.behind.difference}</strong> referrals behind
                  </p>
                  <p className="font-semibold">{rankingData.behind.user_name} (Rank #{rankingData.behind.rank})</p>
                  <Button size="sm" className="w-full mt-2" onClick={shareWhatsApp}>
                    Catch Up Now! 🚀
                  </Button>
                </div>
              )}
              
              {rankingData?.ahead && (
                <div className="p-3 bg-green-50 dark:bg-green-950 rounded-lg text-sm mt-2">
                  <p className="text-green-600 dark:text-green-400">
                    🔥 You're ahead of {rankingData.ahead.count} students!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </CardContent>
      </Card>

      {/* Stats Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-primary" />
              <CardTitle className="text-xl">Referral Stats</CardTitle>
            </div>
            <Badge variant="secondary" className="text-lg px-3 py-1">
              {referralData.total_referrals} Friends
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Rewards Earned */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-lg text-center">
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {referralData.rewards_earned.bonus_downloads}
              </p>
              <p className="text-xs text-muted-foreground">Bonus Downloads</p>
            </div>
            <div className="p-3 bg-purple-50 dark:bg-purple-950 rounded-lg text-center">
              <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {referralData.rewards_earned.ai_access_days}
              </p>
              <p className="text-xs text-muted-foreground">AI Access Days</p>
            </div>
            <div className="p-3 bg-amber-50 dark:bg-amber-950 rounded-lg text-center">
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                {referralData.rewards_earned.premium_days}
              </p>
              <p className="text-xs text-muted-foreground">Premium Days</p>
            </div>
          </div>

          {/* Next Milestone */}
          {stats.next_milestone && (
            <div className="space-y-2 p-4 bg-slate-100 dark:bg-slate-800 rounded-lg">
              <div className="flex items-center justify-between">
                <p className="font-semibold">Next Milestone:</p>
                <Badge variant="outline" className="bg-white dark:bg-black">
                  {stats.next_milestone.count} referrals
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                🎁 {stats.next_milestone.reward}
              </p>
              <Progress value={milestoneProgress} className="h-2" />
              <p className="text-xs text-muted-foreground text-right">
                {stats.next_milestone.needed} more to go!
              </p>
            </div>
          )}

          {/* All Milestones */}
          <div className="pt-2 border-t">
            <p className="text-sm font-medium mb-3">🎯 Referral Milestones:</p>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">3 friends</span>
                <span className="font-medium">🤖 AI Assistant (1 month)</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">10 friends</span>
                <span className="font-medium">👑 Lifetime Premium</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">50 friends</span>
                <span className="font-medium">💰 Cash Payout ₹500</span>
              </div>
            </div>
          </div>

          {/* How it works */}
          <div className="p-4 bg-blue-50 dark:bg-blue-950/50 rounded-lg">
            <p className="text-sm font-medium mb-2">💡 How Referrals Work:</p>
            <ul className="text-xs space-y-1 text-muted-foreground">
              <li>✅ Friend signs up → You get 10 downloads instantly</li>
              <li>✅ Friend uploads note → You get 5 more downloads</li>
              <li>✅ Your friend gets 20 downloads (vs 5 normally)</li>
              <li>✅ Reach milestones for premium features!</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
