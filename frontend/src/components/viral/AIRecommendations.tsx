import { useState, useEffect } from 'react';
import { Sparkles, BookOpen, TrendingUp, Users, Brain, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiRequest } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface Note {
  id: string;
  title: string;
  subject: string;
  department: string;
  download_count: number;
}

interface StudyInsight {
  insights: string[];
  stats: {
    level: number;
    points: number;
    streak: number;
    uploads: number;
    downloads: number;
    groups: number;
  };
}

interface StudyPlan {
  study_plan: string[];
  duration_days: number;
  upcoming_exams: any[];
  focus_subjects: string[];
}

export function AIRecommendations() {
  const [activeTab, setActiveTab] = useState('notes');
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Note[]>([]);
  const [insights, setInsights] = useState<StudyInsight | null>(null);
  const [studyPlan, setStudyPlan] = useState<StudyPlan | null>(null);
  const [similarStudents, setSimilarStudents] = useState<any[]>([]);
  const { toast } = useToast();

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const data = await apiRequest('/api/ai/recommendations/notes?limit=10');
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
      toast({
        title: 'Error',
        description: 'Failed to load AI recommendations',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const loadInsights = async () => {
    setLoading(true);
    try {
      const data = await apiRequest('/api/ai/insights/study-pattern');
      setInsights(data);
    } catch (error) {
      console.error('Failed to load insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStudyPlan = async () => {
    setLoading(true);
    try {
      const data = await apiRequest('/api/ai/study-plan?days=7');
      setStudyPlan(data);
    } catch (error) {
      console.error('Failed to load study plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSimilarStudents = async () => {
    setLoading(true);
    try {
      const data = await apiRequest('/api/ai/similar-students?limit=10');
      setSimilarStudents(data.similar_students || []);
    } catch (error) {
      console.error('Failed to load similar students:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'notes') loadRecommendations();
    else if (activeTab === 'insights') loadInsights();
    else if (activeTab === 'plan') loadStudyPlan();
    else if (activeTab === 'students') loadSimilarStudents();
  }, [activeTab]);

  return (
    <Card className="border-2 border-purple-200" data-testid="ai-recommendations">
      <CardHeader className="bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 text-white">
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-6 w-6" />
          AI-Powered Insights
        </CardTitle>
        <CardDescription className="text-white/90">
          Personalized recommendations using AI
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="notes" data-testid="tab-notes">
              <BookOpen className="h-4 w-4 mr-2" />
              Notes
            </TabsTrigger>
            <TabsTrigger value="insights" data-testid="tab-insights">
              <Sparkles className="h-4 w-4 mr-2" />
              Insights
            </TabsTrigger>
            <TabsTrigger value="plan" data-testid="tab-plan">
              <Target className="h-4 w-4 mr-2" />
              Plan
            </TabsTrigger>
            <TabsTrigger value="students" data-testid="tab-students">
              <Users className="h-4 w-4 mr-2" />
              Similar
            </TabsTrigger>
          </TabsList>

          <TabsContent value="notes" className="space-y-4 mt-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-purple-500" />
                Recommended for You
              </h3>
              <Button onClick={loadRecommendations} size="sm" variant="outline">
                Refresh
              </Button>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">
                <Brain className="h-8 w-8 mx-auto mb-2 animate-pulse" />
                AI is analyzing your behavior...
              </div>
            ) : recommendations.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No recommendations yet. Download some notes to get started!
              </div>
            ) : (
              <div className="space-y-2">
                {recommendations.map((note) => (
                  <Card key={note.id} className="p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold">{note.title}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="secondary">{note.subject}</Badge>
                          <span className="text-sm text-muted-foreground">
                            {note.download_count} downloads
                          </span>
                        </div>
                      </div>
                      <Button size="sm" data-testid={`view-note-${note.id}`}>
                        View
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="insights" className="space-y-4 mt-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                Your Study Pattern
              </h3>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">
                <Brain className="h-8 w-8 mx-auto mb-2 animate-pulse" />
                Analyzing your study habits...
              </div>
            ) : insights ? (
              <div className="space-y-4">
                <Card className="p-4 bg-gradient-to-r from-purple-50 to-pink-50">
                  <h4 className="font-semibold mb-3">AI Insights</h4>
                  <div className="space-y-2">
                    {insights.insights.map((insight, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <Sparkles className="h-4 w-4 mt-0.5 text-purple-500 flex-shrink-0" />
                        <p className="text-sm">{insight}</p>
                      </div>
                    ))}
                  </div>
                </Card>
                
                <div className="grid grid-cols-3 gap-3">
                  <Card className="p-3 text-center">
                    <div className="text-2xl font-bold text-purple-600">{insights.stats.level}</div>
                    <div className="text-xs text-muted-foreground">Level</div>
                  </Card>
                  <Card className="p-3 text-center">
                    <div className="text-2xl font-bold text-orange-600">{insights.stats.streak}</div>
                    <div className="text-xs text-muted-foreground">Day Streak</div>
                  </Card>
                  <Card className="p-3 text-center">
                    <div className="text-2xl font-bold text-blue-600">{insights.stats.groups}</div>
                    <div className="text-xs text-muted-foreground">Groups</div>
                  </Card>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No insights available yet
              </div>
            )}
          </TabsContent>

          <TabsContent value="plan" className="space-y-4 mt-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold flex items-center gap-2">
                <Target className="h-4 w-4 text-blue-500" />
                7-Day Study Plan
              </h3>
              <Button onClick={loadStudyPlan} size="sm" variant="outline">
                Regenerate
              </Button>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">
                <Brain className="h-8 w-8 mx-auto mb-2 animate-pulse" />
                Creating your personalized plan...
              </div>
            ) : studyPlan ? (
              <div className="space-y-3">
                {studyPlan.study_plan.map((dayPlan, i) => (
                  <Card key={i} className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 font-bold flex-shrink-0">
                        {i + 1}
                      </div>
                      <p className="text-sm flex-1">{dayPlan}</p>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No study plan generated yet
              </div>
            )}
          </TabsContent>

          <TabsContent value="students" className="space-y-4 mt-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold flex items-center gap-2">
                <Users className="h-4 w-4 text-blue-500" />
                Students Like You
              </h3>
            </div>
            
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">
                <Brain className="h-8 w-8 mx-auto mb-2 animate-pulse" />
                Finding similar students...
              </div>
            ) : similarStudents.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No similar students found yet
              </div>
            ) : (
              <div className="space-y-2">
                {similarStudents.map((student) => (
                  <Card key={student.user_id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold">{student.usn || 'Student'}</h4>
                        <p className="text-sm text-muted-foreground">
                          {student.department} • Level {student.level || 1}
                        </p>
                      </div>
                      <Button size="sm" variant="outline">
                        Follow
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
