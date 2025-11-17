import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ShareButtons, WhatsAppShareButtons, InstagramStoryGenerator } from "@/components/viral";
import { TrendingUp, Share2, Instagram, MessageCircle, Users, Gift, Target, Trophy, Brain, Sparkles } from "lucide-react";
import { Link } from "wouter";

export default function ViralHub() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl" data-testid="viral-hub">
      {/* Hero Section */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
          <TrendingUp className="h-10 w-10 text-primary" />
          Viral Growth Hub
        </h1>
        <p className="text-muted-foreground text-lg">
          Share your achievements, invite friends, and grow the community!
        </p>
      </div>

      {/* Quick Navigation to All Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <Link href="/leaderboard">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-blue-500">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-6 w-6 text-yellow-500" />
                Leaderboards & Rankings
              </CardTitle>
              <CardDescription>
                View your rank, compete with peers, track streaks and achievements
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/community">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-purple-500">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-6 w-6 text-purple-500" />
                Community & Social
              </CardTitle>
              <CardDescription>
                Join study groups, follow friends, and engage with the community
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/rewards">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-green-500">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gift className="h-6 w-6 text-green-500" />
                Rewards & Challenges
              </CardTitle>
              <CardDescription>
                Complete challenges, win contests, claim mystery rewards
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/analytics">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-indigo-500">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-6 w-6 text-indigo-500" />
                Analytics Dashboard
              </CardTitle>
              <CardDescription>
                View detailed analytics, trends, and performance metrics
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/instagram-stories">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-pink-500">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Instagram className="h-6 w-6 text-pink-500" />
                Instagram Stories
              </CardTitle>
              <CardDescription>
                Create beautiful stories to share your achievements
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/community?tab=ai">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-purple-500 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-6 w-6 text-purple-600" />
                AI Recommendations
              </CardTitle>
              <CardDescription>
                Get personalized note recommendations powered by AI
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>
      </div>

      {/* Sharing Tools Section */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Share2 className="h-6 w-6 text-blue-500" />
              Share & Grow
            </CardTitle>
            <CardDescription>
              Share notes and achievements to help others and earn rewards
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* WhatsApp Sharing */}
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <MessageCircle className="h-5 w-5 text-green-500" />
                WhatsApp Sharing
              </h3>
              <WhatsAppShareButtons />
            </div>

            {/* General Share Buttons */}
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-500" />
                Social Media Sharing
              </h3>
              <ShareButtons />
            </div>
          </CardContent>
        </Card>

        {/* Instagram Story Preview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Instagram className="h-6 w-6 text-pink-500" />
              Create Instagram Story
            </CardTitle>
            <CardDescription>
              Generate beautiful stories to showcase your achievements
            </CardDescription>
          </CardHeader>
          <CardContent>
            <InstagramStoryGenerator />
          </CardContent>
        </Card>

        {/* Growth Tips */}
        <Card className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950 dark:to-purple-950 border-indigo-200">
          <CardHeader>
            <CardTitle>💡 Viral Growth Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Share on social media:</strong> Post your achievements on Instagram, WhatsApp</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Invite friends:</strong> Refer classmates to earn 50 points per referral</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Join study groups:</strong> Collaborate and grow together</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Upload quality notes:</strong> Help others and build your reputation</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span><strong>Maintain streaks:</strong> Daily activity keeps you at the top</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
