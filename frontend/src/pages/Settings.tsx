import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Key, Bell, Eye, EyeOff, Camera, UserCircle, Settings as SettingsIcon, Shield, User } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { useState, useEffect, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { showToast } from "@/components/ui/toast-container";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export default function Settings() {
  const { user, isLoading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [notifyNewNotes, setNotifyNewNotes] = useState(false);
  const [notifyDownloads, setNotifyDownloads] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const updateSettingsMutation = useMutation({
    mutationFn: (settings: { notifyNewNotes?: boolean, notifyDownloads?: boolean }) => {
      return apiRequest('PATCH', '/api/user/settings', settings);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/user'] });
      showToast('Settings updated successfully', 'success');
    },
    onError: (error) => {
      showToast(`Failed to update settings: ${error.message}`, 'error');
    }
  });

  const updatePasswordMutation = useMutation({
    mutationFn: () => {
      if (newPassword !== confirmPassword) {
        throw new Error('New passwords do not match');
      }
      return apiRequest('PATCH', '/api/user/password', {
        currentPassword,
        newPassword,
        confirmNewPassword: confirmPassword,
      });
    },
    onSuccess: () => {
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      showToast('Password updated successfully', 'success');
    },
    onError: (error) => {
      showToast(`Failed to update password: ${error.message}`, 'error');
    }
  });

  function handleSaveNotifications() {
    updateSettingsMutation.mutate({ notifyNewNotes, notifyDownloads });
  }

  function handleUpdatePassword() {
    if (!currentPassword) {
      showToast('Please enter your current password', 'error');
      return;
    }
    if (!newPassword) {
      showToast('Please enter a new password', 'error');
      return;
    }
    if (newPassword !== confirmPassword) {
      showToast('New passwords do not match', 'error');
      return;
    }
    updatePasswordMutation.mutate();
  }

  function handleProfilePictureChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (file.size > 2 * 1024 * 1024) {
      showToast('File size must be less than 2MB', 'error');
      return;
    }
    
    const formData = new FormData();
    formData.append('profilePicture', file);
    setIsUploading(true);
    
    const token = localStorage.getItem('auth_token');
    fetch('/api/user/profile-picture', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    })
      .then(response => {
        if (!response.ok) throw new Error('Failed to upload profile picture');
        return response.json();
      })
      .then(() => {
        queryClient.invalidateQueries({ queryKey: ['/api/user'] });
        showToast('Profile picture updated successfully', 'success');
      })
      .catch(error => {
        showToast(`Error: ${error.message}`, 'error');
      })
      .finally(() => {
        setIsUploading(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
      });
  }
  
  useEffect(() => {
    if (user) {
      setNotifyNewNotes(user.notifyNewNotes ?? true);
      setNotifyDownloads(user.notifyDownloads ?? false);
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
          <h3 className="text-lg font-medium text-slate-700">You need to be logged in to view settings.</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-14 h-14 bg-slate-900 rounded-lg flex items-center justify-center">
              <SettingsIcon className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">Settings</h1>
              <p className="text-slate-600 text-lg mt-1">Manage your account preferences and security</p>
            </div>
          </div>
        </div>

        {/* Settings Tabs */}
        <Tabs defaultValue="account" className="space-y-6">
          <TabsList className="bg-white border border-slate-200 p-1 shadow-sm">
            <TabsTrigger 
              value="account" 
              className="data-[state=active]:bg-slate-900 data-[state=active]:text-white"
            >
              <User className="h-4 w-4 mr-2" />
              Account
            </TabsTrigger>
            <TabsTrigger 
              value="profile" 
              className="data-[state=active]:bg-slate-900 data-[state=active]:text-white"
            >
              <Camera className="h-4 w-4 mr-2" />
              Profile
            </TabsTrigger>
            <TabsTrigger 
              value="security" 
              className="data-[state=active]:bg-slate-900 data-[state=active]:text-white"
            >
              <Shield className="h-4 w-4 mr-2" />
              Security
            </TabsTrigger>
            <TabsTrigger 
              value="notifications" 
              className="data-[state=active]:bg-slate-900 data-[state=active]:text-white"
            >
              <Bell className="h-4 w-4 mr-2" />
              Notifications
            </TabsTrigger>
          </TabsList>
          
          {/* Account Tab */}
          <TabsContent value="account">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-2xl flex items-center text-slate-900">
                  <User className="h-6 w-6 mr-2 text-blue-600" />
                  Account Information
                </CardTitle>
                <CardDescription className="text-slate-600">Your registered account details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="usn" className="text-sm font-medium text-slate-700">University Seat Number</Label>
                    <div className="relative">
                      <Input id="usn" defaultValue={user.usn} disabled className="bg-slate-50 pl-10 border-slate-300" />
                      <UserCircle className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                    </div>
                    <p className="text-xs text-slate-500">Cannot be modified after registration</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="department" className="text-sm font-medium text-slate-700">Department</Label>
                    <div className="relative">
                      <Input id="department" defaultValue={user.department} disabled className="bg-slate-50 pl-10 border-slate-300" />
                      <Shield className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                    </div>
                    <p className="text-xs text-slate-500">Cannot be modified after registration</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="createdAt" className="text-sm font-medium text-slate-700">Member Since</Label>
                    <Input 
                      id="createdAt" 
                      value={new Date(user.createdAt).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })} 
                      disabled 
                      className="bg-slate-50 border-slate-300"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Profile Picture Tab */}
          <TabsContent value="profile">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-2xl flex items-center text-slate-900">
                  <Camera className="h-6 w-6 mr-2 text-blue-600" />
                  Profile Picture
                </CardTitle>
                <CardDescription className="text-slate-600">Update your profile photo</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col items-center space-y-6">
                  <Avatar className="h-32 w-32 border-4 border-slate-200 shadow-lg">
                    <AvatarImage 
                      src={user.profile_picture ? `/api/user/profile-picture/${user.profile_picture}` : undefined} 
                      alt={user.usn} 
                    />
                    <AvatarFallback className="text-3xl bg-slate-900 text-white">
                      {user.usn?.substring(0, 2).toUpperCase() || "UN"}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex flex-col items-center gap-3">
                    <Button 
                      variant="outline" 
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isUploading}
                      className="border-slate-300 hover:bg-slate-50"
                    >
                      {isUploading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Camera className="mr-2 h-4 w-4" />
                          Change Picture
                        </>
                      )}
                    </Button>
                    <input 
                      type="file" 
                      ref={fileInputRef}
                      className="hidden" 
                      accept="image/*"
                      onChange={handleProfilePictureChange}
                    />
                    <p className="text-sm text-slate-500 text-center">
                      JPG, PNG or GIF. Max size 2MB.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Security Tab */}
          <TabsContent value="security">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-2xl flex items-center text-slate-900">
                  <Shield className="h-6 w-6 mr-2 text-blue-600" />
                  Security Settings
                </CardTitle>
                <CardDescription className="text-slate-600">Manage your password and security preferences</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current-password" className="text-slate-700">Current Password</Label>
                    <div className="relative">
                      <Input 
                        id="current-password" 
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your current password" 
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className="pr-10 border-slate-300"
                      />
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="absolute right-0 top-0" 
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="new-password" className="text-slate-700">New Password</Label>
                    <Input 
                      id="new-password" 
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your new password" 
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="border-slate-300"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirm-password" className="text-slate-700">Confirm New Password</Label>
                    <Input 
                      id="confirm-password" 
                      type={showPassword ? "text" : "password"}
                      placeholder="Confirm your new password" 
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="border-slate-300"
                    />
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  onClick={handleUpdatePassword}
                  disabled={updatePasswordMutation.isPending}
                  className="bg-slate-900 hover:bg-slate-800"
                >
                  {updatePasswordMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    <>
                      <Key className="mr-2 h-4 w-4" />
                      Update Password
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
          
          {/* Notifications Tab */}
          <TabsContent value="notifications">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader>
                <CardTitle className="text-2xl flex items-center text-slate-900">
                  <Bell className="h-6 w-6 mr-2 text-blue-600" />
                  Notification Preferences
                </CardTitle>
                <CardDescription className="text-slate-600">Manage how you receive notifications</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="space-y-1 flex-1">
                    <Label htmlFor="notify-new-notes" className="text-base font-medium text-slate-900">New Department Content</Label>
                    <p className="text-sm text-slate-600">
                      Receive notifications when new content is uploaded in your department
                    </p>
                  </div>
                  <Switch
                    id="notify-new-notes"
                    checked={notifyNewNotes}
                    onCheckedChange={setNotifyNewNotes}
                  />
                </div>
                <Separator className="bg-slate-200" />
                <div className="flex items-center justify-between p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="space-y-1 flex-1">
                    <Label htmlFor="notify-downloads" className="text-base font-medium text-slate-900">Download Notifications</Label>
                    <p className="text-sm text-slate-600">
                      Get notified when users download your contributed content
                    </p>
                  </div>
                  <Switch
                    id="notify-downloads"
                    checked={notifyDownloads}
                    onCheckedChange={setNotifyDownloads}
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  onClick={handleSaveNotifications}
                  disabled={updateSettingsMutation.isPending}
                  className="bg-slate-900 hover:bg-slate-800"
                >
                  {updateSettingsMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Bell className="mr-2 h-4 w-4" />
                      Save Preferences
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
