import { useEffect, useState } from "react";
import { Star, TrendingUp, Award } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { apiRequest } from "@/lib/api";

interface PointsData {
  total_points: number;
  level: number;
  level_name: string;
  points_to_next_level: number;
  progress_percentage: number;
}

interface PointsDisplayProps {
  compact?: boolean;
  showProgress?: boolean;
}

export function PointsDisplay({ compact = false, showProgress = true }: PointsDisplayProps) {
  const [pointsData, setPointsData] = useState<PointsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPointsData();
  }, []);

  const fetchPointsData = async () => {
    try {
      const response = await apiRequest("/api/gamification/points");
      setPointsData(response);
    } catch (error) {
      console.error("Failed to fetch points data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-10 bg-muted rounded w-32"></div>
      </div>
    );
  }

  if (!pointsData) {
    return null;
  }

  const getLevelColor = (level: number) => {
    if (level >= 50) return "from-purple-500 to-pink-500";
    if (level >= 40) return "from-blue-500 to-purple-500";
    if (level >= 30) return "from-green-500 to-blue-500";
    if (level >= 20) return "from-yellow-500 to-green-500";
    if (level >= 10) return "from-orange-500 to-yellow-500";
    if (level >= 5) return "from-red-500 to-orange-500";
    return "from-gray-500 to-gray-600";
  };

  const getLevelEmoji = (levelName: string) => {
    const emojiMap: Record<string, string> = {
      "Newbie": "🌱",
      "Helper": "🤝",
      "Expert": "⭐",
      "Master": "🏆",
      "Champion": "👑",
      "Elite": "💎",
      "Legend": "🔥"
    };
    return emojiMap[levelName] || "🌟";
  };

  if (compact) {
    return (
      <div className="flex items-center gap-3" data-testid="points-display-compact">
        <Badge 
          className={`bg-gradient-to-r ${getLevelColor(pointsData.level)} text-white px-3 py-1.5`}
          data-testid="level-badge"
        >
          <Award className="h-3 w-3 mr-1" />
          Level {pointsData.level}
        </Badge>
        <div className="flex items-center gap-1 text-sm font-medium">
          <Star className="h-4 w-4 text-yellow-500" />
          <span data-testid="points-value">{pointsData.total_points.toLocaleString()}</span>
        </div>
      </div>
    );
  }

  return (
    <Card className="w-full" data-testid="points-display">
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Level Badge */}
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-3xl">{getLevelEmoji(pointsData.level_name)}</span>
                <div>
                  <h3 className="text-2xl font-bold" data-testid="level-name">
                    {pointsData.level_name}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Level {pointsData.level}
                  </p>
                </div>
              </div>
            </div>
            <Badge 
              variant="outline" 
              className={`bg-gradient-to-r ${getLevelColor(pointsData.level)} text-white border-none px-4 py-2 text-lg font-bold`}
            >
              {pointsData.total_points.toLocaleString()} pts
            </Badge>
          </div>

          {/* Progress to next level */}
          {showProgress && pointsData.points_to_next_level > 0 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Progress to next level</span>
                <span className="font-medium">
                  {pointsData.points_to_next_level.toLocaleString()} pts needed
                </span>
              </div>
              <Progress 
                value={pointsData.progress_percentage} 
                className="h-2" 
                data-testid="level-progress"
              />
              <p className="text-xs text-muted-foreground text-right">
                {pointsData.progress_percentage.toFixed(1)}% complete
              </p>
            </div>
          )}

          {pointsData.level >= 50 && (
            <div className="p-3 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-lg">
              <p className="text-sm font-medium text-purple-800 dark:text-purple-200">
                🎉 Maximum level reached! You're a NotesHub Legend!
              </p>
            </div>
          )}

          {/* How to earn points */}
          <div className="pt-2 border-t">
            <p className="text-xs text-muted-foreground mb-2">💡 Earn points by:</p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-green-500" />
                <span>Upload notes (+100)</span>
              </div>
              <div className="flex items-center gap-1">
                <Star className="h-3 w-3 text-yellow-500" />
                <span>Daily streak (+5)</span>
              </div>
              <div className="flex items-center gap-1">
                <Award className="h-3 w-3 text-blue-500" />
                <span>Get downloads (+5 each)</span>
              </div>
              <div className="flex items-center gap-1">
                <Award className="h-3 w-3 text-purple-500" />
                <span>Referrals (+50)</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
