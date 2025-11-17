import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  ChallengesHub,
  ContestsGallery,
  FOMOTriggers,
  SurpriseRewards
} from "@/components/viral";
import { Gift, Target, Trophy, Zap, TrendingUp } from "lucide-react";
import { Link } from "wouter";

export default function RewardsHub() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl" data-testid="rewards-hub">
      {/* Hero Section */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
          <Gift className="h-10 w-10 text-primary" />
          Rewards Hub
        </h1>
        <p className="text-muted-foreground text-lg">
          Earn points, unlock achievements, and claim amazing rewards!
        </p>
      </div>

      {/* 4 Tabs for Rewards - Unique Features Only */}
      <Tabs defaultValue="mystery" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 gap-2">
          <TabsTrigger value="mystery" className="flex items-center gap-2" data-testid="tab-mystery">
            <Gift className="h-4 w-4" />
            <span>Mystery Rewards</span>
          </TabsTrigger>
          <TabsTrigger value="challenges" className="flex items-center gap-2" data-testid="tab-challenges">
            <Target className="h-4 w-4" />
            <span>Challenges</span>
          </TabsTrigger>
          <TabsTrigger value="contests" className="flex items-center gap-2" data-testid="tab-contests">
            <Trophy className="h-4 w-4" />
            <span>Contests</span>
          </TabsTrigger>
          <TabsTrigger value="alerts" className="flex items-center gap-2" data-testid="tab-alerts">
            <Zap className="h-4 w-4" />
            <span>Live Alerts</span>
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Mystery Rewards */}
        <TabsContent value="mystery" className="space-y-6">
          <SurpriseRewards />
          
          {/* Quick Links to Other Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/leaderboard?tab=achievements">
              <div className="p-6 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950 dark:to-orange-950 rounded-lg border border-amber-200 cursor-pointer hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">View All</p>
                    <p className="text-xl font-bold flex items-center gap-2">
                      Achievements
                      <TrendingUp className="h-4 w-4 text-amber-500" />
                    </p>
                  </div>
                </div>
              </div>
            </Link>
            
            <Link href="/leaderboard?tab=referrals">
              <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950 rounded-lg border border-purple-200 cursor-pointer hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Invite Friends</p>
                    <p className="text-xl font-bold flex items-center gap-2">
                      Referrals
                      <TrendingUp className="h-4 w-4 text-purple-500" />
                    </p>
                  </div>
                </div>
              </div>
            </Link>
            
            <Link href="/leaderboard?tab=overview">
              <div className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950 dark:to-cyan-950 rounded-lg border border-blue-200 cursor-pointer hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Track Your</p>
                    <p className="text-xl font-bold flex items-center gap-2">
                      Progress
                      <TrendingUp className="h-4 w-4 text-blue-500" />
                    </p>
                  </div>
                </div>
              </div>
            </Link>
          </div>
        </TabsContent>

        {/* Tab 2: Challenges */}
        <TabsContent value="challenges">
          <ChallengesHub />
        </TabsContent>

        {/* Tab 3: Contests */}
        <TabsContent value="contests">
          <ContestsGallery />
        </TabsContent>

        {/* Tab 4: Live Alerts */}
        <TabsContent value="alerts">
          <FOMOTriggers />
        </TabsContent>
      </Tabs>
    </div>
  );
}
