import { useEffect, useState } from "react";
import { Flame, Trophy, TrendingUp } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { apiRequest } from "@/lib/api";

interface StreakData {
  current_streak: number;
  longest_streak: number;
  last_activity_date: string | null;
  days_until_next_milestone: number;
  next_milestone: number;
}

export function StreakTracker() {
  const [streakData, setStreakData] = useState<StreakData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStreakData();
  }, []);

  const fetchStreakData = async () => {
    try {
      const response = await apiRequest("/api/gamification/streak");
      setStreakData(response);
    } catch (error) {
      console.error("Failed to fetch streak data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="w-full" data-testid="streak-tracker-loading">
        <CardContent className="pt-6">
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-muted rounded w-1/2"></div>
            <div className="h-8 bg-muted rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!streakData) {
    return null;
  }

  const progress = ((streakData.next_milestone - streakData.days_until_next_milestone) / streakData.next_milestone) * 100;

  return (
    <Card className="w-full bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700" data-testid="streak-tracker">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Flame className="h-6 w-6 text-orange-500" />
            <CardTitle className="text-2xl font-bold">
              {streakData.current_streak} Day Streak
            </CardTitle>
          </div>
          {streakData.current_streak >= 7 && (
            <Badge variant="default" className="bg-orange-500 hover:bg-orange-600">
              🔥 On Fire!
            </Badge>
          )}
        </div>
        <CardDescription>
          Keep your streak alive by staying active daily!
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress to next milestone */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              Next Milestone: {streakData.next_milestone} days
            </span>
            <span className="font-medium">
              {streakData.days_until_next_milestone} days to go
            </span>
          </div>
          <Progress value={progress} className="h-2" data-testid="streak-progress" />
        </div>

        {/* Longest streak */}
        <div className="flex items-center justify-between p-3 bg-white/50 dark:bg-black/20 rounded-lg">
          <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-amber-500" />
            <span className="text-sm font-medium">Longest Streak</span>
          </div>
          <span className="text-lg font-bold">{streakData.longest_streak} days</span>
        </div>

        {/* Motivational message */}
        {streakData.current_streak === 0 && (
          <div className="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
            <p className="text-sm text-orange-800 dark:text-orange-200">
              💡 Upload or download a note to start your streak!
            </p>
          </div>
        )}

        {streakData.current_streak > 0 && streakData.current_streak < 7 && (
          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              🎯 Keep going! {7 - streakData.current_streak} more days to earn the Bronze badge!
            </p>
          </div>
        )}

        {streakData.current_streak >= 7 && streakData.current_streak < 30 && (
          <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
            <p className="text-sm text-green-800 dark:text-green-200">
              🌟 Amazing! {30 - streakData.current_streak} more days to Silver badge!
            </p>
          </div>
        )}

        {streakData.current_streak >= 30 && (
          <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <p className="text-sm text-purple-800 dark:text-purple-200">
              👑 You're a legend! Keep your streak alive!
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
