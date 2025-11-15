import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Calendar, Clock, AlertTriangle, BookOpen, TrendingUp } from "lucide-react";

interface Exam {
  id: string;
  subject: string;
  department: string;
  year: number;
  exam_date: string;
  exam_type: string;
  days_until: number;
}

export function ExamCountdown() {
  // Fetch exam countdown data
  const { data: countdownData, isLoading } = useQuery({
    queryKey: ["/api/exams/countdown"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/exams/countdown");
      return await res.json();
    },
    refetchInterval: 60000, // Refresh every minute
  });

  // Fetch panic mode data
  const { data: panicData } = useQuery({
    queryKey: ["/api/exams/panic-mode"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/exams/panic-mode");
      return await res.json();
    },
  });

  // Fetch exam stats
  const { data: statsData } = useQuery({
    queryKey: ["/api/exams/stats"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/exams/stats");
      return await res.json();
    },
  });

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading exam data...</div>;
  }

  const nextExam = countdownData?.next_exam;
  const upcomingExams: Exam[] = countdownData?.upcoming_exams || [];
  const stats = statsData || {};
  const isPanicMode = panicData?.panic_mode || false;
  const urgentExams = panicData?.urgent_exams || [];

  const getUrgencyColor = (daysUntil: number) => {
    if (daysUntil <= 3) return "bg-red-500";
    if (daysUntil <= 7) return "bg-orange-500";
    if (daysUntil <= 14) return "bg-yellow-500";
    return "bg-green-500";
  };

  const getUrgencyText = (daysUntil: number) => {
    if (daysUntil === 0) return "TODAY!";
    if (daysUntil === 1) return "TOMORROW!";
    if (daysUntil <= 3) return "URGENT";
    if (daysUntil <= 7) return "Soon";
    return "Upcoming";
  };

  return (
    <div className="space-y-6" data-testid="exam-countdown">
      {/* Panic Mode Alert */}
      {isPanicMode && urgentExams.length > 0 && (
        <Card className="border-red-500 border-2 bg-red-50 dark:bg-red-950">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700 dark:text-red-300">
              <AlertTriangle className="h-6 w-6 animate-pulse" />
              EXAM PANIC MODE ACTIVATED!
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-red-600 dark:text-red-400 font-semibold">
              {panicData.message}
            </p>
            
            {urgentExams.map((urgentExam: any) => (
              <div key={urgentExam.exam.id} className="bg-white dark:bg-gray-900 p-4 rounded-lg space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-bold text-lg">{urgentExam.exam.subject}</h4>
                    <Badge variant="destructive" className="mt-1">
                      {urgentExam.hours_until} hours left
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-red-600">
                      {urgentExam.days_until}
                    </p>
                    <p className="text-xs text-muted-foreground">days</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Users className="h-4 w-4" />
                  <span>{urgentExam.students_studying_now} students studying right now!</span>
                </div>

                <Button className="w-full" variant="destructive" asChild>
                  <a href={`/find-notes?subject=${urgentExam.exam.subject}`}>
                    <BookOpen className="h-4 w-4 mr-2" />
                    Get Notes Now!
                  </a>
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Next Exam Countdown */}
      {nextExam && (
        <Card className="relative overflow-hidden">
          <div className={`absolute top-0 left-0 right-0 h-2 ${getUrgencyColor(nextExam.days_until)}`} />
          
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Next Exam Countdown
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center py-6">
              <h3 className="text-3xl font-bold mb-2">{nextExam.subject}</h3>
              <Badge className={getUrgencyColor(nextExam.days_until)}>
                {getUrgencyText(nextExam.days_until)}
              </Badge>
              
              <div className="mt-6">
                <div className="text-6xl font-bold text-primary mb-2">
                  {nextExam.days_until}
                </div>
                <p className="text-muted-foreground text-lg">
                  days until exam
                </p>
              </div>

              <div className="mt-4 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4 inline mr-1" />
                {new Date(nextExam.exam_date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </div>
            </div>

            {nextExam.days_until <= 7 && (
              <Button className="w-full" size="lg" asChild>
                <a href={`/find-notes?subject=${nextExam.subject}`}>
                  <BookOpen className="h-4 w-4 mr-2" />
                  Study for {nextExam.subject}
                </a>
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Exam Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Exam Preparation Stats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary">
                {stats.total_upcoming_exams || 0}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Total Exams</p>
            </div>
            
            <div className="text-center">
              <p className="text-3xl font-bold text-orange-500">
                {stats.urgent_exams || 0}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Urgent (7 days)</p>
            </div>
            
            <div className="text-center">
              <p className="text-3xl font-bold text-green-500">
                {stats.notes_downloaded_for_exams || 0}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Notes Downloaded</p>
            </div>
            
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-500">
                {stats.days_until_next_exam !== null ? stats.days_until_next_exam : '--'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Days to Next</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Upcoming Exams List */}
      {upcomingExams.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Upcoming Exams ({upcomingExams.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {upcomingExams.map((exam) => (
                <div 
                  key={exam.id} 
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                  data-testid={`exam-${exam.id}`}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold">{exam.subject}</h4>
                      <Badge variant="outline" className="text-xs">
                        {exam.exam_type}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {new Date(exam.exam_date).toLocaleDateString()}
                    </p>
                  </div>

                  <div className="text-right">
                    <div className={`inline-flex items-center gap-1 px-2 py-1 rounded ${getUrgencyColor(exam.days_until)} text-white text-xs font-bold`}>
                      {exam.days_until} days
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Exams State */}
      {!nextExam && upcomingExams.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Calendar className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-xl font-semibold mb-2">No Upcoming Exams</h3>
            <p className="text-muted-foreground">
              You're all caught up! Keep studying and stay ahead! 📚
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Fix: Import Users icon
import { Users } from "lucide-react";
