import { useEffect, useState } from "react";
import { Trophy, Medal, Award, TrendingUp, Users } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { apiRequest } from "@/lib/api";

interface LeaderboardEntry {
  user_id: string;
  usn: string;
  rank: number;
  score: number;
  college?: string;
  department: string;
  profile_picture?: string;
  streak: number;
  level: number;
}

interface LeaderboardData {
  type: string;
  rankings: LeaderboardEntry[];
  user_rank: number | null;
  total_users: number;
  updated_at: string;
}

export function Leaderboard() {
  const [allIndiaData, setAllIndiaData] = useState<LeaderboardData | null>(null);
  const [collegeData, setCollegeData] = useState<LeaderboardData | null>(null);
  const [departmentData, setDepartmentData] = useState<LeaderboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all-india");

  useEffect(() => {
    fetchLeaderboards();
  }, []);

  const fetchLeaderboards = async () => {
    try {
      setLoading(true);
      
      // Fetch all three leaderboards in parallel
      const [allIndia, college, department] = await Promise.all([
        apiRequest("/api/leaderboards/all-india?limit=50"),
        apiRequest("/api/leaderboards/college?limit=50").catch(() => null),
        apiRequest("/api/leaderboards/department?limit=50")
      ]);

      setAllIndiaData(allIndia);
      setCollegeData(college);
      setDepartmentData(department);
    } catch (error) {
      console.error("Failed to fetch leaderboards:", error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="h-5 w-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />;
    if (rank === 3) return <Medal className="h-5 w-5 text-amber-700" />;
    return <span className="text-sm font-bold text-muted-foreground">#{rank}</span>;
  };

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) return "bg-gradient-to-r from-yellow-400 to-yellow-600 text-white";
    if (rank === 2) return "bg-gradient-to-r from-gray-300 to-gray-500 text-white";
    if (rank === 3) return "bg-gradient-to-r from-amber-600 to-amber-800 text-white";
    return "bg-muted";
  };

  const renderLeaderboardEntry = (entry: LeaderboardEntry, isCurrentUser: boolean = false) => {
    return (
      <div
        key={entry.user_id}
        className={`flex items-center gap-4 p-4 rounded-lg transition-colors ${
          isCurrentUser 
            ? "bg-primary/10 border-2 border-primary" 
            : "bg-muted/50 hover:bg-muted"
        }`}
        data-testid={`leaderboard-entry-${entry.rank}`}
      >
        {/* Rank */}
        <div className="flex-shrink-0 w-12 flex justify-center">
          {entry.rank <= 3 ? (
            <Badge className={getRankBadgeColor(entry.rank)}>
              {entry.rank}
            </Badge>
          ) : (
            getRankIcon(entry.rank)
          )}
        </div>

        {/* User info */}
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <Avatar className="h-10 w-10">
            <AvatarImage src={entry.profile_picture} />
            <AvatarFallback>
              {entry.usn.slice(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-semibold truncate">{entry.usn}</p>
              {isCurrentUser && (
                <Badge variant="secondary" className="text-xs">You</Badge>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>{entry.department}</span>
              {entry.streak > 0 && (
                <span className="flex items-center gap-1">
                  🔥 {entry.streak}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 flex-shrink-0">
          <div className="text-right">
            <p className="text-lg font-bold">{entry.score.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground">points</p>
          </div>
          <Badge variant="outline" className="flex items-center gap-1">
            <Award className="h-3 w-3" />
            Lvl {entry.level}
          </Badge>
        </div>
      </div>
    );
  };

  const renderLeaderboard = (data: LeaderboardData | null, emptyMessage: string) => {
    if (!data) {
      return (
        <div className="text-center py-8">
          <Users className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
          <p className="text-muted-foreground">{emptyMessage}</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {/* Your rank */}
        {data.user_rank && data.user_rank > 10 && (
          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="pt-4">
              <p className="text-sm font-medium mb-2">Your Ranking:</p>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">#{data.user_rank}</span>
                <span className="text-sm text-muted-foreground">
                  out of {data.total_users} users
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Top rankings */}
        <div className="space-y-2">
          {data.rankings.slice(0, 50).map((entry) => 
            renderLeaderboardEntry(entry, data.user_rank === entry.rank)
          )}
        </div>

        {data.rankings.length === 0 && (
          <div className="text-center py-8">
            <TrendingUp className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
            <p className="text-muted-foreground">No rankings available yet</p>
            <p className="text-sm text-muted-foreground mt-2">
              Be the first! Upload notes to get on the leaderboard.
            </p>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <Card data-testid="leaderboard-loading">
        <CardHeader>
          <CardTitle>Loading Leaderboards...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-16 bg-muted rounded-lg"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full" data-testid="leaderboard">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Trophy className="h-6 w-6 text-yellow-500" />
          <CardTitle>Leaderboards</CardTitle>
        </div>
        <CardDescription>
          See how you rank against other contributors
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="all-india" data-testid="tab-all-india">
              🇮🇳 All India
            </TabsTrigger>
            <TabsTrigger value="college" data-testid="tab-college">
              🏛️ College
            </TabsTrigger>
            <TabsTrigger value="department" data-testid="tab-department">
              📚 Department
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all-india" className="mt-4">
            {renderLeaderboard(allIndiaData, "All-India leaderboard coming soon")}
          </TabsContent>

          <TabsContent value="college" className="mt-4">
            {renderLeaderboard(collegeData, "College leaderboard not available")}
          </TabsContent>

          <TabsContent value="department" className="mt-4">
            {renderLeaderboard(departmentData, "Department leaderboard coming soon")}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
