import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Badge } from "@/components/ui/badge";
import { Users } from "lucide-react";
import { useState, useEffect } from "react";

interface Activity {
  type: string;
  message: string;
  icon: string;
  timestamp: string;
}

export function LiveActivityTicker() {
  const [currentIndex, setCurrentIndex] = useState(0);

  const { data: activitiesData } = useQuery({
    queryKey: ["/api/fomo/live-activity-feed"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/fomo/live-activity-feed");
      return await res.json();
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  const activities: Activity[] = activitiesData?.activities || [];

  useEffect(() => {
    if (activities.length > 0) {
      const interval = setInterval(() => {
        setCurrentIndex((prev) => (prev + 1) % activities.length);
      }, 3000); // Rotate every 3 seconds

      return () => clearInterval(interval);
    }
  }, [activities.length]);

  if (activities.length === 0) return null;

  const currentActivity = activities[currentIndex];

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 animate-slide-up">
      <Badge 
        className="px-6 py-3 text-sm font-medium bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-2xl border-2 border-white/20 backdrop-blur-sm cursor-pointer hover:scale-105 transition-transform"
        onClick={() => window.location.href = '/community'}
      >
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-2xl">{currentActivity.icon}</span>
          <span>{currentActivity.message}</span>
          <Users className="h-4 w-4 ml-2" />
        </div>
      </Badge>
    </div>
  );
}
