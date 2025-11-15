import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Trophy, ThumbsUp, Calendar, TrendingUp, Award } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Contest {
  id: string;
  title: string;
  description: string;
  category: string;
  end_date: string;
  status: string;
  entry_count: number;
  days_remaining: number;
  winner_usn?: string;
}

interface ContestEntry {
  id: string;
  user_usn: string;
  note_title: string;
  votes: number;
  description?: string;
}

export function ContestsGallery() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch active contests
  const { data: activeData, isLoading } = useQuery({
    queryKey: ["/api/contests/active"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/contests/active");
      return await res.json();
    },
  });

  // Fetch past contests
  const { data: pastData } = useQuery({
    queryKey: ["/api/contests/past"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/contests/past");
      return await res.json();
    },
  });

  // Fetch my entries
  const { data: myEntriesData } = useQuery({
    queryKey: ["/api/contests/my-entries"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/contests/my-entries");
      return await res.json();
    },
  });

  const activeContests: Contest[] = activeData?.contests || [];
  const pastContests: Contest[] = pastData?.contests || [];
  const myEntries = myEntriesData?.entries || [];

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading contests...</div>;
  }

  return (
    <div className="space-y-6" data-testid="contests-gallery">
      <Tabs defaultValue="active" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="active">Active Contests</TabsTrigger>
          <TabsTrigger value="past">Past Winners</TabsTrigger>
          <TabsTrigger value="my-entries">My Entries</TabsTrigger>
        </TabsList>

        {/* Active Contests Tab */}
        <TabsContent value="active">
          {activeContests.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Trophy className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">No active contests at the moment</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {activeContests.map((contest) => (
                <Card key={contest.id} className="hover:shadow-lg transition-shadow" data-testid={`contest-${contest.id}`}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{contest.title}</CardTitle>
                        <Badge variant="outline" className="mt-2">
                          {contest.category}
                        </Badge>
                      </div>
                      <Trophy className="h-6 w-6 text-amber-500" />
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      {contest.description}
                    </p>

                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>{contest.days_remaining} days left</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        <span>{contest.entry_count} entries</span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button 
                        className="flex-1" 
                        onClick={() => window.location.href = `/contests/${contest.id}`}
                        data-testid={`view-contest-${contest.id}`}
                      >
                        View Entries
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => window.location.href = `/contests/${contest.id}/submit`}
                        data-testid={`enter-contest-${contest.id}`}
                      >
                        Submit Entry
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Past Winners Tab */}
        <TabsContent value="past">
          {pastContests.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Award className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">No past contests yet</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {pastContests.map((contest) => (
                <Card key={contest.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-2">{contest.title}</h3>
                        <Badge variant="outline">{contest.category}</Badge>
                        
                        {contest.winner_usn && (
                          <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-950 rounded-lg border border-amber-200">
                            <div className="flex items-center gap-2">
                              <Trophy className="h-5 w-5 text-amber-500" />
                              <span className="font-semibold">Winner: {contest.winner_usn}</span>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => window.location.href = `/contests/${contest.id}`}
                      >
                        View Details
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* My Entries Tab */}
        <TabsContent value="my-entries">
          {myEntries.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground mb-4">You haven't entered any contests yet</p>
                <Button onClick={() => window.location.href = "/contests"}>
                  Browse Contests
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {myEntries.map((entry: any) => (
                <Card key={entry.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold">{entry.contest_title}</h4>
                        <p className="text-sm text-muted-foreground mt-1">
                          Status: <Badge variant={entry.contest_status === "active" ? "default" : "secondary"}>
                            {entry.contest_status}
                          </Badge>
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center gap-1 text-primary">
                          <ThumbsUp className="h-4 w-4" />
                          <span className="font-bold">{entry.votes}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">votes</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
