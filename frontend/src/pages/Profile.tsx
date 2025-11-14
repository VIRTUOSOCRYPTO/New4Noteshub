import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, School, Building, GraduationCap, Award, User } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { UserAchievements } from "@/components/badges/UserAchievements";
import { usePageVisits } from "@/hooks/use-page-visits";

export default function Profile() {
  usePageVisits('profile');
  
  const { user, isLoading } = useAuth();
  const [initials, setInitials] = useState("US");

  useEffect(() => {
    if (user?.usn) {
      setInitials(user.usn.substring(0, 2).toUpperCase());
    }
  }, [user]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-slate-900" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8 bg-slate-50 min-h-screen">
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-slate-700">You need to be logged in to view your profile.</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 bg-slate-900 rounded-lg flex items-center justify-center">
              <User className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">User Profile</h1>
              <p className="text-slate-600 text-lg mt-1">Your account information and achievements</p>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="text-center pb-2">
                <div className="flex justify-center mb-4">
                  <Avatar className="h-24 w-24 bg-slate-900 border-4 border-slate-100">
                    <AvatarFallback className="text-2xl text-white font-bold">{initials}</AvatarFallback>
                  </Avatar>
                </div>
                <CardTitle className="text-xl text-slate-900">{user.usn}</CardTitle>
                <CardDescription className="text-slate-600">Student Account</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 pt-2">
                  <div className="flex items-center text-slate-700">
                    <School className="h-5 w-5 mr-3 text-slate-500" />
                    <span>{user.department}</span>
                  </div>
                  <div className="flex items-center text-slate-700">
                    <Building className="h-5 w-5 mr-3 text-slate-500" />
                    <span>{user.college}</span>
                  </div>
                  <div className="flex items-center text-slate-700">
                    <GraduationCap className="h-5 w-5 mr-3 text-slate-500" />
                    <span>Joined {new Date(user.createdAt).toLocaleDateString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="md:col-span-2">
            <Card className="mb-6 border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-slate-900">Account Information</CardTitle>
                <CardDescription className="text-slate-600">Your account details and activity</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-slate-500 mb-1">University Seat Number</h3>
                    <p className="text-slate-900 font-medium">{user.usn}</p>
                  </div>
                  <Separator className="bg-slate-200" />
                  <div>
                    <h3 className="text-sm font-medium text-slate-500 mb-1">Department</h3>
                    <p className="text-slate-900 font-medium">{user.department}</p>
                  </div>
                  <Separator className="bg-slate-200" />
                  <div>
                    <h3 className="text-sm font-medium text-slate-500 mb-1">Institution</h3>
                    <p className="text-slate-900 font-medium">{user.college}</p>
                  </div>
                  <Separator className="bg-slate-200" />
                  <div>
                    <h3 className="text-sm font-medium text-slate-500 mb-1">Member Since</h3>
                    <p className="text-slate-900 font-medium">{new Date(user.createdAt).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>
                  </div>
                  <Separator className="bg-slate-200" />
                  <div>
                    <h3 className="text-sm font-medium text-slate-500 mb-1">Account Status</h3>
                    <Badge className="mt-1 bg-green-100 text-green-800 hover:bg-green-100 border-green-200">Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-900">
                  <Award className="h-5 w-5 text-blue-600" />
                  Achievements & Contributions
                </CardTitle>
                <CardDescription className="text-slate-600">Track your progress and milestones</CardDescription>
              </CardHeader>
              <CardContent>
                {user && <UserAchievements user={user} />}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
