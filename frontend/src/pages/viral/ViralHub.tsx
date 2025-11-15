import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  StreakTracker, 
  PointsDisplay, 
  Leaderboard, 
  ReferralDashboard,
  AchievementShowcase,
  StudyGroups,
  SocialFeed,
  ExamCountdown
} from "@/components/viral";
import { Flame, Trophy, Users, Gift, TrendingUp, Award, MessageCircle, Calendar } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";

export default function ViralHub() {
  // Fetch user rank from leaderboard
  const { data: leaderboardData } = useQuery({
    queryKey: ["/api/leaderboards/all-india"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/leaderboards/all-india");
      return await res.json();
    },
  });

  // Fetch referral data
  const { data: referralData } = useQuery({
    queryKey: ["/api/referrals/my-referral"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/referrals/my-referral");
      return await res.json();
    },
  });

  // Fetch achievements count
  const { data: achievementStats } = useQuery({
    queryKey: ["/api/achievements/stats"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/achievements/stats");
      return await res.json();
    },
  });

  const achievementsCount = achievementStats?.unlocked || 0;

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl" data-testid="viral-hub">
      {/* Hero Section */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
          <TrendingUp className="h-10 w-10 text-primary" />
          Growth & Rewards
        </h1>
        <p className="text-muted-foreground text-lg">
          Track your progress, compete with friends, and earn rewards!
        </p>
      </div>

      {/* Tabs for different sections */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-8 lg:grid-cols-8">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Flame className="h-4 w-4" />
            <span className="hidden md:inline">Overview</span>
          </TabsTrigger>
          <TabsTrigger value="leaderboards" className="flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            <span className="hidden md:inline">Ranks</span>
          </TabsTrigger>
          <TabsTrigger value="achievements" className="flex items-center gap-2">
            <Award className="h-4 w-4" />
            <span className="hidden md:inline">Achievements</span>
          </TabsTrigger>
          <TabsTrigger value="groups" className="flex items-center gap-2">
            <MessageCircle className="h-4 w-4" />
            <span className="hidden md:inline">Groups</span>
          </TabsTrigger>
          <TabsTrigger value="social" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            <span className="hidden md:inline">Social</span>
          </TabsTrigger>
          <TabsTrigger value="referrals" className="flex items-center gap-2">
            <Gift className="h-4 w-4" />
            <span className="hidden md:inline">Referrals</span>
          </TabsTrigger>
          <TabsTrigger value="exams" className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span className="hidden md:inline">Exams</span>
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <StreakTracker />
            <PointsDisplay showProgress={true} />
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950 dark:to-cyan-950 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Your Rank</p>
                  <p className="text-3xl font-bold">
                    {leaderboardData?.user_rank ? `#${leaderboardData.user_rank}` : "#--"}
                  </p>
                </div>
                <Trophy className="h-10 w-10 text-blue-500" />
              </div>
            </div>
            
            <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950 rounded-lg border border-purple-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Referrals</p>
                  <p className="text-3xl font-bold">
                    {referralData?.total_referrals ?? "--"}
                  </p>
                </div>
                <Users className="h-10 w-10 text-purple-500" />
              </div>
            </div>
            
            <div className="p-6 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950 dark:to-orange-950 rounded-lg border border-amber-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Achievements</p>
                  <p className="text-3xl font-bold">{achievementsCount}</p>
                </div>
                <Gift className="h-10 w-10 text-amber-500" />
              </div>
            </div>
          </div>

          {/* Tips Section */}
          <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950 dark:to-purple-950 rounded-lg border border-indigo-200">
            <h3 className="text-lg font-semibold mb-3">💡 Pro Tips to Rank Higher</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Maintain daily streaks for bonus points (5 pts/day)</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Upload quality notes to earn 100 points each</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Your notes getting downloaded = 5 points each</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Refer friends for 50 points + instant rewards</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Share notes on social media for extra points</span>
              </li>
            </ul>
          </div>
        </TabsContent>

        {/* Leaderboards Tab */}
        <TabsContent value="leaderboards">
          <Leaderboard />
        </TabsContent>

        {/* Referrals Tab */}
        <TabsContent value="referrals">
          <ReferralDashboard />
        </TabsContent>

        {/* Achievements Tab */}
        <TabsContent value="achievements">
          <AchievementShowcase />
        </TabsContent>

        {/* Study Groups Tab */}
        <TabsContent value="groups">
          <StudyGroups />
        </TabsContent>

        {/* Social Feed Tab */}
        <TabsContent value="social">
          <SocialFeed />
        </TabsContent>

        {/* Exams Tab */}
        <TabsContent value="exams">
          <ExamCountdown />
        </TabsContent>
      </Tabs>
    </div>
  );
}
