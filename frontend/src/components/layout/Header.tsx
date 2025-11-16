import { Link, useLocation } from "wouter";
import { School, Search, Upload, Home as HomeIcon, User, Settings, LogOut, ShieldAlert, BarChart3, Building2, TrendingUp, Flame, Star, Users } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/use-auth";
import { useEffect, useState } from "react";
import { NotificationBell } from "@/components/notifications/NotificationBell";
import { apiRequest } from "@/lib/api";

export default function Header() {
  const [location, navigate] = useLocation();
  const { user, logoutMutation } = useAuth();
  const [initials, setInitials] = useState("");
  const [points, setPoints] = useState(0);
  const [level, setLevel] = useState(1);
  const [streak, setStreak] = useState(0);

  useEffect(() => {
    if (user?.usn) {
      setInitials(user.usn.substring(0, 2).toUpperCase());
      fetchUserStats();
    }
  }, [user]);

  const fetchUserStats = async () => {
    try {
      const [pointsData, streakData] = await Promise.all([
        apiRequest("/api/gamification/points").catch(() => ({ total_points: 0, level: 1 })),
        apiRequest("/api/gamification/streak").catch(() => ({ current_streak: 0 }))
      ]);
      setPoints(pointsData.total_points || 0);
      setLevel(pointsData.level || 1);
      setStreak(streakData.current_streak || 0);
    } catch (error) {
      console.error("Failed to fetch user stats:", error);
    }
  };

  const handleLogout = async () => {
    await logoutMutation.mutateAsync();
    navigate("/");
  };
  
  const isAdmin = user && ['CSE', 'ISE', 'AIML', 'ECE'].includes(user.department);

  return (
    <header className="bg-slate-900 text-white shadow-lg border-b border-slate-800">
      <div className="container mx-auto px-4 py-3 flex flex-col md:flex-row md:justify-between md:items-center">
        <div className="flex items-center space-x-3 mb-3 md:mb-0">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <Building2 className="h-6 w-6 text-white" />
          </div>
          <Link href="/">
            <h1 className="text-2xl font-bold cursor-pointer tracking-tight text-white hover:text-blue-400 transition-colors">NotesHub</h1>
          </Link>
        </div>
        <div className="flex justify-between items-center">
          <nav className="mr-4">
            <div className="flex flex-wrap space-x-2 md:space-x-4">
              <Link href="/">
                <div className={`flex items-center space-x-1 px-3 py-2 rounded transition ${location === '/' ? 'bg-slate-800 text-white' : 'hover:bg-slate-800 text-slate-300 hover:text-white'}`}>
                  <HomeIcon className="h-4 w-4" />
                  <span className="hidden sm:inline">Home</span>
                </div>
              </Link>
              <Link href="/find">
                <div className={`flex items-center space-x-1 px-3 py-2 rounded transition ${location === '/find' ? 'bg-slate-800 text-white' : 'hover:bg-slate-800 text-slate-300 hover:text-white'}`}>
                  <Search className="h-4 w-4" />
                  <span className="hidden sm:inline">Find Notes</span>
                </div>
              </Link>
              <Link href="/upload">
                <div className={`flex items-center space-x-1 px-3 py-2 rounded transition ${location === '/upload' ? 'bg-slate-800 text-white' : 'hover:bg-slate-800 text-slate-300 hover:text-white'}`}>
                  <Upload className="h-4 w-4" />
                  <span className="hidden sm:inline">Upload</span>
                </div>
              </Link>
              <Link href="/analytics">
                <div className={`flex items-center space-x-1 px-3 py-2 rounded transition ${location === '/analytics' ? 'bg-slate-800 text-white' : 'hover:bg-slate-800 text-slate-300 hover:text-white'}`}>
                  <BarChart3 className="h-4 w-4" />
                  <span className="hidden sm:inline">Analytics</span>
                </div>
              </Link>
              <Link href="/leaderboard">
                <div className={`flex items-center space-x-1 px-3 py-2 rounded transition ${location === '/leaderboard' ? 'bg-slate-800 text-white' : 'hover:bg-slate-800 text-slate-300 hover:text-white'}`}>
                  <TrendingUp className="h-4 w-4" />
                  <span className="hidden sm:inline">Leaderboard</span>
                  {streak > 0 && (
                    <Badge variant="secondary" className="ml-1 bg-orange-500 text-white text-xs px-1.5 py-0 h-4 flex items-center">
                      <Flame className="h-2.5 w-2.5 mr-0.5" />
                      {streak}
                    </Badge>
                  )}
                </div>
              </Link>
              {isAdmin && (
                <Link href="/flagged">
                  <div className={`flex items-center space-x-1 px-3 py-2 rounded transition ${location === '/flagged' ? 'bg-slate-800 text-white' : 'hover:bg-slate-800 text-slate-300 hover:text-white'}`}>
                    <ShieldAlert className="h-4 w-4" />
                    <span className="hidden sm:inline">Moderation</span>
                  </div>
                </Link>
              )}
            </div>
          </nav>
          
          {user ? (
            <div className="flex items-center space-x-2">
              <NotificationBell />
              
              {/* Points Display */}
              {points > 0 && (
                <div className="hidden md:flex items-center gap-1.5 px-2 py-1 bg-slate-800 rounded-lg border border-slate-700">
                  <Badge variant="secondary" className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs px-2 py-0 h-5">
                    Lvl {level}
                  </Badge>
                  <div className="flex items-center gap-0.5 text-xs text-slate-300">
                    <Star className="h-3 w-3 text-yellow-500" />
                    <span className="font-medium">{points.toLocaleString()}</span>
                  </div>
                </div>
              )}
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full hover:bg-slate-800">
                    <Avatar className="h-9 w-9 bg-slate-700 border-2 border-slate-600">
                      <AvatarImage 
                        src={user.profile_picture ? `/api/user/profile-picture/${user.profile_picture}` : undefined} 
                        alt={user.usn} 
                      />
                      <AvatarFallback className="bg-slate-700 text-white">{initials}</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <div className="flex items-center justify-start gap-2 p-2">
                    <div className="flex flex-col space-y-0.5">
                      <p className="text-sm font-medium">{user.usn}</p>
                      <p className="text-xs text-muted-foreground">{user.department}</p>
                    </div>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate("/profile")}>
                    <User className="mr-2 h-4 w-4" />
                    <span>Profile</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/settings")}>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <Button 
              variant="default" 
              onClick={() => navigate("/auth")} 
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Login
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
