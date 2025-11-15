import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Gift, Sparkles, Ticket, Cake, Trophy, Star } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

export function SurpriseRewards() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isOpening, setIsOpening] = useState(false);

  // Fetch mystery box info
  const { data: mysteryBoxData } = useQuery({
    queryKey: ["/api/rewards/mystery-box"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/rewards/mystery-box");
      return await res.json();
    },
  });

  // Fetch lucky draw status
  const { data: luckyDrawData } = useQuery({
    queryKey: ["/api/rewards/lucky-draw"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/rewards/lucky-draw");
      return await res.json();
    },
  });

  // Fetch birthday special
  const { data: birthdayData } = useQuery({
    queryKey: ["/api/rewards/birthday-special"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/rewards/birthday-special");
      return await res.json();
    },
  });

  // Fetch milestone rewards
  const { data: milestonesData } = useQuery({
    queryKey: ["/api/rewards/milestone-rewards"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/rewards/milestone-rewards");
      return await res.json();
    },
  });

  // Open mystery box mutation
  const openBoxMutation = useMutation({
    mutationFn: async () => {
      const res = await apiRequest("POST", "/api/rewards/mystery-box/open");
      return await res.json();
    },
    onSuccess: (data) => {
      setIsOpening(false);
      toast({
        title: "🎁 Mystery Box Opened!",
        description: data.message,
      });
      queryClient.invalidateQueries({ queryKey: ["/api/rewards/mystery-box"] });
    },
    onError: (error: any) => {
      setIsOpening(false);
      toast({
        title: "Error",
        description: error.message || "Failed to open mystery box",
        variant: "destructive",
      });
    },
  });

  const handleOpenBox = () => {
    setIsOpening(true);
    setTimeout(() => {
      openBoxMutation.mutate();
    }, 1500); // Animation delay
  };

  const unclaimed = milestonesData?.unclaimed_milestones || [];

  return (
    <div className="space-y-6" data-testid="surprise-rewards">
      <Tabs defaultValue="mystery-box" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="mystery-box">Mystery Box</TabsTrigger>
          <TabsTrigger value="lucky-draw">Lucky Draw</TabsTrigger>
          <TabsTrigger value="milestones">Milestones</TabsTrigger>
          <TabsTrigger value="birthday">Birthday</TabsTrigger>
        </TabsList>

        {/* Mystery Box Tab */}
        <TabsContent value="mystery-box">
          <Card className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gift className="h-6 w-6" />
                Daily Mystery Box
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center">
                {mysteryBoxData?.can_open ? (
                  <>
                    <div className={`relative inline-block ${isOpening ? "animate-bounce" : ""}`}>
                      <Gift className="h-32 w-32 text-primary mx-auto" />
                      {isOpening && (
                        <Sparkles className="h-16 w-16 text-amber-500 absolute top-0 right-0 animate-spin" />
                      )}
                    </div>
                    
                    <h3 className="text-2xl font-bold mt-4 mb-2">Ready to Open!</h3>
                    <p className="text-muted-foreground mb-6">
                      Open your daily mystery box and get random rewards!
                    </p>
                    
                    <Button 
                      size="lg" 
                      onClick={handleOpenBox}
                      disabled={openBoxMutation.isPending || isOpening}
                      data-testid="open-mystery-box"
                    >
                      {isOpening ? "Opening..." : "Open Mystery Box 🎁"}
                    </Button>
                  </>
                ) : (
                  <>
                    <Gift className="h-32 w-32 text-muted-foreground mx-auto opacity-50" />
                    <h3 className="text-2xl font-bold mt-4 mb-2">Come Back Tomorrow!</h3>
                    <p className="text-muted-foreground">
                      Next box available at: {new Date(mysteryBoxData?.next_available_at).toLocaleString()}
                    </p>
                  </>
                )}
              </div>

              <div className="grid grid-cols-3 gap-4 text-center pt-6 border-t">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Total Opened</p>
                  <p className="text-2xl font-bold">{mysteryBoxData?.total_opened || 0}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Reward Tiers</p>
                  <p className="text-sm font-semibold">Common • Rare • Legendary</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Cost</p>
                  <p className="text-2xl font-bold text-green-500">FREE</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Lucky Draw Tab */}
        <TabsContent value="lucky-draw">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Ticket className="h-6 w-6" />
                Weekly Lucky Draw
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="p-6 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950 dark:to-orange-950 rounded-lg">
                <h3 className="font-bold text-lg mb-4">🏆 Prizes This Week:</h3>
                {luckyDrawData?.prizes?.map((prize: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-3 mb-2">
                    <Badge variant="outline">#{prize.rank}</Badge>
                    <span>{prize.prize}</span>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-3xl font-bold text-primary">{luckyDrawData?.user_tickets || 0}</p>
                  <p className="text-xs text-muted-foreground">Your Tickets</p>
                </div>
                <div>
                  <p className="text-3xl font-bold">{luckyDrawData?.user_entries || 0}</p>
                  <p className="text-xs text-muted-foreground">Entries</p>
                </div>
                <div>
                  <p className="text-3xl font-bold">{luckyDrawData?.total_entries || 0}</p>
                  <p className="text-xs text-muted-foreground">Total Entries</p>
                </div>
              </div>

              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-4">
                  Draw Date: {new Date(luckyDrawData?.draw_date || "").toLocaleDateString()}
                </p>
                <Button disabled={!luckyDrawData?.user_tickets}>
                  Enter Draw
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Milestones Tab */}
        <TabsContent value="milestones">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-6 w-6" />
                Milestone Rewards
              </CardTitle>
            </CardHeader>
            <CardContent>
              {unclaimed.length === 0 ? (
                <div className="text-center py-12">
                  <Trophy className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground">No unclaimed milestones</p>
                  <p className="text-sm text-muted-foreground mt-2">Keep contributing to unlock rewards!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {unclaimed.map((milestone: any, idx: number) => (
                    <div 
                      key={idx} 
                      className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950 rounded-lg border border-green-200"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold">{milestone.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            {milestone.threshold} {milestone.type}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-green-600">+{milestone.reward_points}</p>
                          <Button size="sm" className="mt-2">Claim</Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Birthday Tab */}
        <TabsContent value="birthday">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cake className="h-6 w-6" />
                Birthday Special
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center py-12">
              {birthdayData?.is_birthday ? (
                <>
                  <Cake className="h-24 w-24 mx-auto mb-4 text-pink-500" />
                  <h3 className="text-3xl font-bold mb-2">🎉 Happy Birthday!</h3>
                  {birthdayData?.available ? (
                    <>
                      <p className="text-muted-foreground mb-6">
                        Claim your special birthday rewards!
                      </p>
                      <div className="mb-6 p-4 bg-pink-50 dark:bg-pink-950 rounded-lg inline-block">
                        <p className="font-semibold">🎁 Birthday Gift:</p>
                        <p>{birthdayData.rewards.points} Points</p>
                        <p>{birthdayData.rewards.premium_days} Days Premium</p>
                        <p>{birthdayData.rewards.special_badge}</p>
                      </div>
                      <Button size="lg">Claim Birthday Gift 🎂</Button>
                    </>
                  ) : (
                    <p className="text-muted-foreground">Birthday gift already claimed this year! 🎉</p>
                  )}
                </>
              ) : (
                <>
                  <Cake className="h-24 w-24 mx-auto mb-4 text-muted-foreground opacity-50" />
                  <p className="text-muted-foreground">Birthday rewards unlock on your special day!</p>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
