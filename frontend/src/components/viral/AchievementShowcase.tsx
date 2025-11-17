import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Trophy, Lock, Star, TrendingUp } from "lucide-react";
import { useState, useEffect } from "react";
import { AchievementCelebration } from "./AchievementCelebration";
import { useToast } from "@/hooks/use-toast";

interface Achievement {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  rarity: string;
  points: number;
  unlocked: boolean;
  unlocked_at?: string;
  progress?: {
    current: number;
    required: number;
    percentage: number;
  };
}

const rarityColors = {
  common: "bg-gray-500",
  uncommon: "bg-green-500",
  rare: "bg-blue-500",
  epic: "bg-purple-500",
  legendary: "bg-amber-500"
};

const rarityTextColors = {
  common: "text-gray-700 dark:text-gray-300",
  uncommon: "text-green-700 dark:text-green-300",
  rare: "text-blue-700 dark:text-blue-300",
  epic: "text-purple-700 dark:text-purple-300",
  legendary: "text-amber-700 dark:text-amber-300"
};

export function AchievementShowcase() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [celebratingAchievement, setCelebratingAchievement] = useState<Achievement | null>(null);
  const { toast } = useToast();

  // Fetch all achievements
  const { data: achievementsData, isLoading } = useQuery({
    queryKey: ["/api/achievements/all"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/achievements/all");
      return await res.json();
    },
  });

  // Fetch achievement stats
  const { data: statsData } = useQuery({
    queryKey: ["/api/achievements/stats"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/achievements/stats");
      return await res.json();
    },
  });

  // Fetch categories
  const { data: categoriesData } = useQuery({
    queryKey: ["/api/achievements/categories"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/achievements/categories");
      return await res.json();
    },
  });

  // Poll for newly unlocked achievements
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await apiRequest("GET", "/api/achievements/recent-unlock");
        const data = await res.json();
        if (data.achievement && !data.shown) {
          setCelebratingAchievement(data.achievement);
          // Mark as shown
          await apiRequest("POST", `/api/achievements/${data.achievement.id}/mark-shown`);
        }
      } catch (error) {
        console.error("Failed to check for new achievements:", error);
      }
    }, 5000); // Check every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading achievements...</div>;
  }

  const achievements: Achievement[] = achievementsData || [];
  const stats = statsData || {};
  const categories = categoriesData?.categories || {};

  const filteredAchievements = selectedCategory === "all" 
    ? achievements 
    : achievements.filter(a => a.category === selectedCategory);

  return (
    <div className="space-y-6" data-testid="achievement-showcase">
      {/* Stats Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Achievement Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Overall Completion</span>
                <span className="font-bold">{stats.unlocked || 0}/{stats.total_achievements || 0}</span>
              </div>
              <Progress value={stats.completion_percentage || 0} className="h-3" />
              <p className="text-xs text-muted-foreground mt-1">
                {stats.completion_percentage?.toFixed(1) || 0}% Complete
              </p>
            </div>

            {/* Rarity Breakdown */}
            <div className="grid grid-cols-5 gap-2 text-center text-xs">
              {Object.entries(stats.rarity_breakdown || {}).map(([rarity, count]) => (
                <div key={rarity} className="space-y-1">
                  <div className={`h-2 rounded ${rarityColors[rarity as keyof typeof rarityColors]}`} />
                  <div className="font-semibold capitalize">{rarity}</div>
                  <div className="text-muted-foreground">{count as number}</div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Category Tabs */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="upload">Upload</TabsTrigger>
          <TabsTrigger value="download">Download</TabsTrigger>
          <TabsTrigger value="social">Social</TabsTrigger>
          <TabsTrigger value="streak">Streak</TabsTrigger>
          <TabsTrigger value="hidden">Hidden</TabsTrigger>
        </TabsList>

        <TabsContent value={selectedCategory} className="mt-6">
          {/* Achievement Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredAchievements.map((achievement) => (
              <Card 
                key={achievement.id} 
                className={`relative overflow-hidden transition-all ${
                  achievement.unlocked 
                    ? 'border-2 border-primary' 
                    : 'opacity-60'
                }`}
                data-testid={`achievement-${achievement.id}`}
              >
                {/* Rarity Indicator */}
                <div className={`absolute top-0 right-0 w-20 h-20 ${rarityColors[achievement.rarity as keyof typeof rarityColors]} opacity-10 rounded-bl-full`} />
                
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    {/* Icon */}
                    <div className={`text-4xl ${achievement.unlocked ? '' : 'grayscale opacity-50'}`}>
                      {achievement.unlocked ? achievement.icon : <Lock className="h-10 w-10" />}
                    </div>

                    <div className="flex-1 space-y-2">
                      {/* Title and Rarity */}
                      <div>
                        <h3 className="font-bold text-sm">{achievement.name}</h3>
                        <Badge variant="outline" className={`text-xs ${rarityTextColors[achievement.rarity as keyof typeof rarityTextColors]}`}>
                          {achievement.rarity}
                        </Badge>
                      </div>

                      {/* Description */}
                      <p className="text-xs text-muted-foreground">
                        {achievement.description}
                      </p>

                      {/* Points */}
                      <div className="flex items-center gap-1 text-xs">
                        <Star className="h-3 w-3 text-amber-500" />
                        <span className="font-semibold">{achievement.points} pts</span>
                      </div>

                      {/* Unlock Status */}
                      {achievement.unlocked ? (
                        <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                          ✓ Unlocked {achievement.unlocked_at ? new Date(achievement.unlocked_at).toLocaleDateString() : ''}
                        </div>
                      ) : (
                        <div className="text-xs text-muted-foreground">
                          🔒 Locked
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredAchievements.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <Trophy className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No achievements in this category yet.</p>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Achievement Celebration Modal */}
      <AchievementCelebration
        achievement={celebratingAchievement}
        onClose={() => setCelebratingAchievement(null)}
        onShare={async () => {
          // Award bonus points for sharing
          try {
            await apiRequest("POST", "/api/achievements/share-bonus");
            toast({
              title: "🎉 Bonus Points Earned!",
              description: "+50 points for sharing your achievement!",
            });
          } catch (error) {
            console.error("Failed to award share bonus:", error);
          }
        }}
      />
    </div>
  );
}
