import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  StudyGroups,
  SocialFeed,
  AIRecommendations
} from "@/components/viral";
import { User, Users, MessageCircle, Brain, UserPlus, TrendingUp } from "lucide-react";
import { Link } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useAuth } from "@/hooks/use-auth";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function CommunityHub() {
  const { user } = useAuth();

  // Fetch user rank
  const { data: leaderboardData } = useQuery({
    queryKey: ["/api/leaderboards/all-india"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/leaderboards/all-india");
      return await res.json();
    },
  });

  // Fetch user stats
  const { data: userStats } = useQuery({
    queryKey: ["/api/gamification/points"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/gamification/points");
      return await res.json();
    },
  });

  // Fetch following data
  const { data: followingData } = useQuery({
    queryKey: ["/api/social/following"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/social/following");
      return await res.json();
    },
  });

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl" data-testid="community-hub">
      {/* Hero Section */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
          <Users className="h-10 w-10 text-primary" />
          Community Hub
        </h1>
        <p className="text-muted-foreground text-lg">
          Connect with friends, join groups, and grow together!
        </p>
      </div>

      {/* 3 Tabs for Community */}
      <Tabs defaultValue="feed" className="space-y-6">
        <TabsList className="grid w-full grid-cols-1 lg:grid-cols-3 gap-2">
          <TabsTrigger value="feed" className="flex items-center gap-2" data-testid="tab-feed">
            <MessageCircle className="h-4 w-4" />
            <span>Feed</span>
          </TabsTrigger>
          <TabsTrigger value="groups" className="flex items-center gap-2" data-testid="tab-groups">
            <Users className="h-4 w-4" />
            <span>Groups</span>
          </TabsTrigger>
          <TabsTrigger value="ai" className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-pink-600 text-white" data-testid="tab-ai">
            <Brain className="h-4 w-4" />
            <span>AI Buddy</span>
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Social Feed + Following */}
        <TabsContent value="feed" className="space-y-6">
          <SocialFeed />
          
          {/* Following Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus className="h-5 w-5" />
                People You Follow
              </CardTitle>
            </CardHeader>
            <CardContent>
              {followingData?.following && followingData.following.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {followingData.following.map((followedUser: any) => (
                    <div 
                      key={followedUser.user_id} 
                      className="p-4 border rounded-lg hover:bg-accent transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <Avatar className="h-12 w-12">
                          <AvatarFallback>
                            {followedUser.usn?.substring(0, 2).toUpperCase() || "U"}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold truncate">{followedUser.usn}</p>
                          <p className="text-sm text-muted-foreground">{followedUser.department}</p>
                        </div>
                        {followedUser.level && (
                          <Badge variant="secondary">Lvl {followedUser.level}</Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <UserPlus className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground">You're not following anyone yet</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    Explore the leaderboard and social feed to find people to follow!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Study Groups */}
        <TabsContent value="groups">
          <StudyGroups />
        </TabsContent>

        {/* Tab 3: AI Buddy */}
        <TabsContent value="ai">
          <AIRecommendations />
        </TabsContent>
      </Tabs>
    </div>
  );
}
