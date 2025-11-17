import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { InstagramStoryGenerator } from "@/components/viral";
import { Instagram, Sparkles, TrendingUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function InstagramStories() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl" data-testid="instagram-stories-page">
      {/* Hero Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl">
              <Instagram className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold flex items-center gap-3">
                Instagram Story Templates
                <Badge variant="secondary" className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                  <Sparkles className="h-3 w-3 mr-1" />
                  Viral
                </Badge>
              </h1>
              <p className="text-muted-foreground text-lg mt-1">
                Create stunning Instagram stories to share your achievements!
              </p>
            </div>
          </div>
        </div>

        {/* Feature Benefits */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Sparkles className="h-8 w-8 text-purple-500" />
                <div>
                  <h3 className="font-semibold">10+ Templates</h3>
                  <p className="text-sm text-muted-foreground">Choose from beautiful designs</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950 dark:to-cyan-950">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <TrendingUp className="h-8 w-8 text-blue-500" />
                <div>
                  <h3 className="font-semibold">Boost Visibility</h3>
                  <p className="text-sm text-muted-foreground">Get more engagement</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-green-200 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Instagram className="h-8 w-8 text-green-500" />
                <div>
                  <h3 className="font-semibold">Share Instantly</h3>
                  <p className="text-sm text-muted-foreground">One-click sharing to Instagram</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Story Generator Component */}
      <Card>
        <CardHeader>
          <CardTitle>Create Your Story</CardTitle>
          <CardDescription>
            Select a template, customize it with your achievements, and share it on Instagram to inspire others!
          </CardDescription>
        </CardHeader>
        <CardContent>
          <InstagramStoryGenerator />
        </CardContent>
      </Card>

      {/* Tips Section */}
      <Card className="mt-6 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950 dark:to-purple-950 border-indigo-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            Pro Tips for Maximum Engagement
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Post your stories during peak hours (9 AM - 11 AM and 7 PM - 9 PM)</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Use relevant hashtags like #StudyNotes #ExamPrep #NotesHub</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Tag friends who might benefit from the notes</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Share milestone achievements (Level ups, Streaks, Top rankings)</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Add engaging captions and stickers to your stories</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
