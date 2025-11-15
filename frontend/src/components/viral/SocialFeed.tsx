import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { UserPlus, UserMinus, TrendingUp, Users, Upload, Trophy, Flame } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ActivityItem {
  user_id: string;
  usn: string;
  activity_type: string;
  details: any;
  timestamp: string;
  profile_picture?: string;
}

interface User {
  user_id: string;
  usn: string;
  department: string;
  college?: string;
  profile_picture?: string;
  level: number;
  upload_count?: number;
  followers?: number;
  score?: number;
}

export function SocialFeed() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch activity feed
  const { data: feedData, isLoading } = useQuery({
    queryKey: ["/api/social/feed"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/social/feed?limit=50");
      return await res.json();
    },
  });

  // Fetch suggested users
  const { data: suggestedData } = useQuery({
    queryKey: ["/api/social/suggested-users"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/social/suggested-users");
      return await res.json();
    },
  });

  // Fetch trending users
  const { data: trendingData } = useQuery({
    queryKey: ["/api/social/trending-users"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/social/trending-users");
      return await res.json();
    },
  });

  // Fetch following list
  const { data: followingData } = useQuery({
    queryKey: ["/api/social/following"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/social/following");
      return await res.json();
    },
  });

  // Follow mutation
  const followMutation = useMutation({
    mutationFn: async (userId: string) => {
      const res = await apiRequest("POST", `/api/social/follow/${userId}`);
      return await res.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Success!",
        description: data.message || "Now following user!",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/social/suggested-users"] });
      queryClient.invalidateQueries({ queryKey: ["/api/social/following"] });
      queryClient.invalidateQueries({ queryKey: ["/api/social/feed"] });
    },
  });

  // Unfollow mutation
  const unfollowMutation = useMutation({
    mutationFn: async (userId: string) => {
      const res = await apiRequest("DELETE", `/api/social/unfollow/${userId}`);
      return await res.json();
    },
    onSuccess: () => {
      toast({
        title: "Unfollowed",
        description: "Unfollowed user successfully",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/social/following"] });
      queryClient.invalidateQueries({ queryKey: ["/api/social/feed"] });
    },
  });

  const activities: ActivityItem[] = feedData?.activities || [];
  const suggestedUsers: User[] = suggestedData?.suggested_users || [];
  const trendingUsers: User[] = trendingData?.trending_users || [];
  const following: User[] = followingData?.following || [];

  const renderActivityItem = (activity: ActivityItem) => {
    const getActivityIcon = () => {
      switch (activity.activity_type) {
        case "upload":
          return <Upload className="h-4 w-4 text-blue-500" />;
        case "achievement":
          return <Trophy className="h-4 w-4 text-amber-500" />;
        case "level_up":
          return <TrendingUp className="h-4 w-4 text-purple-500" />;
        case "streak":
          return <Flame className="h-4 w-4 text-orange-500" />;
        default:
          return <Users className="h-4 w-4" />;
      }
    };

    const getActivityText = () => {
      switch (activity.activity_type) {
        case "upload":
          return `uploaded "${activity.details.title}"`;
        case "achievement":
          return `unlocked an achievement`;
        case "level_up":
          return `reached Level ${activity.details.level} - ${activity.details.level_name}`;
        case "streak":
          return `achieved a ${activity.details.streak} day streak! 🔥`;
        default:
          return "did something awesome";
      }
    };

    return (
      <div key={`${activity.user_id}-${activity.timestamp}`} className="flex gap-3 p-3 hover:bg-muted/50 rounded-lg transition-colors">
        <Avatar className="h-10 w-10">
          <AvatarImage src={activity.profile_picture} />
          <AvatarFallback>{activity.usn.substring(0, 2)}</AvatarFallback>
        </Avatar>

        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            {getActivityIcon()}
            <p className="text-sm">
              <span className="font-semibold">{activity.usn}</span>{" "}
              <span className="text-muted-foreground">{getActivityText()}</span>
            </p>
          </div>
          <p className="text-xs text-muted-foreground">
            {new Date(activity.timestamp).toLocaleString()}
          </p>
        </div>
      </div>
    );
  };

  const renderUserCard = (user: User, showFollowButton: boolean = true, isFollowing: boolean = false) => (
    <Card key={user.user_id} className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <Avatar className="h-12 w-12">
            <AvatarImage src={user.profile_picture} />
            <AvatarFallback>{user.usn.substring(0, 2)}</AvatarFallback>
          </Avatar>

          <div className="flex-1 space-y-2">
            <div>
              <h4 className="font-semibold text-sm">{user.usn}</h4>
              <p className="text-xs text-muted-foreground">
                {user.department} • {user.college || ""}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                Level {user.level}
              </Badge>
              {user.upload_count !== undefined && (
                <span className="text-xs text-muted-foreground">
                  {user.upload_count} uploads
                </span>
              )}
              {user.followers !== undefined && (
                <span className="text-xs text-muted-foreground">
                  {user.followers} followers
                </span>
              )}
            </div>

            {showFollowButton && (
              isFollowing ? (
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full"
                  onClick={() => unfollowMutation.mutate(user.user_id)}
                  disabled={unfollowMutation.isPending}
                  data-testid={`unfollow-${user.user_id}`}
                >
                  <UserMinus className="h-3 w-3 mr-1" />
                  Unfollow
                </Button>
              ) : (
                <Button
                  size="sm"
                  className="w-full"
                  onClick={() => followMutation.mutate(user.user_id)}
                  disabled={followMutation.isPending}
                  data-testid={`follow-${user.user_id}`}
                >
                  <UserPlus className="h-3 w-3 mr-1" />
                  Follow
                </Button>
              )
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading social feed...</div>;
  }

  return (
    <div className="space-y-6" data-testid="social-feed">
      <Tabs defaultValue="feed" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="feed">Feed</TabsTrigger>
          <TabsTrigger value="following">Following</TabsTrigger>
          <TabsTrigger value="suggested">Suggested</TabsTrigger>
          <TabsTrigger value="trending">Trending</TabsTrigger>
        </TabsList>

        {/* Activity Feed */}
        <TabsContent value="feed">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Activity Feed
              </CardTitle>
            </CardHeader>
            <CardContent>
              {activities.length === 0 ? (
                <div className="text-center py-12">
                  <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground mb-4">
                    Follow users to see their activity here!
                  </p>
                  <Button onClick={() => document.querySelector('[value="suggested"]')?.dispatchEvent(new Event('click'))}>
                    Find Users to Follow
                  </Button>
                </div>
              ) : (
                <div className="space-y-1">
                  {activities.map(renderActivityItem)}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Following Tab */}
        <TabsContent value="following">
          <div>
            <h3 className="text-lg font-semibold mb-4">
              Following ({following.length})
            </h3>
            {following.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <p className="text-muted-foreground">You're not following anyone yet</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {following.map((user) => renderUserCard(user, true, true))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* Suggested Users Tab */}
        <TabsContent value="suggested">
          <div>
            <h3 className="text-lg font-semibold mb-4">
              Suggested Users
            </h3>
            {suggestedUsers.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <p className="text-muted-foreground">No suggestions available</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {suggestedUsers.map((user) => renderUserCard(user))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* Trending Users Tab */}
        <TabsContent value="trending">
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Trending This Week
            </h3>
            {trendingUsers.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <p className="text-muted-foreground">No trending users this week</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {trendingUsers.map((user) => renderUserCard(user))}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
