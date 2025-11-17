import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, Clock, TrendingUp, Users, Zap, Star } from "lucide-react";
import { useState, useEffect } from "react";

interface FOMOTrigger {
  type: string;
  title: string;
  message: string;
  urgency_level: string;
  expires_at?: string;
  action_url?: string;
  action_text?: string;
  data?: any;
}

export function FOMOTriggers() {
  // Sound notification function
  const playNotificationSound = () => {
    try {
      const audio = new Audio('/notification.mp3');
      audio.volume = 0.3;
      audio.play().catch(() => {}); // Ignore errors if user hasn't interacted
    } catch (error) {
      // Silently fail if sound doesn't exist
    }
  };

  // Fetch FOMO triggers
  const { data: triggersData } = useQuery({
    queryKey: ["/api/fomo/triggers"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/fomo/triggers");
      return await res.json();
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Play sound for high urgency triggers
  useEffect(() => {
    if (triggersData?.triggers?.length > 0) {
      const hasHighUrgency = triggersData.triggers.some((t: FOMOTrigger) => t.urgency_level === 'high');
      if (hasHighUrgency) {
        playNotificationSound();
      }
    }
  }, [triggersData]);

  // Fetch live stats
  const { data: liveStats } = useQuery({
    queryKey: ["/api/fomo/live-stats"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/fomo/live-stats");
      return await res.json();
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  const triggers: FOMOTrigger[] = triggersData?.triggers || [];

  const getUrgencyColor = (level: string) => {
    switch (level) {
      case "high":
        return "border-red-500 bg-red-50 dark:bg-red-950";
      case "medium":
        return "border-orange-500 bg-orange-50 dark:bg-orange-950";
      default:
        return "border-blue-500 bg-blue-50 dark:bg-blue-950";
    }
  };

  const getUrgencyIcon = (level: string) => {
    switch (level) {
      case "high":
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case "medium":
        return <Clock className="h-5 w-5 text-orange-500" />;
      default:
        return <TrendingUp className="h-5 w-5 text-blue-500" />;
    }
  };

  return (
    <div className="space-y-6" data-testid="fomo-triggers">
      {/* Live Stats Bar */}
      <Card className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950">
        <CardContent className="py-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="flex items-center justify-center gap-1 mb-1">
                <Users className="h-4 w-4 text-purple-500" />
                <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {liveStats?.active_users_now || 0}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">Online Now</p>
            </div>
            
            <div>
              <div className="flex items-center justify-center gap-1 mb-1">
                <TrendingUp className="h-4 w-4 text-blue-500" />
                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {liveStats?.notes_uploaded_today || 0}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">Notes Today</p>
            </div>
            
            <div>
              <div className="flex items-center justify-center gap-1 mb-1">
                <Zap className="h-4 w-4 text-amber-500" />
                <span className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                  {liveStats?.downloads_last_hour || 0}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">Downloads (1h)</p>
            </div>
            
            <div>
              <div className="flex items-center justify-center gap-1 mb-1">
                <Star className="h-4 w-4 text-green-500" />
                <span className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {liveStats?.active_study_sessions || 0}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">Study Sessions</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* FOMO Triggers */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">🔥 Don't Miss Out!</h3>
        
        {triggers.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-muted-foreground">No urgent alerts at the moment</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {triggers.map((trigger, index) => {
              const isHighPriority = trigger.urgency_level === 'high';
              
              return (
                <Card 
                  key={index} 
                  className={`border-2 ${getUrgencyColor(trigger.urgency_level)} ${
                    isHighPriority ? 'animate-bounce shadow-2xl' : ''
                  } relative`}
                  data-testid={`fomo-trigger-${trigger.type}`}
                >
                  {isHighPriority && (
                    <div className="absolute -top-2 -right-2">
                      <Badge className="bg-red-600 text-white animate-pulse">
                        URGENT
                      </Badge>
                    </div>
                  )}
                  
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      {getUrgencyIcon(trigger.urgency_level)}
                      
                      <div className="flex-1">
                        <h4 className="font-semibold mb-1">{trigger.title}</h4>
                        <p className="text-sm text-muted-foreground mb-3">
                          {trigger.message}
                        </p>
                        
                        {trigger.expires_at && (
                          <p className="text-xs text-red-600 dark:text-red-400 mb-2">
                            ⏰ Expires: {new Date(trigger.expires_at).toLocaleString()}
                          </p>
                        )}
                        
                        {trigger.action_url && (
                          <Button 
                            size="sm" 
                            variant={trigger.urgency_level === "high" ? "default" : "outline"}
                            onClick={() => window.location.href = trigger.action_url!}
                            data-testid={`fomo-action-${trigger.type}`}
                          >
                            {trigger.action_text || "Take Action"}
                          </Button>
                        )}
                        
                        {/* High priority additional info */}
                        {isHighPriority && (
                          <div className="mt-4 p-3 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200">
                            <p className="text-xs font-semibold text-red-600 dark:text-red-400 mb-2">
                              ⚠️ This offer expires soon! Act now to avoid missing out.
                            </p>
                            <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                              <Users className="h-3 w-3" />
                              <span>{trigger.data?.participants_count || 0} students already participating</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
