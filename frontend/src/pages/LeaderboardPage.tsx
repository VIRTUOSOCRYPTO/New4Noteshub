import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  StreakTracker, 
  PointsDisplay,
  Leaderboard,
  ReferralDashboard,
  AchievementShowcase,
  ExamCountdown
} from "@/components/viral";
import { Trophy, Flame, Users, Award, Calendar, Star } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { usePageVisits } from "@/hooks/use-page-visits";

export default function LeaderboardPage() {
  usePageVisits('leaderboard');

  // Fetch user rank
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
    <div className="container mx-auto py-8 px-4 max-w-7xl" data-testid="leaderboard-page">
      {/* Hero Section */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
          <Trophy className="h-10 w-10 text-yellow-500" />
          Leaderboard & Progress
        </h1>
        <p className="text-muted-foreground text-lg">
          Track your progress, compete with peers, and unlock achievements!
        </p>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Your Rank</p>
              <p className="text-3xl font-bold">
                {leaderboardData?.user_rank ? `#${leaderboardData.user_rank}` : "#--"}
              </p>
            </div>
            <Trophy className="h-10 w-10" style={{ color: 'rgb(15 23 42 / var(--tw-bg-opacity, 1))' }} />
          </div>
        </div>
        
        <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Referrals</p>
              <p className="text-3xl font-bold">
                {referralData?.total_referrals ?? 0}
              </p>
            </div>
            <Users className="h-10 w-10" style={{ color: 'rgb(15 23 42 / var(--tw-bg-opacity, 1))' }} />
          </div>
        </div>
        
        <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Achievements</p>
              <p className="text-3xl font-bold">{achievementsCount}</p>
            </div>
            <Award className="h-10 w-10" style={{ color: 'rgb(15 23 42 / var(--tw-bg-opacity, 1))' }} />
          </div>
        </div>
      </div>

      {/* Tabs for different sections */}
      <Tabs defaultValue="rankings" className="space-y-6">
        <TabsList className="grid w-full grid-cols-1 lg:grid-cols-3 gap-2">
          <TabsTrigger value="rankings" className="flex items-center gap-2" data-testid="tab-rankings">
            <Trophy className="h-4 w-4" />
            <span>Rankings</span>
          </TabsTrigger>
          <TabsTrigger value="achievements" className="flex items-center gap-2" data-testid="tab-achievements">
            <Award className="h-4 w-4" />
            <span>Achievements</span>
          </TabsTrigger>
          <TabsTrigger value="exams" className="flex items-center gap-2" data-testid="tab-exams">
            <Calendar className="h-4 w-4" />
            <span>Exams</span>
          </TabsTrigger>
        </TabsList>

        {/* Rankings Tab - Merged with Overview */}
        <TabsContent value="rankings" className="space-y-6">
          {/* Overview Stats Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <StreakTracker />
            <PointsDisplay showProgress={true} />
          </div>

          {/* Leaderboard */}
          <Leaderboard />

          {/* Tips Section */}
          <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
            <h3 className="text-lg font-semibold mb-3">💡 How to Earn Points</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Upload notes:</strong> Earn 100 points for each quality note</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Daily streak:</strong> Get 5 bonus points for consistent activity</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Downloads:</strong> Earn 5 points when your notes are downloaded</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Referrals:</strong> Get 50 points for each friend you invite</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Share on WhatsApp:</strong> Earn bonus points for sharing notes</span>
              </li>
            </ul>
          </div>
        </TabsContent>

        {/* Achievements Tab */}
        <TabsContent value="achievements">
          <AchievementShowcase />
        </TabsContent>

        {/* Exams Tab */}
        <TabsContent value="exams">
          <ExamCountdown />
        </TabsContent>
      </Tabs>
    </div>
  );
}
