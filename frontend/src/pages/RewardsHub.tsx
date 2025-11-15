import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  StreakTracker, 
  PointsDisplay,
  ReferralDashboard,
  AchievementShowcase,
  ChallengesHub,
  ContestsGallery,
  FOMOTriggers,
  SurpriseRewards
} from "@/components/viral";
import { Flame, Gift, Award, Users as UsersIcon, Target, Trophy, Zap } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";

export default function RewardsHub() {
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
    <div className="container mx-auto py-8 px-4 max-w-7xl" data-testid="rewards-hub">
      {/* Hero Section */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
          <Gift className="h-10 w-10 text-primary" />
          Rewards Hub
        </h1>
        <p className="text-muted-foreground text-lg">
          Earn points, unlock achievements, and claim amazing rewards!
        </p>
      </div>

      {/* 7 Tabs for Rewards */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:grid-cols-7 gap-2">
          <TabsTrigger value="overview" className="flex items-center gap-2" data-testid="tab-overview">
            <Flame className="h-4 w-4" />
            <span>Overview</span>
          </TabsTrigger>
          <TabsTrigger value="mystery" className="flex items-center gap-2" data-testid="tab-mystery">
            <Gift className="h-4 w-4" />
            <span>Mystery</span>
          </TabsTrigger>
          <TabsTrigger value="achievements" className="flex items-center gap-2" data-testid="tab-achievements">
            <Award className="h-4 w-4" />
            <span>Achievements</span>
          </TabsTrigger>
          <TabsTrigger value="referrals" className="flex items-center gap-2" data-testid="tab-referrals">
            <UsersIcon className="h-4 w-4" />
            <span>Referrals</span>
          </TabsTrigger>
          <TabsTrigger value="challenges" className="flex items-center gap-2" data-testid="tab-challenges">
            <Target className="h-4 w-4" />
            <span>Challenges</span>
          </TabsTrigger>
          <TabsTrigger value="contests" className="flex items-center gap-2" data-testid="tab-contests">
            <Trophy className="h-4 w-4" />
            <span>Contests</span>
          </TabsTrigger>
          <TabsTrigger value="alerts" className="flex items-center gap-2" data-testid="tab-alerts">
            <Zap className="h-4 w-4" />
            <span>Live Alerts</span>
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Overview */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <StreakTracker />
            <PointsDisplay showProgress={true} />
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950 rounded-lg border border-purple-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Referrals</p>
                  <p className="text-3xl font-bold">
                    {referralData?.total_referrals ?? 0}
                  </p>
                </div>
                <UsersIcon className="h-10 w-10 text-purple-500" />
              </div>
            </div>
            
            <div className="p-6 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950 dark:to-orange-950 rounded-lg border border-amber-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Achievements</p>
                  <p className="text-3xl font-bold">{achievementsCount}</p>
                </div>
                <Award className="h-10 w-10 text-amber-500" />
              </div>
            </div>
          </div>

          {/* Tips Section */}
          <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950 dark:to-purple-950 rounded-lg border border-indigo-200">
            <h3 className="text-lg font-semibold mb-3">💡 Ways to Earn Rewards</h3>
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
                <span>Complete daily challenges for instant rewards</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Refer friends for 50 points + mystery box</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Open daily mystery box for surprise rewards</span>
              </li>
            </ul>
          </div>
        </TabsContent>

        {/* Tab 2: Mystery Rewards */}
        <TabsContent value="mystery">
          <SurpriseRewards />
        </TabsContent>

        {/* Tab 3: Achievements */}
        <TabsContent value="achievements">
          <AchievementShowcase />
        </TabsContent>

        {/* Tab 4: Referrals */}
        <TabsContent value="referrals">
          <ReferralDashboard />
        </TabsContent>

        {/* Tab 5: Challenges */}
        <TabsContent value="challenges">
          <ChallengesHub />
        </TabsContent>

        {/* Tab 6: Contests */}
        <TabsContent value="contests">
          <ContestsGallery />
        </TabsContent>

        {/* Tab 7: Live Alerts */}
        <TabsContent value="alerts">
          <FOMOTriggers />
        </TabsContent>
      </Tabs>
    </div>
  );
}
