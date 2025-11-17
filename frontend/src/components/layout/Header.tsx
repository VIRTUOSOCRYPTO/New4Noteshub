import { Link, useLocation } from "wouter";
import { School, Search, Upload, Home as HomeIcon, User, Settings, LogOut, ShieldAlert, BarChart3, Building2, TrendingUp, Flame, Star, Users, Menu, X, Gift, Sparkles, Brain } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/use-auth";
import { useEffect, useState } from "react";
import { NotificationBell } from "@/components/notifications/NotificationBell";
import { apiRequest } from "@/lib/api";
import { useIsMobile } from "@/hooks/use-mobile";

export default function Header() {
  const [location, navigate] = useLocation();
  const { user, logoutMutation } = useAuth();
  const [initials, setInitials] = useState("");
  const [points, setPoints] = useState(0);
  const [level, setLevel] = useState(1);
  const [streak, setStreak] = useState(0);
  const [isAdmin, setIsAdmin] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const isMobile = useIsMobile();

  useEffect(() => {
    if (user?.usn) {
      setInitials(user.usn.substring(0, 2).toUpperCase());
      fetchUserStats();
      fetchAdminStatus();
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

  const fetchAdminStatus = async () => {
    try {
      const data = await apiRequest("/api/user/is-admin");
      setIsAdmin(data.is_admin || false);
    } catch (error) {
      console.error("Failed to fetch admin status:", error);
      setIsAdmin(false);
    }
  };

  const handleLogout = async () => {
    await logoutMutation.mutateAsync();
    navigate("/");
    setMobileMenuOpen(false);
  };

  const navLinks = [
    { href: "/", icon: HomeIcon, label: "Home" },
    { href: "/find", icon: Search, label: "Find Notes" },
    { href: "/upload", icon: Upload, label: "Upload" },
    { href: "/leaderboard", icon: TrendingUp, label: "Leaderboard", badge: streak > 0 ? streak : null },
    { href: "/community", icon: Users, label: "Community" },
    { href: "/rewards", icon: Gift, label: "Rewards" },
  ];

  if (isAdmin) {
    navLinks.push({ href: "/flagged", icon: ShieldAlert, label: "Moderation", badge: null });
    navLinks.push({ href: "/admin", icon: Brain, label: "Admin Panel", badge: null });
  }

  const handleNavClick = () => {
    setMobileMenuOpen(false);
  };

  return (
    <header className="bg-slate-900 text-white shadow-lg border-b border-slate-800">
      <div className="container mx-auto px-4 py-3">
        {/* Top Bar - Logo and Actions */}
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Building2 className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
            </div>
            <Link href="/">
              <h1 className="text-xl sm:text-2xl font-bold cursor-pointer tracking-tight text-white hover:text-blue-400 transition-colors">NotesHub</h1>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link key={link.href} href={link.href}>
                <div className={`flex items-center space-x-1 px-3 py-2 rounded transition ${
                  location === link.href ? 'bg-slate-800 text-white' : 'hover:bg-slate-800 text-slate-300 hover:text-white'
                }`}>
                  <link.icon className="h-4 w-4" />
                  <span>{link.label}</span>
                  {link.badge && (
                    <Badge variant="secondary" className="ml-1 bg-orange-500 text-white text-xs px-1.5 py-0 h-4 flex items-center">
                      <Flame className="h-2.5 w-2.5 mr-0.5" />
                      {link.badge}
                    </Badge>
                  )}
                </div>
              </Link>
            ))}
          </nav>
          
          {/* Right Side - User Actions */}
          <div className="flex items-center space-x-2">
            {user ? (
              <>
                <NotificationBell />
                
                {/* Points Display - Hidden on mobile */}
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
                
                {/* User Avatar Dropdown */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-9 w-9 sm:h-10 sm:w-10 rounded-full hover:bg-slate-800">
                      <Avatar className="h-8 w-8 sm:h-9 sm:w-9 bg-slate-700 border-2 border-slate-600">
                        <AvatarImage 
                          src={user.profile_picture ? `/api/user/profile-picture/${user.profile_picture}` : undefined} 
                          alt={user.usn} 
                        />
                        <AvatarFallback className="bg-slate-700 text-white text-xs sm:text-sm">{initials}</AvatarFallback>
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
                    <DropdownMenuItem onClick={() => navigate("/analytics")}>
                      <BarChart3 className="mr-2 h-4 w-4" />
                      <span>Analytics</span>
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

                {/* Mobile Menu Toggle */}
                <Button
                  variant="ghost"
                  className="lg:hidden h-9 w-9 p-0 hover:bg-slate-800"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  aria-label="Toggle menu"
                >
                  {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </Button>
              </>
            ) : (
              <>
                <Button 
                  variant="default" 
                  onClick={() => navigate("/auth")} 
                  className="bg-blue-600 hover:bg-blue-700 text-white text-sm sm:text-base px-3 sm:px-4 h-9 sm:h-10"
                >
                  Login
                </Button>
                
                {/* Mobile Menu Toggle for non-authenticated users */}
                <Button
                  variant="ghost"
                  className="lg:hidden h-9 w-9 p-0 hover:bg-slate-800"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  aria-label="Toggle menu"
                >
                  {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <nav className="lg:hidden mt-4 pb-2 border-t border-slate-800 pt-4">
            <div className="flex flex-col space-y-1">
              {navLinks.map((link) => (
                <Link key={link.href} href={link.href}>
                  <div 
                    onClick={handleNavClick}
                    className={`flex items-center justify-between px-4 py-3 rounded-lg transition ${
                      location === link.href 
                        ? 'bg-slate-800 text-white' 
                        : 'hover:bg-slate-800 text-slate-300 hover:text-white'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <link.icon className="h-5 w-5" />
                      <span className="text-base font-medium">{link.label}</span>
                    </div>
                    {link.badge && (
                      <Badge variant="secondary" className="bg-orange-500 text-white text-xs px-2 py-1">
                        <Flame className="h-3 w-3 mr-1" />
                        {link.badge}
                      </Badge>
                    )}
                  </div>
                </Link>
              ))}
              
              {/* Mobile Points Display */}
              {user && points > 0 && (
                <div className="flex items-center justify-between px-4 py-3 bg-slate-800 rounded-lg mt-2">
                  <span className="text-sm text-slate-300">Your Progress</span>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs px-2 py-1">
                      Lvl {level}
                    </Badge>
                    <div className="flex items-center gap-1 text-sm text-slate-300">
                      <Star className="h-4 w-4 text-yellow-500" />
                      <span className="font-medium">{points.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
