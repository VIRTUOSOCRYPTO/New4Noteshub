import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  StreakTracker, 
  PointsDisplay, 
  Leaderboard, 
  ReferralDashboard,
  AchievementShowcase,
  StudyGroups,
  SocialFeed,
  ExamCountdown,
  ChallengesHub,
  ContestsGallery,
  FOMOTriggers,
  SurpriseRewards,
  AIRecommendations
} from "@/components/viral";
import { Flame, Trophy, Users, TrendingUp, Target, Sparkles, Brain, Gift } from "lucide-react";
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

      {/* Tabs for different sections - Consolidated from 12 to 6 */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6 gap-2">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Flame className="h-4 w-4" />
            <span>Overview</span>
          </TabsTrigger>
          <TabsTrigger value="progress" className="flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            <span>Progress</span>
          </TabsTrigger>
          <TabsTrigger value="community" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            <span>Community</span>
          </TabsTrigger>
          <TabsTrigger value="compete" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            <span>Compete</span>
          </TabsTrigger>
          <TabsTrigger value="rewards" className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            <span>Rewards</span>
          </TabsTrigger>
          <TabsTrigger value="ai" className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-pink-600 text-white">
            <Brain className="h-4 w-4" />
            <span>AI</span>
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

        {/* Progress Tab - Combines Ranks + Achievements */}
        <TabsContent value="progress" className="space-y-6">
          <div className="mb-4">
            <h2 className="text-2xl font-bold mb-2">Your Progress</h2>
            <p className="text-muted-foreground">Track your rankings and unlock achievements</p>
          </div>
          <Leaderboard />
          <div className="mt-8">
            <AchievementShowcase />
          </div>
        </TabsContent>

        {/* Community Tab - Combines Groups + Social + Referrals */}
        <TabsContent value="community" className="space-y-6">
          <div className="mb-4">
            <h2 className="text-2xl font-bold mb-2">Community</h2>
            <p className="text-muted-foreground">Connect with friends, join groups, and grow together</p>
          </div>
          
          {/* Referrals Section */}
          <div>
            <h3 className="text-xl font-semibold mb-4">Referrals & Invites</h3>
            <ReferralDashboard />
          </div>

          {/* Study Groups Section */}
          <div className="mt-8">
            <h3 className="text-xl font-semibold mb-4">Study Groups</h3>
            <StudyGroups />
          </div>

          {/* Social Feed Section */}
          <div className="mt-8">
            <h3 className="text-xl font-semibold mb-4">Social Feed</h3>
            <SocialFeed />
          </div>
        </TabsContent>

        {/* Compete Tab - Combines Challenges + Contests + Exams */}
        <TabsContent value="compete" className="space-y-6">
          <div className="mb-4">
            <h2 className="text-2xl font-bold mb-2">Competitions</h2>
            <p className="text-muted-foreground">Join challenges, contests, and track your exams</p>
          </div>

          {/* Exam Countdown */}
          <div>
            <h3 className="text-xl font-semibold mb-4">Exam Countdown</h3>
            <ExamCountdown />
          </div>

          {/* Challenges */}
          <div className="mt-8">
            <h3 className="text-xl font-semibold mb-4">Daily Challenges</h3>
            <ChallengesHub />
          </div>

          {/* Contests */}
          <div className="mt-8">
            <h3 className="text-xl font-semibold mb-4">Contests</h3>
            <ContestsGallery />
          </div>
        </TabsContent>

        {/* Rewards Tab - Combines Alerts + Rewards */}
        <TabsContent value="rewards" className="space-y-6">
          <div className="mb-4">
            <h2 className="text-2xl font-bold mb-2">Rewards & Alerts</h2>
            <p className="text-muted-foreground">Claim rewards and stay updated with live activity</p>
          </div>

          {/* FOMO Triggers / Alerts */}
          <div>
            <h3 className="text-xl font-semibold mb-4">Live Activity Feed</h3>
            <FOMOTriggers />
          </div>

          {/* Surprise Rewards */}
          <div className="mt-8">
            <h3 className="text-xl font-semibold mb-4">Surprise Rewards</h3>
            <SurpriseRewards />
          </div>
        </TabsContent>

        {/* AI Personalization Tab - NEW */}
        <TabsContent value="ai">
          <AIRecommendations />
        </TabsContent>
      </Tabs>
    </div>
  );
}
