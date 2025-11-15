import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Trophy, Target, Swords, Users, TrendingUp, Calendar, CheckCircle2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DailyChallenge {
  id: string;
  type: string;
  title: string;
  description: string;
  target: number;
  current_progress: number;
  completed: boolean;
  reward_points: number;
}

interface Battle {
  id: string;
  opponent_usn: string;
  challenge_type: string;
  status: string;
  challenger_score: number;
  opponent_score: number;
  days_remaining: number;
  is_challenger: boolean;
}

export function ChallengesHub() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch daily challenges
  const { data: challengesData, isLoading } = useQuery({
    queryKey: ["/api/challenges/daily"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/challenges/daily");
      return await res.json();
    },
  });

  // Fetch my battles
  const { data: battlesData } = useQuery({
    queryKey: ["/api/challenges/battles/my"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/challenges/battles/my?status=active");
      return await res.json();
    },
  });

  // Fetch department war
  const { data: deptWarData } = useQuery({
    queryKey: ["/api/challenges/department-war"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/challenges/department-war");
      return await res.json();
    },
  });

  // Fetch college war
  const { data: collegeWarData } = useQuery({
    queryKey: ["/api/challenges/college-war"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/challenges/college-war");
      return await res.json();
    },
  });

  // Fetch challenge stats
  const { data: statsData } = useQuery({
    queryKey: ["/api/challenges/stats"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/challenges/stats");
      return await res.json();
    },
  });

  const challenges: DailyChallenge[] = challengesData?.challenges || [];
  const battles: Battle[] = battlesData?.battles || [];
  const deptRankings = deptWarData?.rankings || [];
  const collegeRankings = collegeWarData?.rankings || [];
  const stats = statsData || {};

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading challenges...</div>;
  }

  return (
    <div className="space-y-6" data-testid="challenges-hub">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary">
                {challengesData?.completed || 0}/{challengesData?.total || 0}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Daily Challenges</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-green-500">
                {stats.battle_wins || 0}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Battle Wins</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-500">
                {stats.win_rate?.toFixed(0) || 0}%
              </p>
              <p className="text-xs text-muted-foreground mt-1">Win Rate</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-500">
                #{deptWarData?.user_department_rank || "--"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Dept. Rank</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="daily" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="daily">Daily</TabsTrigger>
          <TabsTrigger value="battles">Battles</TabsTrigger>
          <TabsTrigger value="department">Dept War</TabsTrigger>
          <TabsTrigger value="college">College War</TabsTrigger>
        </TabsList>

        {/* Daily Challenges Tab */}
        <TabsContent value="daily">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Today's Challenges
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {challenges.map((challenge) => (
                <div
                  key={challenge.id}
                  className={`p-4 rounded-lg border ${
                    challenge.completed ? "bg-green-50 dark:bg-green-950 border-green-200" : "bg-muted/50"
                  }`}
                  data-testid={`challenge-${challenge.type}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold">{challenge.title}</h4>
                        {challenge.completed && (
                          <CheckCircle2 className="h-5 w-5 text-green-500" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {challenge.description}
                      </p>
                    </div>
                    <Badge variant={challenge.completed ? "default" : "outline"}>
                      {challenge.reward_points} pts
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Progress</span>
                      <span className="font-semibold">
                        {challenge.current_progress}/{challenge.target}
                      </span>
                    </div>
                    <Progress
                      value={(challenge.current_progress / challenge.target) * 100}
                      className="h-2"
                    />
                  </div>
                </div>
              ))}

              {challenges.length === 0 && (
                <div className="text-center py-12">
                  <Target className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground">No challenges available today</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Battles Tab */}
        <TabsContent value="battles">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Swords className="h-5 w-5" />
                Active Battles
              </CardTitle>
            </CardHeader>
            <CardContent>
              {battles.length === 0 ? (
                <div className="text-center py-12">
                  <Swords className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground mb-4">No active battles</p>
                  <Button>Challenge Someone</Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {battles.map((battle) => (
                    <div
                      key={battle.id}
                      className="p-4 rounded-lg border bg-muted/50"
                      data-testid={`battle-${battle.id}`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-semibold">vs {battle.opponent_usn}</h4>
                          <p className="text-sm text-muted-foreground capitalize">
                            {battle.challenge_type} Challenge
                          </p>
                        </div>
                        <Badge>{battle.days_remaining} days left</Badge>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-center">
                        <div>
                          <p className="text-2xl font-bold text-primary">
                            {battle.is_challenger ? battle.challenger_score : battle.opponent_score}
                          </p>
                          <p className="text-xs text-muted-foreground">You</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-muted-foreground">
                            {battle.is_challenger ? battle.opponent_score : battle.challenger_score}
                          </p>
                          <p className="text-xs text-muted-foreground">Opponent</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Department War Tab */}
        <TabsContent value="department">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Department Rankings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {deptRankings.slice(0, 10).map((dept: any) => (
                  <div
                    key={dept.rank}
                    className={`flex items-center justify-between p-3 rounded-lg ${
                      dept.department === deptWarData?.user_department
                        ? "bg-primary/10 border-2 border-primary"
                        : "bg-muted/50"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 font-bold">
                        {dept.rank}
                      </div>
                      <div>
                        <p className="font-semibold">{dept.department}</p>
                        <p className="text-xs text-muted-foreground">
                          {dept.member_count} members
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary">{dept.total_points.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">points</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* College War Tab */}
        <TabsContent value="college">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5" />
                College Rankings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {collegeRankings.slice(0, 10).map((college: any) => (
                  <div
                    key={college.rank}
                    className={`flex items-center justify-between p-3 rounded-lg ${
                      college.college === collegeWarData?.user_college
                        ? "bg-primary/10 border-2 border-primary"
                        : "bg-muted/50"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 font-bold">
                        {college.rank}
                      </div>
                      <div>
                        <p className="font-semibold text-sm">{college.college}</p>
                        <p className="text-xs text-muted-foreground">
                          {college.member_count} students
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary">{college.total_points.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">points</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
